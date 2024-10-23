from .base import *

DEBUG = True
CORS_ORIGIN_ALLOW_ALL = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(";")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(";")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(";")
