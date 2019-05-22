"""
Tasks for async processing of csv files.
"""
from __future__ import absolute_import, unicode_literals

import importlib
import json
import logging

from celery import task
from super_csv.models import CSVOperation

log = logging.getLogger(__name__)


@task(bind=True)
def do_deferred_commit(self, operation_id):
    operation = CSVOperation.objects.get(pk=operation_id)
    log.info('Loading CSV state %s', operation.data.name)
    state = json.loads(operation.data.read())
    module_name, classname = state.pop('__class__')

    instance = getattr(importlib.import_module(module_name), classname)(**state)
    instance.commit(running_task=True)
    status = instance.status()
    log.info('Commit succeeded %s %s', instance, status)
    operation = instance.save()
    log.info('Saved CSV state %s %s', instance, operation.data.name)
    return status
