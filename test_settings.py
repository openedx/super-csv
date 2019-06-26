"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join

import djcelery


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'super_csv',
    'djcelery',
)

LOCALE_PATHS = [
    root('super_csv', 'conf', 'locale'),
]

ROOT_URLCONF = 'super_csv.urls'

SECRET_KEY = 'insecure-secret-key'
CELERY_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND = 'djcelery.backends.cache:CacheBackend'
CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
CELERY_BROKER_URL = BROKER_URL = 'memory://'
CELERY_BROKER_TRANSPORT = 'memory://'
CELERY_BROKER_HOSTNAME = 'localhost'

djcelery.setup_loader()
