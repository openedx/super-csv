#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the `super-csv` models module.
"""

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.test import TestCase
from mock import patch

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
        assert operation.data.name is ''
