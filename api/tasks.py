import csv
import os
import subprocess
from celery import shared_task
from django.conf import settings
from django.db import transaction
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
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        print("Error:", e)
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
        print("city.csv not found.")
    except Exception as e:
        print("Error occurred while extracting city names:", e)
    finally:
        # Clean up: delete the cloned repository directory
        try:
            subprocess.run(["rm", "-rf", repo_dir], check=True)
        except subprocess.CalledProcessError as e:
            print("Error cleaning up:", e)

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

        print("Cities successfully created")


def set_opacity(image: Image, opacity: float):
    if not 0 <= opacity <= 1:
        return

    alpha = image.split()[3]
    new_alpha = alpha.point(lambda i: i * opacity)

    image.putalpha(new_alpha)

    return image


# TODO add "SKU" processing
@shared_task
def export_products_to_csv(email_to=None):
    # Экспорт данных в CSV
    products = Product.objects.all()
    prices = Price.objects.all()
    city_group_names = prices.values_list("city_group__name", flat=True)
    characteristic_names = Characteristic.objects.values_list("name", flat=True)
    characteristic_values = (
        CharacteristicValue.objects.values_list("value", "characteristic", "product")
        .order_by("characteristic__name")
        .distinct("characteristic__name")
    )

    serializer = ProductDetailSerializer(products, many=True)
    file_path = os.path.join(settings.MEDIA_ROOT, "products.csv")

    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "TITLE",
                "CATEGORIES",
                "SKU",
                "DESCRIPTION",
                *characteristic_names,
                *city_group_names,
                "PRIORITY",
            ]
        )
        for product in serializer.data:

            # Select product prices by city name
            price_cells = []
            for name in city_group_names:
                try:
                    val = prices.get(product=product["id"], city_group__name=name).price
                except (Price.DoesNotExist, AttributeError):
                    val = ""
                price_cells.append(val)

            categories_names = " | ".join(
                [item[0] for item in product["category"].get("parents")]
                + [
                    product["category"]["name"],
                    product["title"].split(", ")[-1].capitalize(),
                ]
            )

            # Select product characteristics by characterictic name
            characteristic_values_cells = []
            for item in characteristic_names:
                try:
                    value = characteristic_values.get(
                        product=product["id"], characteristic__name=item
                    )[0]
                except CharacteristicValue.DoesNotExist:
                    value = ""
                characteristic_values_cells.append(value)

            writer.writerow(
                [
                    product["title"],
                    categories_names,
                    product["article"],
                    product["description"],
                    *characteristic_values_cells,
                    *price_cells,
                    product["priority"],
                ]
            )

    return file_path
