# Segments Module

Dynamic customer segmentation with rule-based filters.

## Features

- Create dynamic or static customer segments with configurable rules
- Combine rules using AND (all must match) or OR (any must match) logic operators
- Filter customers by 11 fields: lifecycle stage, source, total spent, total purchases, last purchase date, city, country, active status, created date, customer group, and birthday month
- Support 12 comparison operators: equals, not equals, contains, not contains, greater than, less than, greater/less or equal, is empty, is not empty, in last X days, not in last X days
- Automatic customer count calculation and caching
- Color-coded segments (primary, success, warning, error, neutral)
- Export segment data
- Configurable auto-refresh interval for dynamic segments
- Set maximum segment size limits

## Installation

This module is installed automatically via the ERPlora Marketplace.

**Dependencies**: Requires `customers` module.

## Configuration

Access settings via: **Menu > Segments > Settings**

Configurable options include:

- Auto-refresh interval (minutes, 0 to disable)
- Maximum segment size (customer limit per segment)

## Usage

Access via: **Menu > Segments**

### Views

| View | URL | Description |
|------|-----|-------------|
| Segments | `/m/segments/list/` | List and manage customer segments |
| Settings | `/m/segments/settings/` | Module configuration |

## Models

| Model | Description |
|-------|-------------|
| `Segment` | Customer segment with name, description, color, dynamic/static flag, logic operator, customer count, and calculation timestamp |
| `SegmentRule` | Filter rule for a segment with field, operator, value, value type, and sort order |
| `SegmentSettings` | Per-hub settings for auto-refresh interval and maximum segment size |

## Permissions

| Permission | Description |
|------------|-------------|
| `segments.view_segment` | View segments |
| `segments.add_segment` | Create new segments |
| `segments.change_segment` | Edit existing segments |
| `segments.delete_segment` | Delete segments |
| `segments.export_segment` | Export segment data |
| `segments.manage_settings` | Manage module settings |

## Integration with Other Modules

- **customers**: Segments query the Customer model to dynamically calculate matching customers based on defined rules. The customers module must be installed for segment calculation to function.

## License

MIT

## Author

ERPlora Team - support@erplora.com
