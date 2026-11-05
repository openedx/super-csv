"""
super_csv Django application initialization.
"""

from django.apps import AppConfig


class SuperCSVConfig(AppConfig):
    """
    Configuration for the super_csv Django application.
    """

    name = 'super_csv'
    plugin_app = {
        'settings_config': {
            'lms.djangoapp': {
                'common': {'relative_path': 'common_settings'},
            },
        },

    }

    def ready(self):
        from . import signals  # pylint: disable=unused-import, import-outside-toplevel
