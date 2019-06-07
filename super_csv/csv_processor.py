"""
Generic class-based CSV Processor.
"""
from __future__ import absolute_import, unicode_literals, print_function
import csv
import hashlib
import importlib
import json
import logging

from collections import defaultdict

from celery.result import AsyncResult
from django.conf import settings
from django.utils.translation import ugettext as _
from six import text_type

from .models import CSVOperation
from .tasks import do_deferred_commit

log = logging.getLogger(__name__)

__all__ = ('CSVProcessor', 'ChecksumMixin', 'DeferrableMixin', 'ValidationError')


class ResultDict(dict):
    def __init__(self, *args, **kwargs):
        super(ResultDict, self).__init__(*args, **kwargs)
        if 'error' not in self:
            self['error'] = ''
            self['status'] = _('Success')


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class ValidationError(ValueError):
    pass


class CSVProcessor(object):
    """
    Generic CSV processor.

    Create a subclass that implements process_row(row)

    To use:
    processor = MyProcessor(optional_args='foo')
    processor.process_file(open_csv_file)
    result = processor.status()

    If you want to separate validation/processing:
    processor = MyProcessor(optional_args='foo')
    processor.process_file(open_csv_file, autocommit=False)
    # save the state somewhere, or send to another process.
    processor.commit()

    If the subclass saves rows to self.rollback_rows, it's possible to
    rollback the saved items by calling processor.rollback()
    """
    columns = []
    required_columns = []
    max_file_size = 2 * 1024 * 1024

    def __init__(self, **kwargs):
        self.total_rows = 0
        self.processed_rows = 0
        self.saved_rows = 0
        self.stage = []
        self.rollback_rows = []
        self.result_data = []
        self.error_messages = defaultdict(list)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_error(self, message, row=0):
        """
        Add an error message. Does not store duplicates.
        """
        self.error_messages[message].append(row)

    def write_file(self, thefile, rows=None):
        """
        Write the rows to the file.
        """
        for row in self.get_iterator(rows):
            thefile.write(row)

    def get_iterator(self, rows=None, columns=None, error_data=False):
        """
        Export the CSV as an iterator.
        """
        if error_data:
            # return an iterator of the original data with an added error column
            rows = self.result_data
            columns = self.columns + ['status', 'error']
        else:
            rows = rows or self.get_rows_to_export()
            columns = columns or self.columns
        writer = csv.DictWriter(Echo(), columns)
        header = writer.writerow(dict(zip(writer.fieldnames, writer.fieldnames)))
        yield header
        for row in rows:
            self.preprocess_export_row(row)
            yield writer.writerow(row)

    def process_file(self, thefile, autocommit=True):
        """
        Read the file, validating and preprocessing each row.
        If autocommit=False, rows will be staged for writing. Call commit() to finalize.
        If autocommit=True, the staged rows will be committed.
        """
        reader = self.read_file(thefile)
        if reader:
            self.preprocess_file(reader)
            thefile.close()
            if autocommit and self.can_commit:
                self.commit()

    def read_file(self, thefile):
        """
        Create a CSV reader and validate the file.
        Returns the reader.
        """
        try:
            reader = csv.DictReader(thefile)
            self.validate_file(thefile, reader)
            return reader
        except ValidationError as exc:
            self.add_error(text_type(exc))

    def preprocess_file(self, reader):
        """
        Preprocess the rows, saving them to the staging list.
        """
        rownum = processed_rows = 0
        snapshot = []
        failure = _('Failure')
        no_action = _('No Action')
        for rownum, row in enumerate(reader, 1):
            result = ResultDict(row)
            try:
                self.validate_row(row)
                row = self.preprocess_row(row)
                if row:
                    self.stage.append((rownum, row))
                    processed_rows += 1
                else:
                    result['status'] = no_action
            except ValidationError as e:
                self.add_error(text_type(e), rownum)
                result['error'] = text_type(e)
                result['status'] = failure
            snapshot.append(result)
        self.result_data = snapshot
        self.total_rows = rownum
        self.processed_rows = processed_rows

    def validate_file(self, thefile, reader):
        """
        Validate the file.
        Returns bool.
        """
        if hasattr(thefile, 'size') and self.max_file_size and thefile.size > self.max_file_size:
            raise ValidationError(_("The CSV file must be under {} bytes").format(self.max_file_size))
        elif self.required_columns:
            for field in self.required_columns:
                if field not in reader.fieldnames:
                    raise ValidationError(_("Missing column: {}").format(field))

    def validate_row(self, row):
        """
        Validate the fields in the row.
        Raise ValidationError for invalid rows.
        """
        return True

    def preprocess_export_row(self, row):
        """
        Preprocess row just before writing to CSV.
        Returns a row.
        """

    def preprocess_row(self, row):
        """
        Preprocess the row.
        Returns the same row or new row, or None.
        """
        return row

    def get_rows_to_export(self):
        """
        Subclasses should implement this to return rows to export.
        """
        return []

    @property
    def can_commit(self):
        """
        Return whether there's data to commit.
        """
        return bool(self.stage and not self.error_messages)

    def commit(self):
        """
        Commit the processed rows to the database.
        """
        saved = 0
        while self.stage:
            rownum, row = self.stage.pop(0)
            try:
                did_save, rollback_row = self.process_row(row)
                if did_save:
                    saved += 1
                    if rollback_row:
                        self.rollback_rows.append((rownum, rollback_row))
            except Exception as e:
                log.exception('Committing %r', self)
                self.add_error(text_type(e), row=rownum)
                if self.result_data:
                    self.result_data[rownum - 1]['error'] = text_type(e)
                    self.result_data[rownum - 1]['status'] = _('Failure')
        self.saved_rows = saved
        log.info('%r committed %d rows', self, saved)

    def rollback(self):
        """
        Rollback the previously saved rows, by applying each undo row.
        """
        saved = 0
        while self.rollback_rows:
            rownum, row = self.rollback_rows.pop(0)
            try:
                did_save, __ = self.process_row(row)
                if did_save:
                    saved += 1
            except Exception as e:
                log.exception('Rolling back %r', self)
                self.add_error(text_type(e), row=rownum)
        self.saved_rows = saved

    def status(self):
        """
        Return a status dict.
        """
        result = {
            'total': self.total_rows,
            'processed': self.processed_rows,
            'saved': self.saved_rows,
            'error_rows': [row for row in self.result_data if row.get('error')],
            'error_messages': list(self.error_messages.keys()),
            'percentage': format(self.saved_rows / float(self.total_rows or 1), '.1%'),
            'can_commit': self.can_commit,
        }
        return result

    def process_row(self, row):
        """
        Save the row to the database.
        Returns success, undo (dictionary of row to use for rolling back the operation) or None

        At minimun should implement this method.
        """
        return False, None


