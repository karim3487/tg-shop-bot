from .base import *  # noqa: F403
from .base import env

from django.core.exceptions import ImproperlyConfigured

DEBUG = False

# SECRET_KEY enforcement (Step 9)
SECRET_KEY = env("SECRET_KEY", default=None)
if not SECRET_KEY:
    raise ImproperlyConfigured("The SECRET_KEY environment variable is required in production.")

# CORS hardening (Step 9)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///placeholder"),
}

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# SECURITY
# Railway terminates SSL at the proxy; internal traffic is HTTP.
# Let the proxy handle HTTPS redirection, not Django.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
