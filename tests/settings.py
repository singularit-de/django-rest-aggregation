"""Settings for the test project.

The database is chosen with the ``DB_BACKEND`` environment variable (``sqlite`` by default, an in-memory
database). Connection details for the other backends can be overridden with ``DB_NAME``, ``DB_USER``,
``DB_PASSWORD``, ``DB_HOST`` and ``DB_PORT``.
"""

import os

SECRET_KEY = "not-secret-only-for-tests"
DEBUG = False
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "django_filters",
    "tests.testapp",
]

MIDDLEWARE = []
ROOT_URLCONF = "tests.testapp.urls"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DB_BACKENDS = {
    "sqlite": {"ENGINE": "django.db.backends.sqlite3"},
    "postgres": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "TestDB",
        "USER": "postgres",
        "PASSWORD": "mysecretpassword",
        "HOST": "localhost",
        "PORT": "5432",
    },
    "mysql": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "TestDB",
        "USER": "root",
        "PASSWORD": "mysecretpassword",
        "HOST": "localhost",
        "PORT": "3306",
    },
    "mssql": {
        "ENGINE": "mssql",
        "NAME": "TestDB",
        "USER": "sa",
        "PASSWORD": "yourStrong(!)Password",
        "HOST": "127.0.0.1",
        "PORT": "1433",
        # mssql-python ships its own ODBC Driver 18, so no system ODBC packages are needed.
        "OPTIONS": {"python_driver": "mssql_python", "extra_params": "TrustServerCertificate=yes"},
    },
}
# MariaDB uses Django's MySQL backend.
DB_BACKENDS["mariadb"] = DB_BACKENDS["mysql"]

DB_BACKEND = os.environ.get("DB_BACKEND", "sqlite")
database = dict(DB_BACKENDS[DB_BACKEND])
for key in ["NAME", "USER", "PASSWORD", "HOST", "PORT"]:
    if f"DB_{key}" in os.environ:
        database[key] = os.environ[f"DB_{key}"]

DATABASES = {"default": database}
