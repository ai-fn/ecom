from loguru import logger

from unidecode import unidecode
from celery import group, shared_task

from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
from django.utils.text import slugify as django_slugify

from shop.models import Promo
from account.models import CityGroup


def custom_slugify(value):
    return django_slugify(unidecode(value))


@shared_task
def update_promo_status():
    one_day_ago = timezone.now().date() + timezone.timedelta(days=1)

    expired_promos = Promo.objects.filter(active_to__lte=one_day_ago)

    expired_promos.update(is_active=False)

@shared_task
def collect_single_feed_xml(city_group_name: str):
    from shop.services import FeedsService
    FeedsService.collect_feeds(city_group_name)
    return f"Feeds for {city_group_name} successfully collected"


@shared_task
def collect_feed_xml_files():
    tasks = group(collect_single_feed_xml.s(cg.name) for cg in CityGroup.objects.all())
    result = tasks.apply_async()
    return result


def send_email_with_attachment(email_to, file_path):
    subject = "Экспортированные продукты CSV"
    body = "Пожалуйста, найдите приложенный CSV-файл с экспортированными продуктами."
    email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [email_to])
    email.attach_file(file_path)
    result = email.send(fail_silently=True)
    logger.debug(f"CSV file of products was mailed with status: {result}")
