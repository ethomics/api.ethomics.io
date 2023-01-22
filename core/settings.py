import os
# from .secrets import SECRET_KEY, BASE_DIR, DATABASES
import environ

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "xxxxxxxxxxxxxx123"),
    DB_ENGINE=(str, "django.db.backends.sqlite3"),
    DB_NAME=(str, "db.sqlite3"),
    DB_HOST=(str, "localhost"),
    DB_USER=(str, ""),
    DB_PASSWORD=(str, ""),
    MEDIA_ROOT=(str, "uploads"),
    ADMIN=(bool, False),
    MAILGUN_API_KEY=(str, "MAILGUN_KEY"),
    EMAIL_HOST_PASSWORD=(str, "EMAIL_HOST_PASSWORD"),
    SERVE_FILES=(bool, False)
)
APPEND_SLASH = False
ALLOWED_HOSTS = ["*"]

DEBUG = env("DEBUG")

SECRET_KEY = env("SECRET_KEY")

ADMIN = env("ADMIN")

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "graphene_django",
    "corsheaders",
    "core",
    "admin",
    "django_cleanup.apps.CleanupConfig",
]

USE_TZ = True
TIME_ZONE = "UTC"

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.AuthenticationMiddleware"
] + (["admin.middleware.ActivityMiddleware"])

DATABASES = {"default": {
    "ENGINE": env("DB_ENGINE"),
    "NAME": env("DB_NAME"),
    "USER": env("DB_USER"),
    "HOST": env("DB_HOST"),
    "PASSWORD": env("DB_PASSWORD"),
}}

AUTH_PASSWORD_VALIDATORS = [{
    "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    "OPTIONS": {"min_length": 9}
},{
    "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
}, {
    "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
}]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

TOKEN_TIMEOUT = 15
SESSION_LENGTH_DAYS = 365

GRAPHENE = {
    "SCHEMA": "admin.schema.schema" if env("ADMIN") else "core.schema.schema"
}

SERVE_FILES = env("SERVE_FILES")
MEDIA_URL = "/uploads/"
MEDIA_ROOT = env("MEDIA_ROOT")
