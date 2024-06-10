import csv
import os
import subprocess
from celery import shared_task

from django.conf import settings
from django.db import transaction
from django.core.mail import EmailMessage

from loguru import logger

from PIL import Image

from django.utils import timezone
from django.utils.text import slugify as django_slugify
from api.serializers.product_detail import ProductDetailSerializer

from shop.models import (
    Characteristic,
    CharacteristicValue,
    Product,
    Price,
    City,
    ProductFile,
    ProductImage,
    Promo,
)
from unidecode import unidecode


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
def update_cities():
    # Clone the git repository
    repo_url = "https://github.com/hflabs/city.git"
    repo_dir = "city_repo"

    try:
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
        logger.debug("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        logger.debug("Error:", e)
        return

    # Open city.csv and extract city names
    city_csv_path = os.path.join(repo_dir, "city.csv")

    try:
        with open(city_csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            city_names = {}
            for row in reader:
                p = int(row["population"])

                if row["city"] != "":
                    city_names[row["city"]] = p
                elif row["region_type"] == "г":
                    city_names[row["region"]] = p
                elif row["area_type"] == "г":
                    city_names[row["area"]] = p
                else:
                    continue

    except FileNotFoundError:
        logger.debug("city.csv not found.")
    except Exception as e:
        logger.debug("Error occurred while extracting city names:", e)
    finally:
        # Clean up: delete the cloned repository directory
        try:
            subprocess.run(["rm", "-rf", repo_dir], check=True)
        except subprocess.CalledProcessError as e:
            logger.debug("Error cleaning up:", e)

    current_cities = City.objects.values_list("name")
    diff = set(city_names.keys()).difference(set(current_cities))

    if len(diff) > 0:
        with transaction.atomic():
            for c in diff:
                p = city_names[c]
                c, created = City.objects.get_or_create(name=c, defaults={"population": p})
                if not created and c.population != p:
                    c.population = p
                    c.save()

        logger.debug("Cities successfully created")


def set_opacity(image: Image, opacity: float):
    if not 0 <= opacity <= 1:
        return

    alpha = image.split()[3]
    new_alpha = alpha.point(lambda i: i * opacity)

    image.putalpha(new_alpha)

    return image



@shared_task
def export_products_to_csv(email_to=None):
    # Экспорт данных в CSV
    products = Product.objects.all().order_by('id')
    prices = Price.objects.all().order_by('product_id', 'city_group__name')
    product_files = ProductFile.objects.all().order_by('product_id')
    product_images = ProductImage.objects.all().order_by('product_id')
    characteristics = Characteristic.objects.all().order_by('name')
    characteristic_values = CharacteristicValue.objects.all().order_by('product_id', 'characteristic__name')

    city_group_names = set(prices.values_list("city_group__name", flat=True))
    characteristic_names = characteristics.values_list("name", flat=True)

    serializer = ProductDetailSerializer(products, many=True)
    file_path = os.path.join(settings.MEDIA_ROOT, "products.csv")

    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Заголовок",
                "Описание",
                "Категории",
                "Артикул",
                "Бренд",
                *characteristic_names,
                *city_group_names,
                "Приоритет",
                "Сертификаты URL",
                "Сертификаты Названия",
                "Изображения",
            ]
        )

        current_prices = {}
        for price in prices:
            current_prices.setdefault(price.product_id, {})
            current_prices[price.product_id][price.city_group.name] = price.price

        current_characteristics = {}
        for cv in characteristic_values:
            current_characteristics.setdefault(cv.product_id, {})
            current_characteristics[cv.product_id][cv.characteristic.name] = cv.value

        current_files = {}
        for pf in product_files:
            current_files.setdefault(pf.product_id, [])
            current_files[pf.product_id].append((os.path.basename(pf.file.name), pf.name))

        current_images = {}
        for pi in product_images:
            current_images.setdefault(pi.product_id, [])
            current_images[pi.product_id].append(os.path.basename(pi.image.url))

        for product in serializer.data:
            product_id = product["id"]

            price_cells = [current_prices.get(product_id, {}).get(name, "") for name in city_group_names]

            categories_names = " || ".join(
                [item[0] for item in product["category"].get("parents", [])] + [product["category"]["name"]]
            )

            characteristic_values_cells = [current_characteristics.get(product_id, {}).get(name, "") for name in characteristic_names]

            product_file_urls = " || ".join([file[0] for file in current_files.get(product_id, [])])
            product_file_names = " || ".join([file[1] for file in current_files.get(product_id, [])])

            product_image_urls = " || ".join(current_images.get(product_id, []))

            writer.writerow(
                [
                    product.get("title", ""),
                    product.get("description", ""),
                    categories_names,
                    product.get("article", ""),
                    product["brand"].get("name", "") if product.get("brand") else "",
                    *characteristic_values_cells,
                    *price_cells,
                    product.get("priority", ""),
                    product_file_urls,
                    product_file_names,
                    product_image_urls,
                ]
            )

    if email_to:
        send_email_with_attachment(email_to, file_path)

    return file_path


def send_email_with_attachment(email_to, file_path):
    subject = "Экспортированные продукты CSV"
    body = "Пожалуйста, найдите приложенный CSV-файл с экспортированными продуктами."
    email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [email_to])
    email.attach_file(file_path)
    result = email.send(fail_silently=True)
    logger.debug(f"CSV file of products was mailed with status: {result}")
