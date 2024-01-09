from .base import *

DEBUG = False

ALLOWED_HOSTS = ['phone.altawest.ru', '94.241.142.109']

CELERY_BROKER_URL = 'redis://cache:6379/0'
