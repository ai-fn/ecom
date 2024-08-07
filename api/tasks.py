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

from shop.models import (
    City,
    Promo,
)
from unidecode import unidecode


def custom_slugify(value):
    return django_slugify(unidecode(value))


@shared_task
def update_promo_status():
    one_day_ago = timezone.now().date() + timezone.timedelta(days=1)

    expired_promos = Promo.objects.filter(active_to__lte=one_day_ago)

    expired_promos.update(is_active=False)


@shared_task
def update_cities():
    repo_url = "https://github.com/hflabs/city.git"
    repo_dir = "city_repo"

    try:
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
        logger.debug("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        logger.debug("Error:", e)
        return

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


def send_email_with_attachment(email_to, file_path):
    subject = "Экспортированные продукты CSV"
    body = "Пожалуйста, найдите приложенный CSV-файл с экспортированными продуктами."
    email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [email_to])
    email.attach_file(file_path)
    result = email.send(fail_silently=True)
    logger.debug(f"CSV file of products was mailed with status: {result}")
