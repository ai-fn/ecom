import csv
import os
import uuid
from celery import shared_task
from django.conf import settings
from django.db import transaction
from loguru import logger
import pandas as pd
import magic
import requests

from PIL import Image
from io import BytesIO

from tempfile import NamedTemporaryFile
from pytils import translit
from django.utils.text import slugify as django_slugify
from api.serializers.product_detail import ProductDetailSerializer

from shop.models import (
    Category,
    Characteristic,
    CharacteristicValue,
    Product,
    ProductImage,
)
from unidecode import unidecode
from django.core.files.uploadedfile import InMemoryUploadedFile


def custom_slugify(value):
    return django_slugify(unidecode(value))


@shared_task
def handle_xlsx_file_task(file_path, upload_type):
    try:
        with open(file_path, "rb") as file_obj:
            # Проверка MIME-типа файла для удостоверения, что это действительно Excel файл
            mime_type = magic.from_buffer(file_obj.read(2048), mime=True)
            file_obj.seek(0)  # Возвращаем указатель в начало файла после чтения

            # Создание временного файла для хранения содержимого .xlsx файла
            with NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
                tmp.write(file_obj.read())
                tmp.flush()
                tmp.seek(0)
                df = pd.read_excel(tmp.name, engine="openpyxl")
                # Вызов функции обработки DataFrame
                result = process_dataframe(df, upload_type)
                return result
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return False


@shared_task
def handle_csv_file_task(file_path, upload_type):
    try:
        with open(file_path, "r", encoding="utf-8") as file_obj:
            df = pd.read_csv(file_obj)
            # Вызов функцию обработки DataFrame
            result = process_dataframe(df, upload_type)
            return result
    except Exception as e:
        # Здесь код для логирования ошибок
        print(f"Error processing CSV file: {e}")
        return False


def process_dataframe(df, upload_type):
    ignored_columns = ["TITLE", "DESCRIPTION", "IMAGES", "CATEGORIES", "SKU"]
    failed_images = []
    try:
        with transaction.atomic():
            # Адаптируйте ниже код обработки DataFrame в соответствии с вашей логикой
            # Пример обработки для PRODUCT
            if upload_type == "PRODUCTS":
                for _, row in df.iterrows():
                    category_path = row["CATEGORIES"].split(" | ")
                    category = None
                    for cat_name in category_path[
                        0:-1
                    ]:  # Правильное исключение последнего элемента
                        if (
                            cat_name
                        ):  # Дополнительная проверка на непустое имя категории
                            cat_slug = translit.slugify(cat_name)
                            if cat_slug:
                                parent_category = category
                                category, created = Category.objects.get_or_create(
                                    name=cat_name,
                                    defaults={
                                        "slug": cat_slug,
                                        "parent": parent_category,
                                    },
                                )
                                # Обновляем parent только если категория была только что создана или если parent отличается
                                if created or (
                                    category.parent != parent_category
                                    and parent_category is not None
                                ):
                                    category.parent = parent_category
                                    category.save()
                            else:
                                logger.error(
                                    f"Unable to create slug for category name '{cat_name}'. Skipping category creation."
                                )
                        else:
                            logger.error(
                                "Empty category name encountered. Skipping category creation."
                            )

                    product_title = row["TITLE"]
                    product_slug = translit.slugify(product_title)
                    # TODO добавить DESCRIPTION потом
                    if product_slug:  # Проверяем, что slug продукта не пустой
                        product, created = Product.objects.get_or_create(
                            title=product_title,
                            defaults={
                                "description": "row['DESCRIPTION']",
                                "category": category,
                                "slug": product_slug,
                            },
                        )

                        product_image_urls = row["IMAGES"].split(",")
                        if len(product_image_urls) > 0:
                            for image_url in product_image_urls:
                                try:
                                    data = requests.get(image_url).content
                                except Exception as err:
                                    print("Error with image url: %s" % err)
                                    continue

                                try:
                                    pil_image = Image.open(BytesIO(data))

                                    # Конвертация PIL фото в байты
                                    img_byte_array = BytesIO()
                                    pil_image.save(img_byte_array, format="WEBP")
                                    img_byte_array.seek(0)
                                    product_image = ProductImage(product=product)

                                    result_filename = f"{uuid.uuid4()}.webp"

                                    product_image.image.save(
                                        result_filename,
                                        InMemoryUploadedFile(
                                            img_byte_array,
                                            None,
                                            result_filename,
                                            "image/webp",
                                            img_byte_array.tell(),
                                            None,
                                        ),
                                    )

                                    print(f"{product_image} successfully saved")

                                    # Стандартизация размеров изображений при импорте
                                    # 16:9 format (the maximum resolution is HD - 1280:720)
                                    image = Image.open(product_image.image.file.name)
                                    width, height = image.size
                                    
                                    width = int(min(width, 1280))
                                    height = int((width * 9) / 16)

                                    image.resize((width, height)).save(product_image.image.file.name)

                                    # Добавление водяного знака на изображение
                                    
                                    try:
                                        path_to_watermark = settings.WATERMARK_PATH
                                        watermark = Image.open(path_to_watermark)
                                        watermark = watermark.resize((100, 100))

                                        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

                                        position = (image.width - watermark.width, image.height - watermark.height)
                                        overlay.paste(watermark, position)

                                        Image.alpha_composite(image.convert('RGBA', overlay)).save(product_image.image.file.name)
                                    except Exception as err:
                                        print("Error while adding watermark to image: %s" % err)
                                        continue
                                    
                                    image.close()
                                    overlay.close()
                                    watermark.close()
                                except Exception as err:
                                    failed_images.append(image_url)
                                    print("Error while save ProductImage: %s" % err)

                        # Обработка характеристик и их значений
                        for column_name in df.columns:
                            if column_name not in ignored_columns:
                                characteristic_value = row[column_name]
                                if pd.notna(
                                    characteristic_value
                                ):  # Проверка наличия значения
                                    # Проверка существования характеристики и создание, если не существует
                                    characteristic, _ = (
                                        Characteristic.objects.get_or_create(
                                            name=column_name,
                                            defaults={"category": category},
                                        )
                                    )
                                    # Создание значения характеристики для продукта
                                    CharacteristicValue.objects.create(
                                        product=product,
                                        characteristic=characteristic,
                                        value=str(characteristic_value),
                                    )
                    else:
                        logger.error(
                            f"Unable to create slug for product title '{product_title}'. Skipping product creation."
                        )
            # Добавьте логику для BRANDS, если необходимо
        return failed_images or []
    except Exception as err:
        # Логирование ошибки
        print(f"Error processing data: {err}")


@shared_task
def export_products_to_csv(email_to):
    # Экспорт данных в CSV
    products = Product.objects.all()
    serializer = ProductDetailSerializer(products, many=True)
    file_path = os.path.join(settings.MEDIA_ROOT, "products.csv")
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Title", "Brand", "Category", "Description"])
        for product in serializer.data:
            writer.writerow(
                [
                    product["id"],
                    product["title"],
                    product.get("brand", ""),
                    product.get("category", ""),
                    product["description"],
                ]
            )

    return file_path
