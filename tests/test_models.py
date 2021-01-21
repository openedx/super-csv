#!/usr/bin/env python
"""
Tests for the `super-csv` models module.
"""

from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from super_csv.models import CSVOperation


class TestModel(TestCase):
    def test_expire_data(self):
        operation = CSVOperation.record_operation('test', 1, 'save', "some data")
        operation_id = operation.id
        with patch.object(settings, 'CSV_EXPIRATION_DAYS', -10):
            operation.operation = 'test save'
            operation.id = 3
            operation.save()
        operation = CSVOperation.objects.get(pk=operation_id)
        assert operation.data.name == ''
