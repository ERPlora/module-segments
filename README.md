# Segments

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `segments` |
| **Version** | `1.0.0` |
| **Icon** | `pie-chart-outline` |
| **Dependencies** | `customers` |

## Dependencies

This module requires the following modules to be installed:

- `customers`

## Models

### `Segment`

Segment(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, name, description, color, is_active, is_dynamic, customer_count, last_calculated_at, logic_operator)

| Field | Type | Details |
|-------|------|---------|
| `name` | CharField | max_length=255 |
| `description` | TextField | optional |
| `color` | CharField | max_length=20, choices: primary, success, warning, error, neutral |
| `is_active` | BooleanField |  |
| `is_dynamic` | BooleanField |  |
| `customer_count` | IntegerField |  |
| `last_calculated_at` | DateTimeField | optional |
| `logic_operator` | CharField | max_length=3, choices: and, or |

**Methods:**

- `calculate_customers()` — Apply all rules and return a queryset of matching customers.

Returns an empty queryset if no rules are defined or the
customers module is not available.
- `update_count()` — Recalculate customer count and update the cached field.
- `get_customer_ids()` — Return a list of customer UUIDs matching this segment.

### `SegmentRule`

SegmentRule(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, segment, field, operator, value, value_type, sort_order)

| Field | Type | Details |
|-------|------|---------|
| `segment` | ForeignKey | → `segments.Segment`, on_delete=CASCADE |
| `field` | CharField | max_length=50, choices: lifecycle_stage, source, total_spent, total_purchases, last_purchase_date, city, ... |
| `operator` | CharField | max_length=30, choices: equals, not_equals, contains, not_contains, greater_than, less_than, ... |
| `value` | CharField | max_length=500, optional |
| `value_type` | CharField | max_length=20, choices: string, number, date, boolean |
| `sort_order` | IntegerField |  |

**Methods:**

- `to_q_object()` — Convert this rule into a Django Q object for filtering customers.

Returns None if the rule cannot be converted (e.g., field doesn't exist
on the Customer model).

### `SegmentSettings`

Per-hub settings for the segments module.

| Field | Type | Details |
|-------|------|---------|
| `auto_refresh_minutes` | PositiveIntegerField |  |
| `max_segment_size` | PositiveIntegerField |  |

**Methods:**

- `get_for_hub()` — Get or create settings for a given hub.

## Cross-Module Relationships

| From | Field | To | on_delete | Nullable |
|------|-------|----|-----------|----------|
| `SegmentRule` | `segment` | `segments.Segment` | CASCADE | No |

## URL Endpoints

Base path: `/m/segments/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `list/` | `list` | GET |
| `segments/` | `segments_list` | GET |
| `segments/add/` | `segment_add` | GET/POST |
| `segments/<uuid:pk>/edit/` | `segment_edit` | GET |
| `segments/<uuid:pk>/delete/` | `segment_delete` | GET/POST |
| `segments/<uuid:pk>/toggle/` | `segment_toggle_status` | GET |
| `segments/bulk/` | `segments_bulk_action` | GET/POST |
| `settings/` | `settings` | GET |

## Permissions

| Permission | Description |
|------------|-------------|
| `segments.view_segment` | View Segment |
| `segments.add_segment` | Add Segment |
| `segments.change_segment` | Change Segment |
| `segments.delete_segment` | Delete Segment |
| `segments.export_segment` | Export Segment |
| `segments.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `add_segment`, `change_segment`, `export_segment`, `view_segment`
- **employee**: `add_segment`, `view_segment`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Segments | `pie-chart-outline` | `list` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_segments`

List customer segments.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `is_active` | boolean | No |  |
| `is_dynamic` | boolean | No |  |

### `create_segment`

Create a customer segment with rules.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes |  |
| `description` | string | No |  |
| `color` | string | No |  |
| `is_dynamic` | boolean | No | Auto-update based on rules |
| `logic_operator` | string | No | and/or for combining rules |
| `rules` | array | No |  |

## File Structure

```
README.md
__init__.py
admin.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
migrations/
  0001_initial.py
  __init__.py
models.py
module.py
static/
  segments/
    css/
      segments.css
    js/
templates/
  segments/
    pages/
      detail.html
      index.html
      list.html
      segment_add.html
      segment_edit.html
      segments.html
      settings.html
    partials/
      dashboard_content.html
      detail_content.html
      panel_segment_add.html
      panel_segment_edit.html
      segment_add_content.html
      segment_customers.html
      segment_edit_content.html
      segment_rules.html
      segments_content.html
      segments_list.html
      settings_content.html
tests/
  __init__.py
  conftest.py
  test_models.py
  test_views.py
urls.py
views.py
```
