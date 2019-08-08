"""
Tasks for async processing of csv files.
"""
from __future__ import absolute_import, unicode_literals

from celery import task
from django.conf import settings

# pylint: disable=unused-import
from .mixins import do_deferred_commit
from .models import CSVOperation


@task
def expire_data():
    """
    Expire CSV data older than settings.CSV_EXPIRATION_DAYS
    """
    CSVOperation.expire_data(settings.CSV_EXPIRATION_DAYS)
