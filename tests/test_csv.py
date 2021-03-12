"""
Tests for CSVProcessor
"""

import io
from unittest import mock

import ddt
from django.contrib.auth import get_user_model
# could use BytesIO, but this adds a size attribute
from django.core.files.base import ContentFile
from django.test import TestCase

from super_csv import csv_processor, models


class DummyProcessor(csv_processor.CSVProcessor):
    """
    Fixture class the inherits from CSVProcessor.
    """
    max_file_size = 20
    columns = ['foo', 'bar']
    required_columns = ['foo', 'bar']

    def get_rows_to_export(self):
        yield from super().get_rows_to_export()
        yield {'foo': 1, 'bar': 1}
        yield {'foo': 2, 'bar': 2}

    def validate_row(self, row):
        super().validate_row(row)
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
    columns = ['foo', 'bar', 'csum']


class DummyDeferrableProcessor(csv_processor.DeferrableMixin, DummyProcessor):
    size_to_defer = 1
    test_set = set()

    def get_unique_path(self):
        return 'test'


USERNAME_FROM_SUBCLASS = 'user_specified_by_client'


class DummyDeferrableProcessorSavingUser(csv_processor.DeferrableMixin, DummyProcessor):
    """
    Fixture that inherits from DeferrableMixin and overrides a save() method,
    which calls the parent save() method with a non-null ``operating_user`` kwarg.
    """
    size_to_defer = 1

    def save(self, operation_name=None, operating_user=None):
        user = get_user_model().objects.get(username=USERNAME_FROM_SUBCLASS)
        return super().save(
            operation_name=operation_name,
            operating_user=user,
        )

    def get_unique_path(self):
        return 'test'


@ddt.ddt
class CSVTestCase(TestCase):
    """
    Test class for CSVProcessor and DeferrableMixin classes.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.dummy_csv = 'foo,bar\r\n1,1\r\n2,2\r\n'
        cls.user = get_user_model().objects.create_user(username='testuser', password='12345')
        cls.user_from_subclass = get_user_model().objects.create(username=USERNAME_FROM_SUBCLASS, password='12345')

    def tearDown(self):
        super().tearDown()
        models.CSVOperation.objects.all().delete()

    def test_write(self):
        buf = io.StringIO()
        processor = DummyProcessor(dummy_arg=True)
        assert processor.dummy_arg is True  # pylint: disable=no-member
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

    def test_write_read(self):
        buf = io.StringIO()
        processor = DummyChecksumProcessor()
        processor.write_file(buf)
        buf.seek(0)
        processor.process_file(buf)
        status = processor.status()
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

    def test_write_column_overrides(self):
        # Given existing data to write
        processor = DummyProcessor()
        processor.process_file(self.dummy_csv)

        # When I restrict the columns with the "columns" kwarg
        output_buf = io.StringIO()
        processor.write_file(output_buf, columns=['foo'])

        # Then only the filtered columns appear in the output
        data = output_buf.getvalue()
        assert data == 'foo\r\n1\r\n2\r\n'

    def test_write_row_overrides(self):
        # Given existing data to write
        processor = DummyProcessor()
        processor.process_file(self.dummy_csv)

        # When I override the rows with the "rows" kwarg
        output_buf = io.StringIO()
        rows = [
            {'foo': 'a', 'bar': 'b'},
            {'foo': 'c', 'bar': 'd'}
        ]
        processor.write_file(output_buf, rows=rows)

        # Then the modified rows end up in the exported data
        data = output_buf.getvalue()
        assert data == 'foo,bar\r\na,b\r\nc,d\r\n'

    def test_get_iterator_error_data(self):
        # Given a request for error data
        processor = DummyProcessor()
        processor.result_data = [
            {'foo': 'a', 'bar': 'b', 'status': 'Success', 'error': ''},
            {'foo': 'c', 'bar': 'd', 'status': 'Failure', 'error': 'Error'}
        ]

        # When I get data from the iterator
        iterator = processor.get_iterator(error_data='1')

        # Extra error data is returned in the output file
        output = [row.strip() for row in iterator]
        assert output == [
            'foo,bar,status,error',
            'a,b,Success,',
            'c,d,Failure,Error'
        ]

    def test_get_iterator_error_column_override(self):
        # Given a request for error data with input column overrides
        processor = DummyProcessor()
        processor.result_data = [
            {'foo': 'a', 'bar': 'b', 'status': 'Success', 'error': ''},
            {'foo': 'c', 'bar': 'd', 'status': 'Failure', 'error': 'Error'}
        ]

        # When I get data from the iterator
        iterator = processor.get_iterator(error_data='1', columns=['bar'])

        # Then columns are filtered before adding error data
        output = [row.strip() for row in iterator]
        assert output == [
            'bar,status,error',
            'b,Success,',
            'd,Failure,Error'
        ]

    def test_checksum(self):
        processor = DummyChecksumProcessor()
        row = {
            'foo': 1,
            'bar': 'hello',
        }
        processor.preprocess_export_row(row)
        assert row['csum'] == '@cfb0'
        assert processor.validate_row(row) is None
        row['csum'] = '@def'
        with self.assertRaises(csv_processor.ValidationError):
            processor.validate_row(row)

    def test_checksum_zero(self):
        processor = DummyChecksumProcessor()
        row = {
            'foo': 0,
            'bar': None,
        }
        processor.preprocess_export_row(row)
        assert row['csum'] == '@fc43'
        assert processor.validate_row(row) is None
        equiv_row = {
            'foo': '0',
            'bar': '',
            'csum': '@fc43'
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
        processor.test_set = {1, 2, 3}
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

    @mock.patch('super_csv.mixins.get_current_user')
    def test_operating_user_is_recorded_from_request(self, patch_get_user):
        processor = DummyDeferrableProcessor()
        patch_get_user.return_value = self.user
        processor.process_file(ContentFile(self.dummy_csv))
        csv_operations = models.CSVOperation.objects.all()
        assert len(csv_operations) == 3
        for csv_operation in csv_operations:
            assert csv_operation.user == self.user

    @mock.patch('super_csv.mixins.get_current_user', return_value=None)
    def test_operating_user_is_recorded_by_subclass(self, patch_get_user):  # pylint: disable=unused-argument
        processor = DummyDeferrableProcessorSavingUser()
        processor.process_file(ContentFile(self.dummy_csv))
        csv_operations = models.CSVOperation.objects.all()
        assert len(csv_operations) == 3
        for csv_operation in csv_operations:
            assert csv_operation.user == self.user_from_subclass
