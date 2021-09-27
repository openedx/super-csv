"""
Serializers for CSV operation data.
"""

import logging

import simplejson as json
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import serializers

from .models import CSVOperation

logger = logging.getLogger(__name__)


class CSVOperationDataSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Serializer for data in CSV bulk operation summary results info
    """
    total_rows = serializers.IntegerField()
    processed_rows = serializers.IntegerField()
    saved_rows = serializers.IntegerField()
    error_message = serializers.CharField(required=False)


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
        """
        Get data
        """
        try:
            data = json.load(operation.data)
        except (FileNotFoundError, ValueError):
            msg = _('Failed to retrieve file.')

            logger.error(
                'Failed to retrieve operation data for operation %s course %s',
                operation.id,
                operation.unique_id
            )
            data = {
                "total_rows": 0,
                "processed_rows": 0,
                "saved_rows": 0,
                "error_message": msg
            }
        finally:
            result = CSVOperationDataSerializer(data).data
        return result
