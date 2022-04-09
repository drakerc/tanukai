import config
from .base import *

DEBUG = False
ALLOWED_HOSTS += [
    "127.0.0.1",
    "localhost",
    "209.239.112.21",
    "tanukai.com",
    "www.tanukai.com",
]
WSGI_APPLICATION = "tanukai_backend.wsgi.prod.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config.MYSQL_DATABASE,
        "USER": config.MYSQL_USER,
        "PASSWORD": config.MYSQL_PASSWORD,
        "HOST": config.MYSQL_HOST,
        "PORT": config.MYSQL_PORT,
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "logfile": {
            "class": "logging.FileHandler",
            "filename": "server.log",
        },
        "stream_logger": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["logfile", "stream_logger"],
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

CORS_ORIGIN_WHITELIST = (
    "http://localhost",
    "http://localhost:3000",
    "http://209.239.112.21:3000",
    "http://tanukai.com",
    "https://tanukai.com",
    "http://www.tanukai.com",
)
