"""
Django settings for megashop project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from loguru import logger

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY") or "dummy_secret_key"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CSRF_TRUSTED_ORIGINS = ["https://dev-api-shop.altawest.ru", "https://*.127.0.0.1"]
ALLOWED_HOSTS = ["127.0.0.1"]
# TODO попробовать убрать ALLOW_ALL
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOWED_ORIGINS = [
    "http://188.235.34.60:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://api.zadarma.com",
    "https://dev-api-shop.altawest.ru",
]
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_elasticsearch_dsl",
    "django_elasticsearch_dsl_drf",
    "corsheaders",
    "django_prometheus",
    "django_celery_beat",
    "django_celery_results",
    "account.apps.AccountConfig",
    "blog.apps.BlogConfig",
    "shop.apps.ShopConfig",
    "cart.apps.CartConfig",
    "mptt",  # Древовидное меню
    "debug_toolbar",  # Дебаг тулбар
    "api.apps.ApiConfig",
]

AUTH_USER_MODEL = "account.CustomUser"

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # Дебаг тулбар
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Статические файлы
    "shop.middlewares.SubdomainMiddleware",  # middleware на получение 3 субдомена
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "megashop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shop.context_processors.shop",
            ],
        },
    },
]

WSGI_APPLICATION = "megashop.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DB_NAMES = ("test", "default")
USE_TEST_DB = os.environ.get("USE_TEST_DB", "0") == "1"

DATABASES = {
    DB_NAMES[not USE_TEST_DB]: {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "default_db_name"),
        "USER": os.environ.get("POSTGRES_USER", "default_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "default_password"),
        "HOST": "db",  # Или другой хост, если он определён
        "PORT": "5432",  # Стандартный порт для PostgreSQL
    },
    DB_NAMES[USE_TEST_DB]: {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": "test_" + os.environ.get("POSTGRES_DB", "default_db_name"),
        "USER": os.environ.get("POSTGRES_USER", "default_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "default_password"),
        "HOST": "db",  # Или другой хост, если он определён
        "PORT": "5432",  # Стандартный порт для PostgreSQL
    }
}

# Pagination settings
PAGINATE_BY = os.getenv('PAGINATE_BY') or 9
PAGE_SIZE = os.getenv('PAGE_SIZE') or 32

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": PAGE_SIZE,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10000/day",
        "user": "100000/day",
    },
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=15),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.MyTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Megashop Project API",
    "DESCRIPTION": "Api For Megashop",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    # OTHER SETTINGS
}
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": "http://elasticsearch:9200",
        # "http_auth": ("elastic", "k1fjic392h9io"),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

LOGIN_URL = "login"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

WATERMARK_PATH = os.path.join(MEDIA_ROOT, os.getenv('WATERMARK_PATH', 'watermark.png'))
try:
    WATERMARK_OPACITY = float(os.environ.get("WATERMARK_OPACITY", 60))
    if WATERMARK_OPACITY > 100:
        raise ValueError("Watermark opaticy must be in range from 0 to 100")
except ValueError as e:
    logger.error(f"invalid watermark opacity setting, using default (0.6): {e}")
    WATERMARK_OPACITY = 60 / 10
else:
    WATERMARK_OPACITY /= 10

try:
    WATERMARK_MARGIN = int(os.environ.get("WATERMARK_MARGIN", 30))
except ValueError as e:
    logger.error(f"invalid watermark margin setting, using defult (30): {e}")
    WATERMARK_MARGIN = 30

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = "redis://cache:6379/0"
CELERY_RESULT_BACKEND = f"db+postgresql://{os.environ.get('POSTGRES_USER', 'default_user')}:{os.environ.get('POSTGRES_PASSWORD', 'default_password')}@db/{os.environ.get('POSTGRES_DB', 'default_db_name')}"

# Default token generator setting
DEFAULT_TOKEN_GENERATOR = PasswordResetTokenGenerator()

# Email settings
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', "True") == "True"
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', "False") == "True"
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# SMS settings
SMS_LOGIN = os.environ.get("SMS_LOGIN", "DEFAULT")
SMS_PASSWORD = os.environ.get("SMS_PASSWORD", "DEFAULT")

CONFIRM_CODE_LIFE_TIME = os.environ.get("CONFIRM_CODE_LIFE_TIME", 60)
SMS_CACHE_PREFIX = os.environ.get("SMS_CACHE_PREFIX", "SMS_CACHE")
CACHE_PREFIX = os.environ.get("CACHE_PREFIX", "SMS_CACHE")

BASE_DOMAIN = os.environ.get('BASE_DOMAIN', 'krov.market')

# TG SETTINGS
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "DEFAULT")

# SEND VERIFY CODE
SEND_TO_TELEGRAM = os.environ.get("SEND_TO_TELEGRAM") == "True"
CHAT_ID = os.environ.get("CHAT_ID", "DEFAULT")

# CACHE SETTINGS
CACHE_LOCATION = os.environ.get("CACHE_LOCATION", "redis://cache:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_LOCATION,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": CACHE_PREFIX
    }
}