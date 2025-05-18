import os
import json
import sys
from pathlib import Path
from datetime import timedelta

import dj_database_url
from decouple import config
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-@9mw!2c2!do@e=%)+^zq_+0_e@1d!mt_(c62utaq5(t#n51l1!"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED HOSTS
ALLOWED_HOSTS = ["*"]

# DATABASE
if os.getenv("ENV") == "production":
    REDIS_URL = os.getenv("REDIS_URL")
else:
    REDIS_URL = "redis://localhost:6379/0"

CELERY_BROKER_URL = (
    f"{REDIS_URL}?ssl_cert_reqs=CERT_NONE" if "rediss" in REDIS_URL else REDIS_URL
)
CELERY_RESULT_BACKEND = (
    f"{REDIS_URL}?ssl_cert_reqs=CERT_NONE" if "rediss" in REDIS_URL else REDIS_URL
)


STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "audit",
    "branches",
    "core",
    "corsheaders",
    "inventory_management",
    "order_management",
    "sales",
    "users",
    "customers",
    "payment",
    "discounts",
    "django_celery_beat",
    "dashboard",
    "django_filters",
    "category"
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "pos_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "pos_backend.wsgi.application"

# Database
if os.getenv("ENV") == "production":
    DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL"))}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DATABASE_NAME"),
            "USER": config("DATABASE_USER"),
            "PASSWORD": config("DATABASE_PASSWORD"),
            "HOST": config("DATABASE_HOST", default="localhost"),
            "PORT": config("DATABASE_PORT", default="5432"),
        }
    }

if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        },
    }

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

ROOT_URLCONF = "pos_backend.urls"
AUTH_USER_MODEL = "users.CustomUser"

# Google Cloud Storage settings
GS_BUCKET_NAME = "dropshop-media-bucket"
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_CREDENTIALS_DICT = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))


GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
    GS_CREDENTIALS_DICT
)


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Default Django authentication
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://pos-frontend-bright-f93c1e04a9c4.herokuapp.com"
]


# Allow these headers in requests from the frontend
CORS_ALLOW_HEADERS = [
    "content-type",
    "authorization",
    "x-requested-with",
]

# Expose these headers in the response for the frontend to access
CORS_EXPOSE_HEADERS = [
    "content-type",
    "authorization",
]

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_CREDENTIALS = True


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
