"""
Generic class-based CSV Processor.
"""

import csv
import logging
from collections import defaultdict
from io import StringIO

from django.utils.translation import ugettext as _

from .exceptions import ValidationError
from .mixins import ChecksumMixin, DeferrableMixin

log = logging.getLogger(__name__)

__all__ = ('CSVProcessor', 'ChecksumMixin', 'DeferrableMixin', 'ValidationError')


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    https://docs.python.org/2/library/csv.html
    """

    def __init__(self, f, dialect=csv.excel, **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f

    def writerow(self, row):
        """
        Write the row
        """
        newrow = []
        for col in row:
            if col is None:
                col = ''
            elif not isinstance(col, str):
                col = str(col)
            newrow.append(col.encode('utf8'))
        self.writer.writerow(newrow)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
        return data

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UnicodeDictWriter(csv.DictWriter):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    # pylint: disable=super-init-not-called, keyword-arg-before-vararg
    def __init__(self, f, fieldnames, restval="", extrasaction="raise",
                 dialect="excel", *args, **kwds):
        self.fieldnames = fieldnames    # list of keys for the dict
        self.restval = restval          # for writing short dicts
        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError("extrasaction (%s) must be 'raise' or 'ignore'" % extrasaction)
        self.extrasaction = extrasaction
        self.writer = UnicodeWriter(f, dialect, *args, **kwds)


class ResultDict(dict):
    """ Resut Dict. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'error' not in self:
            self['error'] = ''
            self['status'] = _('Success')


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def decode_utf8(input_iterator):
    """
    Generator that decodes a utf-8 encoded
    input line by line
    """
    for line in input_iterator:
        yield line if isinstance(line, str) else line.decode('utf-8')


class CSVProcessor:
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
        self.filename = ''  # represents original imported file
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

    def write_file(self, thefile, rows=None, columns=None):
        """
        Write the rows to the file.
        """
        for row in self.get_iterator(rows, columns):
            thefile.write(row)

    def get_iterator(self, rows=None, columns=None, error_data=False):
        """
        Generate row data for writing to an output CSV file.

        Supply rows (dict array) to override output row data.
        Supply columns (string array) to override output columns from processor.
        Set error_data to a truthy value to return error and status info per-row.
        """
        if error_data:
            if columns is None:
                columns = self.columns
            columns = columns + ['status', 'error']
            if rows is None:
                rows = self.result_data
        else:
            if columns is None:
                columns = self.columns
            if rows is None:
                rows = self.get_rows_to_export()

        writer = csv.DictWriter(Echo(), columns, extrasaction="ignore")
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

    # pylint: disable=inconsistent-return-statements
    def read_file(self, thefile):
        """
        Create a CSV reader and validate the file.
        Returns the reader.

        file must be open in binary mode
        """
        try:
            self.filename = getattr(thefile, 'name', '') or ''
            reader = csv.DictReader(decode_utf8(thefile))
            self.validate_file(thefile, reader)
            return reader
        except ValidationError as exc:
            self.add_error(str(exc))

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
                self.add_error(str(e), rownum)
                result['error'] = str(e)
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
        if self.required_columns:
            for field in self.required_columns:
                if field not in reader.fieldnames:
                    raise ValidationError(_("Missing column: {}").format(field))

    # pylint: disable=unused-argument
    def validate_row(self, row):
        """
        Validate the fields in the row.
        Raise ValidationError for invalid rows.
        """
        return True

    # pylint: disable=unused-argument
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
            except Exception as e:  # pylint: disable=broad-except
                log.exception('Committing %r', self)
                self.add_error(str(e), row=rownum)
                if self.result_data:
                    self.result_data[rownum - 1]['error'] = str(e)
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
            except Exception as e:  # pylint: disable=broad-except
                log.exception('Rolling back %r', self)
                self.add_error(str(e), row=rownum)
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
