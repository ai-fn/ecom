from .base import *

DEBUG = False

ALLOWED_HOSTS = ['phone.altawest.ru', '94.241.142.109', "dev-api-shop.altawest.ru"]

CELERY_BROKER_URL = 'redis://cache:6379/0'
