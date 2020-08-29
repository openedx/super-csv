# -*- coding: utf-8 -*-
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
        u'settings_config': {
            u'lms.djangoapp': {
                u'common': {'relative_path': u'common_settings'},
            },
        },

    }

    def ready(self):
        from . import signals  # pylint: disable=unused-import, import-outside-toplevel
