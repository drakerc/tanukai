from .base import *

ALLOWED_HOSTS += [
    "127.0.0.1",
    "localhost",
    "209.239.112.21",
    "tanukai.com",
    "www.tanukai.com",
    "fursuitdb.com",
    "www.fursuitdb.com",
]
DEBUG = True

WSGI_APPLICATION = "tanukai_backend.wsgi.dev.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

CORS_ORIGIN_WHITELIST = (
    "http://localhost",
    "http://localhost:3000",
    "http://209.239.112.21:3000",
    "http://tanukai.com",
    "https://tanukai.com",
    "http://www.tanukai.com",
    "http://fursuitdb.com",
    "https://fursuitdb.com",
    "http://www.fursuitdb.com",
)
