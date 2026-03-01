"""AI tools for the Segments module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListSegments(AssistantTool):
    name = "list_segments"
    description = "List customer segments."
    module_id = "segments"
    required_permission = "segments.view_segment"
    parameters = {
        "type": "object",
        "properties": {"is_active": {"type": "boolean"}, "is_dynamic": {"type": "boolean"}},
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from segments.models import Segment
        qs = Segment.objects.all()
        if 'is_active' in args:
            qs = qs.filter(is_active=args['is_active'])
        if 'is_dynamic' in args:
            qs = qs.filter(is_dynamic=args['is_dynamic'])
        return {"segments": [{"id": str(s.id), "name": s.name, "color": s.color, "is_dynamic": s.is_dynamic, "customer_count": s.customer_count, "is_active": s.is_active} for s in qs]}


@register_tool
class CreateSegment(AssistantTool):
    name = "create_segment"
    description = "Create a customer segment with rules."
    module_id = "segments"
    required_permission = "segments.add_segment"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}, "description": {"type": "string"}, "color": {"type": "string"},
            "is_dynamic": {"type": "boolean", "description": "Auto-update based on rules"},
            "logic_operator": {"type": "string", "description": "and/or for combining rules"},
            "rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string", "description": "lifecycle_stage, source, total_spent, last_purchase_date, city, etc."},
                        "operator": {"type": "string", "description": "equals, greater_than, in_last_days, etc."},
                        "value": {"type": "string"},
                    },
                    "required": ["field", "operator", "value"],
                },
            },
        },
        "required": ["name"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from segments.models import Segment, SegmentRule
        s = Segment.objects.create(
            name=args['name'], description=args.get('description', ''), color=args.get('color', ''),
            is_dynamic=args.get('is_dynamic', False), logic_operator=args.get('logic_operator', 'and'),
        )
        for rule in args.get('rules', []):
            SegmentRule.objects.create(segment=s, field=rule['field'], operator=rule['operator'], value=rule['value'])
        return {"id": str(s.id), "name": s.name, "created": True}
