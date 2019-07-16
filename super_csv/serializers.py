"""
Serializers for CSV operation data.
"""
from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CSVOperation


class CSVOperationSerializer(serializers.ModelSerializer):
    """
    Serializer for history CSV bulk grade operations
    """

    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=get_user_model().objects.all()
    )

    class Meta:
        model = CSVOperation
        fields = ('class_name', 'unique_id', 'operation', 'user', 'modified', 'original_filename')

    @classmethod
    def get_related_queryset(cls, queryset):
        return queryset.select_related('user')
