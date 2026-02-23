import logging
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import HubBaseModel

logger = logging.getLogger(__name__)


# ============================================================================
# Choices
# ============================================================================

COLOR_CHOICES = [
    ('primary', _('Primary')),
    ('success', _('Success')),
    ('warning', _('Warning')),
    ('error', _('Error')),
    ('neutral', _('Neutral')),
]

LOGIC_OPERATOR_CHOICES = [
    ('and', _('All rules must match (AND)')),
    ('or', _('Any rule must match (OR)')),
]

FIELD_CHOICES = [
    ('lifecycle_stage', _('Lifecycle Stage')),
    ('source', _('Source')),
    ('total_spent', _('Total Spent')),
    ('total_purchases', _('Total Purchases')),
    ('last_purchase_date', _('Last Purchase Date')),
    ('city', _('City')),
    ('country', _('Country')),
    ('is_active', _('Is Active')),
    ('created_at', _('Created Date')),
    ('groups', _('Customer Group')),
    ('birthday_month', _('Birthday Month')),
]

OPERATOR_CHOICES = [
    ('equals', _('Equals')),
    ('not_equals', _('Does Not Equal')),
    ('contains', _('Contains')),
    ('not_contains', _('Does Not Contain')),
    ('greater_than', _('Greater Than')),
    ('less_than', _('Less Than')),
    ('greater_equal', _('Greater or Equal')),
    ('less_equal', _('Less or Equal')),
    ('is_empty', _('Is Empty')),
    ('is_not_empty', _('Is Not Empty')),
    ('in_last_days', _('In Last X Days')),
    ('not_in_last_days', _('Not In Last X Days')),
]

VALUE_TYPE_CHOICES = [
    ('string', _('Text')),
    ('number', _('Number')),
    ('date', _('Date')),
    ('boolean', _('Boolean')),
]

# Operators that do not require a value
NO_VALUE_OPERATORS = ('is_empty', 'is_not_empty')

# Mapping of fields to their expected value types
FIELD_VALUE_TYPES = {
    'lifecycle_stage': 'string',
    'source': 'string',
    'total_spent': 'number',
    'total_purchases': 'number',
    'last_purchase_date': 'date',
    'city': 'string',
    'country': 'string',
    'is_active': 'boolean',
    'created_at': 'date',
    'groups': 'string',
    'birthday_month': 'number',
}


# ============================================================================
# Segment
# ============================================================================

