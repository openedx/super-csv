"""
CSV Processing mixins.

ChecksumMixin generates and validates checksums on arbitrary columns.

DeferrableMixin handles asynchronous processing.
"""

import hashlib
import importlib
import logging

import simplejson as json
from celery import shared_task
from celery.result import AsyncResult
from celery_utils.logged_task import LoggedTask
from crum import get_current_user
from django.conf import settings
from django.db import DatabaseError, transaction
from django.utils.translation import ugettext as _
from edx_django_utils.monitoring import set_code_owner_attribute

from .exceptions import ValidationError
from .models import CSVOperation
from .serializers import CSVOperationSerializer

log = logging.getLogger(__name__)


class ChecksumMixin:
    """
    CSV mixin that will create and verify a checksum column in the CSV file
    Specify a list checksum_columns in the subclass.
    """
    secret = settings.SECRET_KEY
    checksum_columns = []
    checksum_fieldname = 'csum'
    checksum_size = 4

    def _get_checksum(self, row):
        to_check = ''.join(str(row[key] if row[key] is not None else '') for key in self.checksum_columns)
        to_check += self.secret
        return '@%s' % hashlib.md5(to_check.encode('utf8')).hexdigest()[:self.checksum_size]

    def preprocess_export_row(self, row):
        """
        Set the checksum column in the row.
        """
        row[self.checksum_fieldname] = self._get_checksum(row)

    def validate_row(self, row):
        """
        Verifies that the calculated checksum matches the stored checksum.
        """
        if self._get_checksum(row) != row[self.checksum_fieldname]:
            raise ValidationError(
                _("Checksum mismatch. Required columns cannot be edited: {}").format(
                    ','.join(self.checksum_columns)
                )
            )


@shared_task(bind=True, base=LoggedTask)
@set_code_owner_attribute
def do_deferred_commit(self, operation_id):  # pylint: disable=unused-argument
    """
    Commit the CSV Operation, asynchronously.
    """
    instance = DeferrableMixin.load(operation_id, load_subclasses=True)
    instance.commit(running_task=True)
    status = instance.status()
    log.info('Commit succeeded %s %s', instance, status)
    operation = instance.save()
    log.info('Saved CSV state %s %s', instance, operation.data.name)
    return status


class DeferrableMixin:
    """
    Mixin that automatically commits data using celery.

    Subclasses should specify `size_to_defer` to tune when to
    run the commit synchronously or asynchronously.

    Subclasses must override get_unique_path to uniquely identify
    this task.
    """
    # if the number of rows is greater than size_to_defer,
    # run the task asynchonously. Otherwise, commit immediately.
    # 0 means: always run in a celery task
    size_to_defer = 0

    def get_unique_path(self):
        raise NotImplementedError()

    def save(self, operation_name=None, operating_user=None):
        """
        Save the state of this object to django storage.

        Clients may pass an optional ``operating_user`` kwarg to
        indicate the ``auth.User`` who is saving this operation state.
        Otherwise, the current request's (if any) user will be recorded.
        """
        state = self.__dict__.copy()
        for k in list(state):
            v = state[k]
            if k.startswith('_'):
                del state[k]
            elif isinstance(v, set):
                state[k] = list(v)

        state['__class__'] = (self.__class__.__module__, self.__class__.__name__)

        if not operation_name:
            operation_name = 'stage' if self.can_commit else 'commit'

        operation = CSVOperation.record_operation(
            self,
            self.get_unique_path(),
            operation_name,
            json.dumps(state),
            original_filename=state.get('filename', ''),
            user=operating_user or get_current_user(),
        )
        return operation

    @classmethod
    def load(cls, operation_id, load_subclasses=False):
        """
        Load the CSVProcessor from the saved state.
        """
        operation = CSVOperation.objects.get(pk=operation_id)
        log.info('Loading CSV state %s', operation.data.name)
        state = json.load(operation.data)
        module_name, classname = state.pop('__class__')
        if classname != cls.__name__:
            if not load_subclasses:
                # this could indicate tampering
                raise ValueError("%s != %s" % (classname, cls.__name__))
            cls = getattr(importlib.import_module(module_name), classname)  # pylint: disable=self-cls-assignment
        instance = cls(**state)
        return instance

    @classmethod
    def get_deferred_result(cls, result_id):
        """
        Return the celery result for the given id.
        """
        return AsyncResult(result_id)

    def status(self):
        """
        Return a status dict.
        """
        status = super().status()
        status['result_id'] = getattr(self, 'result_id', None)
        status['saved_error_id'] = getattr(self, 'saved_error_id', None)
        status['waiting'] = bool(status['result_id'])
        status.update(getattr(self, '_status', {}))
        return status

    def preprocess_file(self, reader):
        super().preprocess_file(reader)
        if self.error_messages:
            operation = self.save('error')
            self.saved_error_id = operation.id

    def commit(self, running_task=None):
        """
        Automatically defer the commit to a celery task
        if the number of rows is greater than self.size_to_defer
        """
        if running_task or len(self.stage) <= self.size_to_defer:
            # Either an async task is already in process,
            # or the size of the request is small enough to commit synchronously
            self.save()
            super().commit()
        else:
            # We'll enqueue an async celery task.
            try:
                with transaction.atomic():
                    # We have to make sure that a CSVOperation record
                    # is created and committed before the task starts,
                    # because the task will look for that CSVOperation
                    # in the database outside of the context of the
                    # current transaction.
                    operation = self.save()
            except DatabaseError:
                log.exception('Error saving DeferrableMixin {}'.format(self))
                raise

            # Now enqueue the async task.
            result = do_deferred_commit.delay(operation.id)
            if not result.ready():
                self.result_id = result.id
                log.info('Queued task %s %r', operation.id, result)
            else:
                self._status = result.get()

    def get_committed_history(self):
        """
        Get the history of all committed CSV upload operations.

        Returns a list of dictionaries.
        """
        all_history = CSVOperation.get_all_history(self, self.get_unique_path())
        committed_history = all_history.filter(operation='commit')
        history_with_users = CSVOperationSerializer.get_related_queryset(committed_history).order_by('-created')
        return CSVOperationSerializer(history_with_users, many=True).data
