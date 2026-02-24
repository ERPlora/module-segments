from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Segment, SegmentSettings

class SegmentForm(forms.ModelForm):
    class Meta:
        model = Segment
        fields = ['name', 'description', 'color', 'is_active', 'is_dynamic', 'customer_count', 'last_calculated_at', 'logic_operator']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'color': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'is_dynamic': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'customer_count': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'last_calculated_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'logic_operator': forms.Select(attrs={'class': 'select select-sm w-full'}),
        }

class SegmentSettingsForm(forms.ModelForm):
    class Meta:
        model = SegmentSettings
        fields = ['auto_refresh_minutes', 'max_segment_size']
        widgets = {
            'auto_refresh_minutes': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'max_segment_size': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
        }

