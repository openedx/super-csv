"""
Serializers for CSV operation data.
"""
from __future__ import absolute_import, unicode_literals

import json

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CSVOperation


class CSVOperationDataSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Serializer for data in CSV bulk operation summary results info
    """
    total_rows = serializers.IntegerField()
    processed_rows = serializers.IntegerField()
    saved_rows = serializers.IntegerField()


class CSVOperationSerializer(serializers.ModelSerializer):
    """
    Serializer for CSV bulk operations
    """

    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=get_user_model().objects.all()
    )
    data = serializers.SerializerMethodField()

    class Meta:
        model = CSVOperation
        fields = ('id', 'class_name', 'unique_id', 'operation', 'user', 'modified', 'original_filename', 'data')

    @classmethod
    def get_related_queryset(cls, queryset):
        return queryset.select_related('user')

    def get_data(self, operation):
        data = json.load(operation.data)
        return CSVOperationDataSerializer(data).data
