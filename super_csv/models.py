"""
Database models for super_csv.
"""

import logging
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models
from django.utils.timezone import now
from model_utils.models import TimeStampedModel

log = logging.getLogger(__name__)


def csv_class_path(instance, filename):
    return f'csv/{instance.class_name}/{instance.unique_id}/{filename}'


class CSVOperation(TimeStampedModel):
    """
    Store processing operations/results.

    .. no_pii:
    """
    class_name = models.CharField(max_length=255, db_index=True)
    unique_id = models.CharField(max_length=255, db_index=True)
    operation = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255, blank=True, default='')
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    data = models.FileField(upload_to=csv_class_path, max_length=255)

    class Meta:
        app_label = "super_csv"

    @classmethod
    def _get_class_name(cls, obj):
        if not isinstance(obj, str):
            obj = '%s.%s' % (obj.__class__.__module__, obj.__class__.__name__)
        return obj

    @classmethod
    def get_all_history(cls, class_name_or_obj, unique_id):
        return cls.objects.filter(
            class_name=cls._get_class_name(class_name_or_obj),
            unique_id=unique_id)

    @classmethod
    def get_latest(cls, class_name_or_obj, unique_id):
        """
        Get the latest Entry.
        """
        try:
            return cls.get_all_history(class_name_or_obj, unique_id).order_by('-modified')[0]
        except IndexError:
            return None

    @classmethod
    def record_operation(cls, class_name_or_obj, unique_id, operation, data, original_filename='', user=None):
        """
        Save a CSVOperation
        """
        instance = cls(
            class_name=cls._get_class_name(class_name_or_obj),
            unique_id=unique_id,
            operation=operation,
            original_filename=original_filename,
            user=user,
        )
        instance.data.save(uuid.uuid4(), ContentFile(data))
        return instance

    @classmethod
    def expire_data(cls, expiration_days):
        """
        Delete data older than expiration_time (days)
        """
        if expiration_days:
            expiration = now() - timedelta(days=expiration_days)
            for obj in cls.objects.filter(modified__lte=expiration):
                log.info('Expiring %r', obj.data)
                obj.data.delete()

    def __str__(self):
        return f'Operation for {self.class_name} {self.unique_id}'

    def delete(self, *args):
        self.data.delete()
        super().delete(*args)
