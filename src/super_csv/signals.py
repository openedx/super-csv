"""
Signals for super_csv
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CSVOperation
from .tasks import expire_data


@receiver(post_save, sender=CSVOperation)
def expire_on_save(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Expire CSV data, asynchronously
    """
    # to slightly reduce impact, we'll do the expiration check
    # every third operation
    if instance.pk % 3 == 0:
        expire_data.apply_async()
