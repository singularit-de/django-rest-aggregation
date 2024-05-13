from pathlib import Path

SECRET_KEY = "secret"
BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "django_filters",
    "tests",
]

postgres = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "TestDB",
    "USER": "postgres",
    "PASSWORD": "mysecretpassword",
    "HOST": "localhost",
    "PORT": "5432",
}

mysql = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": "TestDB",
    "USER": "root",
    "PASSWORD": "mysecretpassword",
    "HOST": "localhost",
    "PORT": "3306",
}

mariadb = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": "TestDB",
    "USER": "root",
    "PASSWORD": "mysecretpassword",
    "HOST": "localhost",
    "PORT": "3306",
}

sqlite = {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}

mssql = {
    "ENGINE": "mssql",
    "NAME": "TestDB",
    "USER": "sa",
    "PASSWORD": "yourStrong(!)Password",
    "HOST": "127.0.0.1",
    "PORT": "1433",
}

DATABASES = {"default": sqlite}

ROOT_URLCONF = "tests.urls"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
