from .base import *

DEBUG = True

ALLOWED_HOSTS = ["phone.altawest.ru", "94.241.142.109", "0.0.0.0", "127.0.0.1"]

CELERY_BROKER_URL = "redis://cache:6379/0"
