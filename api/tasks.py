from loguru import logger

from unidecode import unidecode
from celery import group, shared_task

from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
from django.utils.text import slugify as django_slugify

from shop.models import Promo
from shop.utils import get_shop_name
from account.models import City


def custom_slugify(value):
    return django_slugify(unidecode(value))


@shared_task
def update_promo_status():
    one_day_ago = timezone.now().date() + timezone.timedelta(days=1)
    expired_promos = Promo.objects.filter(active_to__lte=one_day_ago)
    expired_promos.update(is_active=False)

@shared_task
def collect_single_feed_xml(city_name: str):
    from shop.services import FeedsService

    FeedsService.collect_feeds(city_name)
    return f"Feeds for {city_name} successfully collected"

@shared_task
def collect_sitemap_xml(city_name: str, domain: str):
    from shop.services import SitemapService
    from shop.sitemaps import ProductSitemap, CategorySitemap

    sitemaps = {
        "products": ProductSitemap,
        "categories": CategorySitemap,
    }
    SitemapService.collect(city_name, domain, sitemaps, save_to_file=True)

@shared_task
def collect_sitemaps():
    tasks = []
    for c in City.objects.filter(is_active=True):
        tasks.append(collect_sitemap_xml.s(c.name, c.domain))

    g = group(tasks)
    result = g.apply_async()
    return result


@shared_task
def collect_feed_xml_files():
    tasks = group(collect_single_feed_xml.s(c.name) for c in City.objects.all())
    result = tasks.apply_async()
    return result


def send_email_with_attachment(email_to, file_path):
    subject = f"Экспорт {get_shop_name()}"
    email = EmailMessage(subject, from_email=settings.EMAIL_HOST_USER, to=[email_to])
    email.attach_file(file_path)
    result = email.send(fail_silently=True)
    logger.debug(f"Export File was mailed with status: {result}")
