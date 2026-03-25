"""
Base settings shared across all environments.
"""

import sys
from pathlib import Path

import environ

env = environ.Env()

# PATHS
BASE_DIR = Path(__file__).resolve().parent.parent  # config/
PROJECT_ROOT = BASE_DIR.parent  # project root

sys.path.append(str(PROJECT_ROOT / "apps"))

# GENERAL
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

ALLOWED_HOSTS = []

# INSTALLED APPS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.staticfiles",
    "storages",
    "rest_framework",
    "corsheaders",
    # Local apps
    "clients",
    "catalog",
    "cart",
    "orders",
    "faq",
    "broadcasts",
    "bot_settings",
    "api",
    "django_rq",
]

# PASSWORD HASHING
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# DEBUG
DEBUG = False
INTERNAL_IPS = ["127.0.0.1"]

# LOCALE
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True

# MEDIA (fallback for local dev without MinIO)
MEDIA_ROOT = PROJECT_ROOT / "public" / "media"
MEDIA_URL = "/media/"

# STATIC FILES
STATIC_ROOT = PROJECT_ROOT / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ─── MinIO / S3 ──────────────────────────────────────────
MINIO_ENDPOINT = env("MINIO_ENDPOINT", default="")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY", default="")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY", default="")
MINIO_BUCKET_NAME = env("MINIO_BUCKET_NAME", default="media")
MINIO_PUBLIC_URL = env("MINIO_PUBLIC_URL", default="")  # публичный URL для браузера

if MINIO_ENDPOINT and MINIO_ACCESS_KEY:
    from urllib.parse import urlparse as _urlparse
    _public = _urlparse(MINIO_PUBLIC_URL) if MINIO_PUBLIC_URL else None

    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "endpoint_url": MINIO_ENDPOINT,
            "access_key": MINIO_ACCESS_KEY,
            "secret_key": MINIO_SECRET_KEY,
            "bucket_name": MINIO_BUCKET_NAME,
            "file_overwrite": False,
            "default_acl": "public-read",
            "querystring_auth": False,
            # custom_domain = host+path без протокола, url_protocol — явно из MINIO_PUBLIC_URL
            "custom_domain": (_public.netloc + _public.path.rstrip("/")) if _public else None,
            "url_protocol": (_public.scheme + ":") if _public else "https:",
        },
    }

# TEMPLATES
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ─── Telegram Bot Token (used for initData validation) ───────
BOT_TOKEN = env("BOT_TOKEN", default="")

# ─── Redis ───────────────────────────────────────────────────
REDIS_HOST = env("REDIS_HOST", default="redis")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_PASSWORD = env("REDIS_PASSWORD", default="")
REDIS_USERNAME = env("REDIS_USERNAME", default="")
REDIS_DB = env.int("REDIS_DB", default=0)

# ─── Django RQ ───────────────────────────────────────────────
RQ_QUEUES = {
    "default": {
        "HOST": REDIS_HOST,
        "PORT": REDIS_PORT,
        "DB": REDIS_DB,
        "PASSWORD": REDIS_PASSWORD,
        "DEFAULT_TIMEOUT": 360,
    },
}

# ─── Django REST Framework ────────────────────────────────────
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "api.exception_handlers.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api.authentication.TelegramInitDataAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# ─── CORS ───────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
