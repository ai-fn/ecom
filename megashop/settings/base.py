"""
Django settings for megashop project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
import re
from datetime import timedelta
from pathlib import Path

from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY") or "dummy_secret_key"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(";")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(";")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(";")
CORS_ALLOWED_ORIGIN_REGEXES = [re.compile(x) for x in os.getenv("CORS_ALLOWED_ORIGIN_REGEXES", "").split(";")]

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
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
    "import_app.apps.ImportAppConfig",
    "export_app.apps.ExportAppConfig",
    "mptt",
    "debug_toolbar",
    "api.apps.ApiConfig",
    "storages",
    "crm_integration",
]

IMPORT_EXPORT_APPS = [
    "shop",
    "shop",
    "cart",
    "blog",
    "account",
    "import_app",
    "export_app",
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
            ],
        },
    },
]

WSGI_APPLICATION = "megashop.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DB_NAMES = ("test", "default")
USE_TEST_DB = os.getenv("USE_TEST_DB", "0") == "1"

# PORTS SETTINGS

POSTGRES_PORT = 5432
REDIS_PORT = 6379
REDIS_HOST = os.getenv("REDIS_HOST", "cache")
DJANGO_PORT = os.getenv("DJANGO_PORT", "8000")
PROMETHEUS_PORT = os.getenv("PROMETHEUS_PORT", "9090")

ELASTICSEARCH_PASSWORD = os.getenv("ELASTIC_PASSWORD")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ELASTICSEARCH_HTTP_PORT = 9200
ELASTICSEARCH_TRANSPORT_PORT = 9300

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_NAME = os.getenv("POSTGRES_DB", "default_db_name")
POSTGRES_USER = os.getenv("POSTGRES_USER", "default_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default_password")

DATABASES = {
    DB_NAMES[not USE_TEST_DB]: {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": POSTGRES_NAME,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
    },
    DB_NAMES[USE_TEST_DB]: {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": "test_" + POSTGRES_NAME,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
    },
}

# Pagination settings
PAGINATE_BY = os.getenv("PAGINATE_BY") or 9
PAGE_SIZE = os.getenv("PAGE_SIZE") or 32

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
}
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_HTTP_PORT}",
        "basic_auth": ("elastic", ELASTICSEARCH_PASSWORD),
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


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

LOGIN_URL = "/admin/login/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:6379/0"
CELERY_RESULT_BACKEND = f"db+postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_NAME}"

# Default token generator setting
DEFAULT_TOKEN_GENERATOR = PasswordResetTokenGenerator()

# Email settings
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False") == "True"
EMAIL_PORT = os.getenv("EMAIL_PORT", "2525")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# SMS settings
SMS_RU_TOKEN = os.getenv("SMS_RU_TOKEN", "DEFAULT")

CONFIRM_CODE_LIFE_TIME = os.getenv("CONFIRM_CODE_LIFE_TIME", 60)
SMS_CACHE_PREFIX = os.getenv("SMS_CACHE_PREFIX", "SMS_CACHE")
CACHE_PREFIX = os.getenv("CACHE_PREFIX", "CACHE_PREFIX")

# TG SETTINGS
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "DEFAULT")

# SEND VERIFY CODE
SEND_TO_TELEGRAM = os.getenv("SEND_TO_TELEGRAM") == "True"
CHAT_ID = os.getenv("CHAT_ID", "DEFAULT")

# CACHE SETTINGS
CACHE_LOCATION = f"redis://{REDIS_HOST}:6379/0"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_LOCATION,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": CACHE_PREFIX,
    },
    "dev_env":{
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# VERIFY EMAIL SETTINGS
EMAIL_CACHE_PREFIX = os.getenv("EMAIL_CACHE_PREFIX", "EMAIL_CACHE_PREFIX")
EMAIL_CACHE_LIFE_TIME = int(os.getenv("EMAIL_CACHE_LIFE_TIME", 3600))
EMAIL_CACHE_REMAINING_TIME = int(os.getenv("EMAIL_CACHE_REMAINING_TIME", 120))

# BITRIX SETTINGS
LEAD_LIST_WEBHOOK_URL = os.getenv("LEAD_LIST_WEBHOOK_URL")
LEAD_GET_WEBHOOK_URL = os.getenv("LEAD_GET_WEBHOOK_URL")
LEAD_ADD_WEBHOOK_URL = os.getenv("LEAD_ADD_WEBHOOK_URL")
LEAD_UPDATE_WEBHOOK_URL = os.getenv("LEAD_UPDATE_WEBHOOK_URL")
LEAD_FIELDS_WEBHOOK_URL = os.getenv("LEAD_FIELDS_WEBHOOK_URL")
LEAD_DELETE_WEBHOOK_URL = os.getenv("LEAD_DELETE_WEBHOOK_URL")

DEFAULT_LEAD_USER_EMAIL = os.getenv("DEFAULT_LEAD_USER_EMAIL")
GET_USER_WEBHOOK_URL = os.getenv("GET_USER_WEBHOOK_URL")


DEFAULT_CITY_GROUP_NAME = os.getenv("DEFAULT_CITY_GROUP_NAME", "Московская область")
DEFAULT_CITY_NAME = os.getenv("DEFAULT_CITY_NAME", "Москва")

LOGIN_CODE_LENGTH = int(os.getenv("LOGIN_CODE_LENGTH", "4"))
REGISTER_CODE_LENGTH = int(os.getenv("REGISTER_CODE_LENGTH", "4"))
FEEDS_DIR = "feeds"
SITEMAP_DIR = "sitemaps"

LOGO_URL = os.getenv("LOGO_PATH", "logos/logo.png")

AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ENDPOINT_URL = 'https://s3.timeweb.cloud'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.timeweb.cloud' % AWS_STORAGE_BUCKET_NAME

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'megashop', 'static'),
]

STATICFILES_STORAGE = 'megashop.storages.botoS3.StaticStorage'
DEFAULT_FILE_STORAGE = 'megashop.storages.botoS3.MediaStorage'

APP_NAME = os.getenv("APP_NAME")
