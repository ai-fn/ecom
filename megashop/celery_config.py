import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megashop.settings.local')

app = Celery('megashop')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.enable_utc = False
app.conf.timezone = "Europe/Moscow"

app.autodiscover_tasks()