class ChecksumMixin(object):
    """
    CSV mixin that will create and verify a checksum column in the CSV file
    Specify a list checksum_columns in the subclass.
    """
    secret = settings.SECRET_KEY
    checksum_columns = []
    checksum_fieldname = 'csum'
    checksum_size = 4

    def _get_checksum(self, row):
        to_check = ''.join(text_type(row[key] or '') for key in self.checksum_columns)
        to_check += self.secret
        return hashlib.md5(to_check).hexdigest()[:self.checksum_size]

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
            raise ValidationError(_("Checksum mismatch"))


class DeferrableMixin(object):
    """
    Mixin that automatically commits data using celery.

    Subclasses should specify `size_to_defer` to tune when to
    run the commit synchronously or asynchronously

    Subclasses must override get_unique_path to uniquely identify
    this task
    """
    # if the number of rows is greater than size_to_defer,
    # run the task asynchonously. Otherwise, commit immediately.
    # 0 means: always run in a celery task
    size_to_defer = 0

    def get_unique_path(self):
        raise NotImplementedError()

    def save(self, op_name=None):
        """
        Save the state of this object to django storage.
        """
        state = self.__dict__.copy()
        for k, v in state.items():
            if k.startswith('_'):
                del state[k]
            elif isinstance(v, set):
                state[k] = list(v)
        state['__class__'] = (self.__class__.__module__, self.__class__.__name__)
        if not op_name:
            op_name = 'stage' if self.can_commit else 'commit'
        operation = CSVOperation.record_operation(self, self.get_unique_path(), op_name, json.dumps(state))
        return operation

    @classmethod
    def load(cls, operation_id, load_subclasses=False):
        """
        Load the CSVProcessor from the saved state.
        """
        operation = CSVOperation.objects.get(pk=operation_id)
        log.info('Loading CSV state %s', operation.data.name)
        state = json.loads(operation.data.read())
        module_name, classname = state.pop('__class__')
        if classname != cls.__name__:
            if not load_subclasses:
                # this could indicate tampering
                raise ValueError("%s != %s" % (classname, cls.__name__))
            else:
                cls = getattr(importlib.import_module(module_name), classname)
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
        status = super(DeferrableMixin, self).status()
        status['result_id'] = getattr(self, 'result_id', None)
        status['saved_error_id'] = getattr(self, 'saved_error_id', None)
        status['waiting'] = bool(status['result_id'])
        status.update(getattr(self, '_status', {}))
        return status

    def preprocess_file(self, reader):
        super(DeferrableMixin, self).preprocess_file(reader)
        if self.error_messages:
            operation = self.save('error')
            self.saved_error_id = operation.id

    def commit(self, running_task=None):
        """
        Automatically defer the commit to a celery task
        if the number of rows is greater than self.size_to_defer
        """
        operation = self.save()
        if running_task or len(self.stage) <= self.size_to_defer:
            # called by the async task
            # or small enough to commit now
            super(DeferrableMixin, self).commit()
        else:
            # run asynchronously
            result = do_deferred_commit.delay(operation.id)
            if not result.ready():
                self.result_id = result.id
                log.info('Queued task %s %r', operation.id, result)
            else:
                self._status = result.get()
