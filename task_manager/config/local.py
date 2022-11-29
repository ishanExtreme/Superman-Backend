from .base import *  # noqa
from .base import env
import os

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", ".loca.lt", ".ngrok.io"]

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# email backend to send emails
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOW_ALL_ORIGINS = True