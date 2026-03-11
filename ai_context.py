"""
AI context for the Segments module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Segments

### Models

**Segment** — A named group of customers defined by rules.
- `name`, `description`
- `color`: 'primary' | 'success' | 'warning' | 'error' | 'neutral'
- `is_active`, `is_dynamic`: Dynamic segments auto-update; static are manually managed
- `customer_count` (cached integer), `last_calculated_at`
- `logic_operator`: 'and' (all rules must match) | 'or' (any rule must match)
- Methods: `calculate_customers()` → queryset, `update_count()` → recalculates and saves count, `get_customer_ids()` → list of UUIDs

**SegmentRule** — One condition within a segment.
- `segment` FK → Segment (related_name='rules')
- `field`: Customer field to filter on — options:
  - 'lifecycle_stage', 'source' (string)
  - 'total_spent', 'total_purchases' (number)
  - 'last_purchase_date', 'created_at' (date)
  - 'city', 'country' (string)
  - 'is_active' (boolean)
  - 'groups' (customer group ID)
  - 'birthday_month' (number, 1-12)
- `operator`: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'greater_equal' | 'less_equal' | 'is_empty' | 'is_not_empty' | 'in_last_days' | 'not_in_last_days'
- `value` (CharField, max 500): The comparison value (empty for is_empty/is_not_empty operators)
- `value_type`: 'string' | 'number' | 'date' | 'boolean'
- `sort_order`
- Method: `to_q_object()` → Django Q object for filtering customers

**SegmentSettings** — Per-hub settings.
- `auto_refresh_minutes` (default 0 = disabled): Interval for automatic count refresh
- `max_segment_size` (default 10000): Cap on segment size

### Key Flows

1. **Create segment**: Create Segment with name and logic_operator → add SegmentRules defining conditions
2. **Calculate members**: `segment.calculate_customers()` → builds Q objects from all rules, combines with AND/OR logic → filters Customer queryset
3. **Refresh count**: `segment.update_count()` → runs calculation and saves `customer_count` + `last_calculated_at`
4. **Use in campaigns**: Get customer IDs with `segment.get_customer_ids()` for targeted campaigns

### Rule Examples
- Customers who spent > 500: field='total_spent', operator='greater_than', value='500', value_type='number'
- Customers from Madrid: field='city', operator='equals', value='Madrid', value_type='string'
- Customers who purchased in last 30 days: field='last_purchase_date', operator='in_last_days', value='30', value_type='date'
- VIP group: field='groups', operator='equals', value='{group_uuid}'

### Relationships
- Segments filter customers from the customers module (customers.Customer)
"""
