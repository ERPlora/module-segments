from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SegmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'segments'
    label = 'segments'
    verbose_name = _('Segments')

    def ready(self):
        pass
