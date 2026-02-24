from django.contrib import admin

from .models import Segment, SegmentRule

@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'is_active', 'is_dynamic', 'created_at']
    search_fields = ['name', 'description', 'color', 'logic_operator']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SegmentRule)
class SegmentRuleAdmin(admin.ModelAdmin):
    list_display = ['segment', 'field', 'operator', 'value', 'value_type', 'created_at']
    search_fields = ['field', 'operator', 'value', 'value_type']
    readonly_fields = ['created_at', 'updated_at']

