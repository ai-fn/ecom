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
from django.utils import timezone
from django.utils.text import slugify as django_slugify
from api.serializers.product_detail import ProductDetailSerializer

from shop.models import (
    Category,
    Characteristic,
    CharacteristicValue,
    Product,
    ProductImage,
    Price,
    City,
    Promo,
)
from unidecode import unidecode
from django.core.files.base import ContentFile


def custom_slugify(value):
    return django_slugify(unidecode(value))

@shared_task
def update_promo_status():
    # Get the date one day ago
    one_day_ago = timezone.now().date() + timezone.timedelta(days=1)
    
    # Filter promos that are expired one day ago
    expired_promos = Promo.objects.filter(active_to__lte=one_day_ago)
    
    # Deactivate expired promos
    expired_promos.update(is_active=False)

    
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
    city_names = City.objects.all().values_list("name", flat=True)
    try:
        with transaction.atomic():
            # Адаптируйте ниже код обработки DataFrame в соответствии с вашей логикой
            # Пример обработки для PRODUCT
            if upload_type == "PRODUCTS":

                characteristic_columns = []
                cities_columns = []

                # Проверка, есть ли данные о характеристиках и ценах по городам
                for column_name in df.columns:
                    if column_name in city_names:
                        cities_columns.append(column_name)
                    elif column_name not in ignored_columns:
                        characteristic_columns.append(column_name)

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
                            for idx, image_url in enumerate(product_image_urls):
                                try:
                                    data = requests.get(image_url).content
                                except Exception as err:
                                    print(f"Error with image url: {err}")
                                    continue

                                try:
                                    format = "webp"
                                    filename = f"image-{uuid.uuid4()}"

                                    pil_image = Image.open(BytesIO(data))

                                    # Конвертация PIL фото в байты
                                    product_image = ProductImage(product=product)

                                    # Сохранение первого изображение в нескольких форматах
                                    if idx == 0:

                                        # Сохранение каталожной версии изображения
                                        catalog_format = getattr(
                                            settings,
                                            "PRODUCT_CATALOG_IAMGE_FORMAT",
                                            "webp",
                                        )
                                        catalog_image_size = (
                                            getattr(
                                                settings,
                                                "PRODUCT_CATALOG_IMAGE_WIDTH",
                                                500,
                                            ),
                                            getattr(
                                                settings,
                                                "PRODUCT_CATALOG_IMAGE_HEIGHT",
                                                500,
                                            ),
                                        )

                                        catalog_image = pil_image.copy().resize(
                                            catalog_image_size
                                        )
                                        with BytesIO() as buffer:
                                            catalog_image.save(buffer, format.upper())
                                            catalog_image_data = buffer.getvalue()

                                        product.catalog_image.save(
                                            f"catalog-{filename}.{catalog_format}",
                                            ContentFile(catalog_image_data),
                                            save=False,
                                        )

                                        # Сохранение копии изображения для отображения в поиске
                                        search_image_size = (
                                            getattr(
                                                settings,
                                                "PRODUCT_SEARCH_IMAGE_WIDTH",
                                                42,
                                            ),
                                            getattr(
                                                settings,
                                                "PRODUCT_SEARCH_IMAGE_HEIGHT",
                                                50,
                                            ),
                                        )

                                        search_image = pil_image.copy().resize(
                                            search_image_size
                                        )
                                        search_image_format = getattr(
                                            settings,
                                            "PRODUCT_SEARCH_IAMGE_FORMAT",
                                            "webp",
                                        )
                                        with BytesIO() as buffer:
                                            search_image.save(buffer, format.upper())
                                            search_image_data = buffer.getvalue()

                                        product.search_image.save(
                                            f"search-{filename}.{search_image_format}",
                                            ContentFile(search_image_data),
                                            save=False,
                                        )
                                        product.save(
                                            update_fields=[
                                                "search_image",
                                                "catalog_image",
                                            ]
                                        )

                                    # Стандартизация размеров изображений при импорте
                                    # 16:9 format (the maximum resolution is HD - 1280:720)
                                    width, height = pil_image.size

                                    width = int(min(width, 1280))
                                    height = int((width * 9) / 16)

                                    pil_image = pil_image.resize((width, height))

                                    # Добавление водяного знака на изображение
                                    path_to_watermark = settings.WATERMARK_PATH
                                    opacity = 0.6  # 20% opacity
                                    watermark = Image.open(path_to_watermark)
                                    watermark = set_opacity(watermark, opacity)

                                    watermark = watermark.resize((100, 100))

                                    overlay = Image.new(
                                        "RGBA", pil_image.size, (0, 0, 0, 0)
                                    )
                                    margin = 30  # margin in pixels

                                    position = (
                                        pil_image.width - watermark.width - margin,
                                        pil_image.height - watermark.height - margin,
                                    )
                                    overlay.paste(watermark, position)
                                    pil_image = Image.alpha_composite(
                                        pil_image.convert("RGBA"), overlay
                                    )

                                    with BytesIO() as buffer:
                                        pil_image.save(buffer, format.upper())
                                        pil_image_data = buffer.getvalue()

                                    product_image.image.save(
                                        filename + f".{format}",
                                        ContentFile(pil_image_data),
                                    )
                                    print(f"{product_image} saved")

                                except Exception as err:
                                    failed_images.append(image_url)
                                    print(f"Error while save ProductImage: {err}")

                        # Обработка цен по городам
                        if cities_columns:
                            for column_name in cities_columns:
                                city = City.objects.get(name=column_name)
                                new_price = float(row[column_name])
                                price, created = Price.objects.get_or_create(
                                    product=product, city=city, defaults={"price": new_price}
                                )
                                
                                if not created:
                                    price.old_price = price.price
                                    price.price = new_price
                                    price.save()

                        # Обработка характеристик и их значений
                        if characteristic_columns:
                            for column_name in characteristic_columns:

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


def set_opacity(image: Image, opacity: float):
    if not 0 <= opacity <= 1:
        return

    alpha = image.split()[3]
    new_alpha = alpha.point(lambda i: i * opacity)

    image.putalpha(new_alpha)

    return image


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
