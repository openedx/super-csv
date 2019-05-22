"""
Django admin for CSV Operations
"""
from django.contrib import admin

from .models import CSVOperation

@admin.register(CSVOperation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'unique_id', 'created')
