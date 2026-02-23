from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (
    Segment, SegmentRule, SegmentSettings,
    COLOR_CHOICES, LOGIC_OPERATOR_CHOICES,
    FIELD_CHOICES, OPERATOR_CHOICES, VALUE_TYPE_CHOICES,
)


class SegmentForm(forms.ModelForm):
    class Meta:
        model = Segment
        fields = ['name', 'description', 'color', 'is_active', 'is_dynamic', 'logic_operator']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Segment name'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 2,
                'placeholder': _('Describe what this segment represents...'),
            }),
            'color': forms.Select(attrs={
                'class': 'select',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'is_dynamic': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'logic_operator': forms.Select(attrs={
                'class': 'select',
            }),
        }


class SegmentRuleForm(forms.ModelForm):
    class Meta:
        model = SegmentRule
        fields = ['field', 'operator', 'value', 'value_type', 'sort_order']
        widgets = {
            'field': forms.Select(attrs={
                'class': 'select',
            }),
            'operator': forms.Select(attrs={
                'class': 'select',
            }),
            'value': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Value'),
            }),
            'value_type': forms.Select(attrs={
                'class': 'select',
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': '0',
            }),
        }


class SegmentSettingsForm(forms.ModelForm):
    class Meta:
        model = SegmentSettings
        fields = ['auto_refresh_minutes', 'max_segment_size']
        widgets = {
            'auto_refresh_minutes': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': '0',
            }),
            'max_segment_size': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': '10000',
            }),
        }
