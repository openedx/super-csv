"""
Tasks for async processing of csv files.
"""
from __future__ import absolute_import, unicode_literals

import logging

from celery import task

log = logging.getLogger(__name__)


@task(bind=True)
def do_deferred_commit(self, operation_id):
    """
    Commit the CSV Operation, asynchronously.
    """
    from .csv_processor import DeferrableMixin
    instance = DeferrableMixin.load(operation_id, load_subclasses=True)
    instance.commit(running_task=True)
    status = instance.status()
    log.info('Commit succeeded %s %s', instance, status)
    operation = instance.save()
    log.info('Saved CSV state %s %s', instance, operation.data.name)
    return status
