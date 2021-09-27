#!/usr/bin/env python
"""
Tests for the `super-csv` mixins module.
"""

import json

from django.test import TestCase

from super_csv.serializers import CSVOperation, CSVOperationSerializer


class SerializerTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.data = {
            "total_rows": 3,
            "processed_rows": 4,
            "saved_rows": 5
        }

        self.operation = CSVOperation.record_operation('some_name', 'course_id', 'save', json.dumps(self.data))

    def tearDown(self):
        super().tearDown()
        CSVOperation.expire_data(-1)

    def test_get_data_success(self):
        # Test success get total_rows
        operation_serializer = CSVOperationSerializer(self.operation)
        data = operation_serializer.data

        operation_data = data['data']

        self.assertDictEqual(operation_data, self.data)
        self.assertNotIn('error_message', operation_data)

    def test_get_data_fail(self):
        # test error
        CSVOperation.expire_data(-1)
        operation_serializer = CSVOperationSerializer(self.operation)
        data = operation_serializer.data

        operation_data = data['data']

        self.assertEqual(operation_data['total_rows'], 0)
        self.assertEqual(operation_data['processed_rows'], 0)
        self.assertEqual(operation_data['saved_rows'], 0)
        self.assertIn('error_message', operation_data)
