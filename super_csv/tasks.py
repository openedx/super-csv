"""
Tasks for async processing of csv files.
"""

from celery import task
from django.conf import settings
from edx_django_utils.monitoring import set_code_owner_attribute

# pylint: disable=unused-import
from .mixins import do_deferred_commit
from .models import CSVOperation


@task
@set_code_owner_attribute
def expire_data():
    """
    Expire CSV data older than settings.CSV_EXPIRATION_DAYS
    """
    CSVOperation.expire_data(settings.CSV_EXPIRATION_DAYS)
