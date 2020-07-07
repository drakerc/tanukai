from .base import *

ALLOWED_HOSTS += ['127.0.0.1', 'localhost', '209.239.112.21', 'tanukai.com', 'www.tanukai.com']
DEBUG = True

WSGI_APPLICATION = 'home.wsgi.dev.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CORS_ORIGIN_WHITELIST = (
    'http://localhost',
    'http://209.239.112.21:3000',
    'http://tanukai.com',
    'http://www.tanukai.com',
)
