"""
Django admin for CSV Operations
"""
from __future__ import absolute_import, unicode_literals, print_function

from django.contrib import admin

from .models import CSVOperation


@admin.register(CSVOperation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'unique_id', 'created')
    readonly_fields = ('created', 'modified')
