from pathlib import Path

SECRET_KEY = 'secret'
BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'django_filters',
    'tests',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}

ROOT_URLCONF = "tests.urls"

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
