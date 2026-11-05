"""
Common settings for super_csv
"""


def plugin_settings(settings):
    # expire stored CSV data after 90 days
    settings.CSV_EXPIRATION_DAYS = 90
