from django.utils.translation import gettext_lazy as _

MODULE_ID = 'segments'
MODULE_NAME = _('Segments')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'pie-chart-outline'
MODULE_DESCRIPTION = _('Dynamic customer segmentation with rule-based filters')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'marketing'

MENU = {
    'label': _('Segments'),
    'icon': 'pie-chart-outline',
    'order': 55,
}

NAVIGATION = [
    {'label': _('Segments'), 'icon': 'pie-chart-outline', 'id': 'list'},
    {'label': _('Settings'), 'icon': 'settings-outline', 'id': 'settings'},
]

DEPENDENCIES = ['customers']

PERMISSIONS = [
    'segments.view_segment',
    'segments.add_segment',
    'segments.change_segment',
    'segments.delete_segment',
    'segments.export_segment',
    'segments.manage_settings',
]
