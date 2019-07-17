"""
Tests for CSVProcessor
"""
from __future__ import absolute_import, print_function, unicode_literals

import io

import ddt
# could use BytesIO, but this adds a size attribute
from django.core.files.base import ContentFile
from django.test import TestCase

from super_csv import csv_processor, models


class DummyProcessor(csv_processor.CSVProcessor):
    max_file_size = 20
    columns = ['foo', 'bar']
    required_columns = ['foo', 'bar']

    def get_rows_to_export(self):
        for row in super(DummyProcessor, self).get_rows_to_export():
            yield row
        yield {'foo': 1, 'bar': 1}
        yield {'foo': 2, 'bar': 2}

    def validate_row(self, row):
        super(DummyProcessor, self).validate_row(row)
        if row['foo'] == '3':
            raise csv_processor.ValidationError("3 not allowed")

    def process_row(self, row):
        if row['foo'] == '4':
            raise ValueError('4 is not allowed')
        undo = row.copy()
        undo['undo'] = True
        if row['foo'] == '2':
            undo['foo'] = '4'
        return True, undo


class DummyChecksumProcessor(csv_processor.ChecksumMixin, DummyProcessor):
    checksum_columns = ['foo', 'bar']


class DummyDeferrableProcessor(csv_processor.DeferrableMixin, DummyProcessor):
    size_to_defer = 1

    def get_unique_path(self):
        return 'test'


@ddt.ddt
class CSVTestCase(TestCase):
    def setUp(self):
        super(CSVTestCase, self).setUp()
        self.dummy_csv = 'foo,bar\r\n1,1\r\n2,2\r\n'

    def tearDown(self):
        super(CSVTestCase, self).tearDown()
        models.CSVOperation.objects.all().delete()

    def test_write(self):
        buf = io.StringIO()
        processor = DummyProcessor(dummy_arg=True)
        assert processor.dummy_arg is True
        processor.write_file(buf)
        data = buf.getvalue()
        assert data == self.dummy_csv

    def test_read(self):
        buf = ContentFile(self.dummy_csv)
        processor = DummyProcessor()
        processor.process_file(buf)
        status = processor.status()
        assert status['saved'] == 2
        assert status['processed'] == 2

    @ddt.data(
        ('foo,baz\r\n', 0, 'Missing column: bar'),
        ('foo,bar\r\n1,2\r\n3,3\r\n', 1, None),
        ('foo,bar\r\n1,2\r\n4,4\r\n', 0, '4 is not allowed'),
        ('foo,bar\r\n1,2\r\n4,4\r\n5,5\r\n', 0, 'The CSV file must be under 20 bytes'),
    )
    @ddt.unpack
    def test_file_errors(self, contents, error_rows, message):
        processor = DummyProcessor()
        processor.process_file(ContentFile(contents))
        status = processor.status()
        if error_rows:
            assert len(status["error_rows"]) == error_rows
        if message:
            assert status["error_messages"][0] == message

    def test_checksum(self):
        processor = DummyChecksumProcessor()
        row = {
            'foo': 1,
            'bar': 'hello',
        }
        processor.preprocess_export_row(row)
        assert row['csum'] == '"cfb0"'
        assert processor.validate_row(row) is None
        row['csum'] = '"def"'
        with self.assertRaises(csv_processor.ValidationError):
            processor.validate_row(row)

    def test_checksum_zero(self):
        processor = DummyChecksumProcessor()
        row = {
            'foo': 0,
            'bar': None,
        }
        processor.preprocess_export_row(row)
        assert row['csum'] == '"fc43"'
        assert processor.validate_row(row) is None
        equiv_row = {
            'foo': '0',
            'bar': '',
            'csum': '"fc43"'
        }
        assert processor.validate_row(equiv_row) is None

    def test_rollback(self):
        processor = DummyProcessor()
        processor.process_file(ContentFile(self.dummy_csv))
        assert processor.status()['saved'] == 2
        processor.rollback()
        status = processor.status()
        assert status['saved'] == 1
        assert status['error_messages'][0] == '4 is not allowed'

    def test_defer(self):
        processor = DummyDeferrableProcessor()
        processor.test_set = set((1, 2, 3))
        processor.process_file(ContentFile(self.dummy_csv))
        status = processor.status()
        assert status['saved'] == 2

    def test_defer_too_small(self):
        processor = DummyDeferrableProcessor()
        processor.process_file(ContentFile('foo,bar\r\n1,2\r\n'))
        status = processor.status()
        assert not status['waiting']
        operation = models.CSVOperation.get_latest(processor, processor.get_unique_path())
        assert operation is not None
