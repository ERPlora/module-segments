from django.contrib import admin

from .models import Segment, SegmentRule, SegmentSettings


class SegmentRuleInline(admin.TabularInline):
    model = SegmentRule
    extra = 0
    fields = ('field', 'operator', 'value', 'value_type', 'sort_order')
    ordering = ('sort_order',)


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'is_active', 'is_dynamic', 'customer_count', 'logic_operator', 'last_calculated_at', 'created_at')
    list_filter = ('is_active', 'is_dynamic', 'color', 'logic_operator')
    search_fields = ('name', 'description')
    readonly_fields = ('customer_count', 'last_calculated_at')
    inlines = [SegmentRuleInline]


@admin.register(SegmentRule)
class SegmentRuleAdmin(admin.ModelAdmin):
    list_display = ('segment', 'field', 'operator', 'value', 'value_type', 'sort_order')
    list_filter = ('field', 'operator', 'value_type')
    search_fields = ('segment__name', 'value')
    ordering = ('segment', 'sort_order')


@admin.register(SegmentSettings)
class SegmentSettingsAdmin(admin.ModelAdmin):
    list_display = ('hub_id', 'auto_refresh_minutes', 'max_segment_size')
