"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from os.path import abspath, dirname, join

from celery import Celery


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "default.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "super_csv",
)

LOCALE_PATHS = [
    root("super_csv", "conf", "locale"),
]

ROOT_URLCONF = "super_csv.urls"
CSV_EXPIRATION_DAYS = 1


SECRET_KEY = "insecure-secret-key"

APP = Celery()
APP.conf.CELERY_ALWAYS_EAGER = True
APP.conf.CELERY_RESULT_BACKEND = "db+sqlite:///:memory:"
APP.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
APP.conf.CELERY_BROKER_URL = BROKER_URL = "memory://"
APP.conf.CELERY_BROKER_TRANSPORT = "memory://"
APP.conf.CELERY_BROKER_HOSTNAME = "localhost"