class Segment(HubBaseModel):
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
    )
    color = models.CharField(
        max_length=20,
        default='primary',
        choices=COLOR_CHOICES,
        verbose_name=_('Color'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
    )
    is_dynamic = models.BooleanField(
        default=True,
        verbose_name=_('Dynamic'),
        help_text=_('Dynamic segments auto-update when rules change. Static segments are manually managed.'),
    )
    customer_count = models.IntegerField(
        default=0,
        verbose_name=_('Customer Count'),
    )
    last_calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Calculated'),
    )
    logic_operator = models.CharField(
        max_length=3,
        default='and',
        choices=LOGIC_OPERATOR_CHOICES,
        verbose_name=_('Logic Operator'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'segments_segment'
        ordering = ['name']
        verbose_name = _('Segment')
        verbose_name_plural = _('Segments')

    def __str__(self):
        return self.name

    def calculate_customers(self):
        """
        Apply all rules and return a queryset of matching customers.

        Returns an empty queryset if no rules are defined or the
        customers module is not available.
        """
        try:
            from customers.models import Customer
        except ImportError:
            logger.warning("Customers module not available for segment calculation")
            return self._empty_customer_qs()

        qs = Customer.objects.filter(hub_id=self.hub_id, is_deleted=False)

        rules = self.rules.filter(is_deleted=False).order_by('sort_order')
        if not rules.exists():
            return qs.none()

        filters = []
        for rule in rules:
            try:
                q = rule.to_q_object()
                if q is not None:
                    filters.append(q)
            except Exception:
                logger.exception(
                    "Error building Q object for rule %s (field=%s, operator=%s)",
                    rule.id, rule.field, rule.operator,
                )
                continue

        if not filters:
            return qs.none()

        if self.logic_operator == 'and':
            combined = filters[0]
            for f in filters[1:]:
                combined &= f
        else:
            combined = filters[0]
            for f in filters[1:]:
                combined |= f

        return qs.filter(combined)

    def update_count(self):
        """Recalculate customer count and update the cached field."""
        try:
            count = self.calculate_customers().count()
        except Exception:
            logger.exception("Error calculating customer count for segment %s", self.id)
            count = 0

        self.customer_count = count
        self.last_calculated_at = timezone.now()
        self.save(update_fields=['customer_count', 'last_calculated_at', 'updated_at'])
        return count

    def get_customer_ids(self):
        """Return a list of customer UUIDs matching this segment."""
        return list(self.calculate_customers().values_list('id', flat=True))

    def _empty_customer_qs(self):
        """Return an empty Customer queryset safely."""
        try:
            from customers.models import Customer
            return Customer.objects.none()
        except ImportError:
            return None


# ============================================================================
# Segment Rule
# ============================================================================

class SegmentRule(HubBaseModel):
    segment = models.ForeignKey(
        Segment,
        on_delete=models.CASCADE,
        related_name='rules',
        verbose_name=_('Segment'),
    )
    field = models.CharField(
        max_length=50,
        choices=FIELD_CHOICES,
        verbose_name=_('Field'),
    )
    operator = models.CharField(
        max_length=30,
        choices=OPERATOR_CHOICES,
        verbose_name=_('Operator'),
    )
    value = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Value'),
    )
    value_type = models.CharField(
        max_length=20,
        default='string',
        choices=VALUE_TYPE_CHOICES,
        verbose_name=_('Value Type'),
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name=_('Sort Order'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'segments_segmentrule'
        ordering = ['sort_order', 'created_at']
        verbose_name = _('Segment Rule')
        verbose_name_plural = _('Segment Rules')

    def __str__(self):
        return f"{self.get_field_display()} {self.get_operator_display()} {self.value}"

    def to_q_object(self):
        """
        Convert this rule into a Django Q object for filtering customers.

        Returns None if the rule cannot be converted (e.g., field doesn't exist
        on the Customer model).
        """
        field = self.field
        op = self.operator
        val = self.value

        # Validate that the target field exists on the Customer model
        if not self._field_exists(field):
            logger.debug("Field '%s' does not exist on Customer model, skipping rule", field)
            return None

        # Operators that don't need a value
        if op == 'is_empty':
            return self._build_empty_q(field, empty=True)
        elif op == 'is_not_empty':
            return self._build_empty_q(field, empty=False)

        # All other operators need a value
        if not val and val != '0':
            return None

        if op == 'equals':
            return self._build_equals_q(field, val)
        elif op == 'not_equals':
            return ~self._build_equals_q(field, val)
        elif op == 'contains':
            return Q(**{f'{field}__icontains': val})
        elif op == 'not_contains':
            return ~Q(**{f'{field}__icontains': val})
        elif op == 'greater_than':
            numeric_val = self._cast_numeric(val)
            if numeric_val is None:
                return None
            return Q(**{f'{field}__gt': numeric_val})
        elif op == 'less_than':
            numeric_val = self._cast_numeric(val)
            if numeric_val is None:
                return None
            return Q(**{f'{field}__lt': numeric_val})
        elif op == 'greater_equal':
            numeric_val = self._cast_numeric(val)
            if numeric_val is None:
                return None
            return Q(**{f'{field}__gte': numeric_val})
        elif op == 'less_equal':
            numeric_val = self._cast_numeric(val)
            if numeric_val is None:
                return None
            return Q(**{f'{field}__lte': numeric_val})
        elif op == 'in_last_days':
            return self._build_in_last_days_q(field, val)
        elif op == 'not_in_last_days':
            q = self._build_in_last_days_q(field, val)
            if q is None:
                return None
            return ~q

        return None

    # --- Private helpers ---

    def _field_exists(self, field_name):
        """Check if the field exists on the Customer model."""
        try:
            from customers.models import Customer
            # Handle special fields
            if field_name == 'groups':
                return True
            if field_name == 'birthday_month':
                # Check if birthday field exists
                try:
                    Customer._meta.get_field('birthday')
                    return True
                except Exception:
                    return False
            Customer._meta.get_field(field_name)
            return True
        except Exception:
            return False

    def _build_equals_q(self, field, val):
        """Build an equals Q object, handling special field types."""
        if field == 'is_active':
            bool_val = val.lower() in ('true', '1', 'yes', 'on')
            return Q(is_active=bool_val)
        elif field == 'groups':
            return Q(groups__id=val)
        elif field == 'birthday_month':
            try:
                month = int(val)
                return Q(birthday__month=month)
            except (ValueError, TypeError):
                return Q()
        return Q(**{field: val})

    def _build_empty_q(self, field, empty=True):
        """Build a Q for checking if a field is empty or not."""
        if field == 'groups':
            if empty:
                return Q(groups__isnull=True)
            else:
                return Q(groups__isnull=False)
        elif field == 'is_active':
            # Boolean fields are never really 'empty'
            if empty:
                return Q(is_active=False)
            else:
                return Q(is_active=True)
        elif field == 'birthday_month':
            if empty:
                return Q(birthday__isnull=True)
            else:
                return Q(birthday__isnull=False)

        # For string/text fields, check both null and empty string
        if empty:
            return Q(**{f'{field}__isnull': True}) | Q(**{field: ''})
        else:
            return ~Q(**{f'{field}__isnull': True}) & ~Q(**{field: ''})

    def _build_in_last_days_q(self, field, val):
        """Build a Q for 'in last X days' comparison."""
        try:
            days = int(val)
        except (ValueError, TypeError):
            return None
        cutoff = timezone.now() - timedelta(days=days)
        return Q(**{f'{field}__gte': cutoff})

    @staticmethod
    def _cast_numeric(val):
        """Cast a string value to Decimal. Returns None on failure."""
        try:
            return Decimal(str(val))
        except (InvalidOperation, ValueError, TypeError):
            return None


# ============================================================================
# Segment Settings
# ============================================================================

class SegmentSettings(HubBaseModel):
    """Per-hub settings for the segments module."""
    auto_refresh_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Auto-refresh Interval (minutes)'),
        help_text=_('Set to 0 to disable automatic refresh. Segments will only refresh on demand.'),
    )
    max_segment_size = models.PositiveIntegerField(
        default=10000,
        verbose_name=_('Max Segment Size'),
        help_text=_('Maximum number of customers per segment. 0 for unlimited.'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'segments_settings'
        verbose_name = _('Segment Settings')
        verbose_name_plural = _('Segment Settings')

    def __str__(self):
        return f"Segment Settings ({self.hub_id})"

    @classmethod
    def get_for_hub(cls, hub_id):
        """Get or create settings for a given hub."""
        settings, _ = cls.objects.get_or_create(
            hub_id=hub_id,
            is_deleted=False,
            defaults={
                'auto_refresh_minutes': 0,
                'max_segment_size': 10000,
            }
        )
        return settings
