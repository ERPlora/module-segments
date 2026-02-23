"""
Segments Module Views

Dynamic customer segmentation with rule-based filters.
List, create, edit, delete segments. Add/edit/remove rules. Export matching customers.
"""
import csv
import logging

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render as django_render
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.accounts.decorators import login_required
from apps.core.htmx import htmx_view
from apps.modules_runtime.navigation import with_module_nav

from .models import (
    Segment, SegmentRule, SegmentSettings,
    FIELD_CHOICES, OPERATOR_CHOICES, VALUE_TYPE_CHOICES,
    FIELD_VALUE_TYPES, NO_VALUE_OPERATORS,
)

logger = logging.getLogger(__name__)

PER_PAGE_CHOICES = [10, 25, 50, 100]


def _hub_id(request):
    return request.session.get('hub_id')


def _render_segments_list(request, hub_id):
    """Re-render the segments list partial after a mutation."""
    segments = Segment.objects.filter(hub_id=hub_id, is_deleted=False).order_by('name')
    return django_render(request, 'segments/partials/segments_list.html', {
        'segments': segments,
        'search_query': '',
    })


def _render_segment_detail(request, segment):
    """Re-render the detail content partial after a mutation."""
    rules = segment.rules.filter(is_deleted=False).order_by('sort_order', 'created_at')
    customers_qs = segment.calculate_customers()
    paginator = Paginator(customers_qs, 25)
    page_obj = paginator.get_page(1)

    return django_render(request, 'segments/partials/detail_content.html', {
        'segment': segment,
        'rules': rules,
        'customers': page_obj,
        'page_obj': page_obj,
        'field_choices': FIELD_CHOICES,
        'operator_choices': OPERATOR_CHOICES,
        'value_type_choices': VALUE_TYPE_CHOICES,
        'field_value_types_json': FIELD_VALUE_TYPES,
        'no_value_operators': NO_VALUE_OPERATORS,
    })


# ============================================================================
# Segment List
# ============================================================================

@login_required
@with_module_nav('segments', 'list')
@htmx_view('segments/pages/list.html', 'segments/partials/segments_content.html')
def segment_list(request):
    """Segments list with search."""
    hub = _hub_id(request)
    search_query = request.GET.get('q', '').strip()

    segments = Segment.objects.filter(hub_id=hub, is_deleted=False)

    if search_query:
        segments = segments.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    segments = segments.order_by('name')

    context = {
        'segments': segments,
        'search_query': search_query,
    }

    # HTMX partial: swap only the list area
    if request.htmx and request.htmx.target == 'segments-list-body':
        return django_render(request, 'segments/partials/segments_list.html', context)

    return context


# ============================================================================
# Segment CRUD
# ============================================================================

@login_required
def segment_add(request):
    """Add a new segment via side panel."""
    hub = _hub_id(request)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, _('Name is required'))
            return django_render(request, 'segments/partials/panel_segment_add.html')

        segment = Segment.objects.create(
            hub_id=hub,
            name=name,
            description=request.POST.get('description', '').strip(),
            color=request.POST.get('color', 'primary'),
            is_active=request.POST.get('is_active', 'on') == 'on',
            is_dynamic=request.POST.get('is_dynamic', 'on') == 'on',
            logic_operator=request.POST.get('logic_operator', 'and'),
        )

        messages.success(request, _('Segment "%(name)s" created successfully') % {'name': segment.name})
        return _render_segments_list(request, hub)

    return django_render(request, 'segments/partials/panel_segment_add.html')


@login_required
def segment_edit(request, segment_id):
    """Edit segment via side panel."""
    hub = _hub_id(request)
    segment = get_object_or_404(Segment, id=segment_id, hub_id=hub, is_deleted=False)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, _('Name is required'))
            return django_render(request, 'segments/partials/panel_segment_edit.html', {
                'segment': segment,
            })

        segment.name = name
        segment.description = request.POST.get('description', '').strip()
        segment.color = request.POST.get('color', 'primary')
        segment.is_active = request.POST.get('is_active') == 'on'
        segment.is_dynamic = request.POST.get('is_dynamic') == 'on'
        segment.logic_operator = request.POST.get('logic_operator', 'and')
        segment.save()

        messages.success(request, _('Segment updated successfully'))

        # If coming from the detail page, re-render detail
        referer_target = request.headers.get('HX-Target', '')
        if referer_target == 'segment-detail-area':
            return _render_segment_detail(request, segment)

        return _render_segments_list(request, hub)

    return django_render(request, 'segments/partials/panel_segment_edit.html', {
        'segment': segment,
    })


@login_required
@require_POST
def segment_delete(request, segment_id):
    """Soft delete a segment."""
    hub = _hub_id(request)
    segment = get_object_or_404(Segment, id=segment_id, hub_id=hub, is_deleted=False)
    segment.is_deleted = True
    segment.deleted_at = timezone.now()
    segment.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    # Also soft-delete all rules
    segment.rules.filter(is_deleted=False).update(
        is_deleted=True,
        deleted_at=timezone.now(),
    )

    messages.success(request, _('Segment "%(name)s" deleted successfully') % {'name': segment.name})
    return _render_segments_list(request, hub)


# ============================================================================
# Segment Detail
# ============================================================================

@login_required
@with_module_nav('segments', 'list')
@htmx_view('segments/pages/detail.html', 'segments/partials/detail_content.html')
def segment_detail(request, segment_id):
    """Segment detail with rules and matching customers."""
    hub = _hub_id(request)
    segment = get_object_or_404(Segment, id=segment_id, hub_id=hub, is_deleted=False)

    rules = segment.rules.filter(is_deleted=False).order_by('sort_order', 'created_at')

    # Get matching customers with pagination
    page_num = request.GET.get('page', 1)
    customers_qs = segment.calculate_customers()

    paginator = Paginator(customers_qs, 25)
    page_obj = paginator.get_page(page_num)

    # HTMX partial: swap only the customers section
    if request.htmx and request.htmx.target == 'segment-customers-body':
        return django_render(request, 'segments/partials/segment_customers.html', {
            'segment': segment,
            'customers': page_obj,
            'page_obj': page_obj,
        })

    return {
        'segment': segment,
        'rules': rules,
        'customers': page_obj,
        'page_obj': page_obj,
        'field_choices': FIELD_CHOICES,
        'operator_choices': OPERATOR_CHOICES,
        'value_type_choices': VALUE_TYPE_CHOICES,
        'field_value_types_json': FIELD_VALUE_TYPES,
        'no_value_operators': NO_VALUE_OPERATORS,
    }


# ============================================================================
# Segment Actions
# ============================================================================

@login_required
@require_POST
def segment_refresh(request, segment_id):
    """Recalculate customer count for a segment."""
    hub = _hub_id(request)
    segment = get_object_or_404(Segment, id=segment_id, hub_id=hub, is_deleted=False)
    count = segment.update_count()
    messages.success(request, _('Segment refreshed: %(count)d customers matched') % {'count': count})

    # If the request targets the detail area, re-render detail
    target = request.headers.get('HX-Target', '')
    if target == 'segment-detail-area':
        return _render_segment_detail(request, segment)

    return _render_segments_list(request, hub)


@login_required
def segment_export(request, segment_id):
    """Export matching customers as CSV."""
    hub = _hub_id(request)
    segment = get_object_or_404(Segment, id=segment_id, hub_id=hub, is_deleted=False)

    customers = segment.calculate_customers()
    if customers is None:
        messages.error(request, _('Could not export: customers module not available'))
        return _render_segments_list(request, hub)

    response = HttpResponse(content_type='text/csv')
    filename = f'segment_{segment.name.lower().replace(" ", "_")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        str(_('Name')),
        str(_('Email')),
        str(_('Phone')),
        str(_('City')),
        str(_('Country')),
        str(_('Total Purchases')),
        str(_('Total Spent')),
        str(_('Status')),
        str(_('Created Date')),
    ])

    for customer in customers:
        writer.writerow([
            customer.name,
            customer.email,
            customer.phone,
            getattr(customer, 'city', ''),
            getattr(customer, 'country', ''),
            getattr(customer, 'total_purchases', 0),
            float(getattr(customer, 'total_spent', 0)),
            str(_('Active')) if customer.is_active else str(_('Inactive')),
            customer.created_at.strftime('%Y-%m-%d') if customer.created_at else '',
        ])

    return response


# ============================================================================
# Rules CRUD
# ============================================================================

@login_required
def rule_add(request, segment_id):
    """Add a rule to a segment."""
    hub = _hub_id(request)
    segment = get_object_or_404(Segment, id=segment_id, hub_id=hub, is_deleted=False)

    if request.method == 'POST':
        field = request.POST.get('field', '').strip()
        operator = request.POST.get('operator', '').strip()
        value = request.POST.get('value', '').strip()
        value_type = request.POST.get('value_type', '').strip() or FIELD_VALUE_TYPES.get(field, 'string')

        if not field or not operator:
            messages.error(request, _('Field and operator are required'))
            return _render_segment_detail(request, segment)

        # Determine sort order
        max_order = segment.rules.filter(is_deleted=False).order_by('-sort_order').values_list('sort_order', flat=True).first()
        next_order = (max_order or 0) + 1

        SegmentRule.objects.create(
            hub_id=hub,
            segment=segment,
            field=field,
            operator=operator,
            value=value,
            value_type=value_type,
            sort_order=next_order,
        )

        # Auto-recalculate count
        segment.update_count()

        messages.success(request, _('Rule added successfully'))
        return _render_segment_detail(request, segment)

    # GET: return the rules section with empty form state
    return _render_segment_detail(request, segment)


@login_required
def rule_edit(request, segment_id, rule_id):
    """Edit a rule on a segment."""
    hub = _hub_id(request)
    segment = get_object_or_404(Segment, id=segment_id, hub_id=hub, is_deleted=False)
    rule = get_object_or_404(SegmentRule, id=rule_id, segment=segment, is_deleted=False)

    if request.method == 'POST':
        field = request.POST.get('field', '').strip()
        operator = request.POST.get('operator', '').strip()
        value = request.POST.get('value', '').strip()
        value_type = request.POST.get('value_type', '').strip() or FIELD_VALUE_TYPES.get(field, 'string')

        if not field or not operator:
            messages.error(request, _('Field and operator are required'))
            return _render_segment_detail(request, segment)

        rule.field = field
        rule.operator = operator
        rule.value = value
        rule.value_type = value_type
        rule.save()

        # Auto-recalculate count
        segment.update_count()

        messages.success(request, _('Rule updated successfully'))
        return _render_segment_detail(request, segment)

    # GET: return the rules area
    rules = segment.rules.filter(is_deleted=False).order_by('sort_order', 'created_at')
    return django_render(request, 'segments/partials/segment_rules.html', {
        'segment': segment,
        'rules': rules,
        'editing_rule': rule,
        'field_choices': FIELD_CHOICES,
        'operator_choices': OPERATOR_CHOICES,
        'value_type_choices': VALUE_TYPE_CHOICES,
        'field_value_types_json': FIELD_VALUE_TYPES,
        'no_value_operators': NO_VALUE_OPERATORS,
    })


@login_required
@require_POST
def rule_delete(request, segment_id, rule_id):
    """Delete a rule from a segment."""
    hub = _hub_id(request)
    segment = get_object_or_404(Segment, id=segment_id, hub_id=hub, is_deleted=False)
    rule = get_object_or_404(SegmentRule, id=rule_id, segment=segment, is_deleted=False)

    rule.is_deleted = True
    rule.deleted_at = timezone.now()
    rule.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    # Auto-recalculate count
    segment.update_count()

    messages.success(request, _('Rule deleted'))
    return _render_segment_detail(request, segment)


# ============================================================================
# Settings
# ============================================================================

@login_required
@with_module_nav('segments', 'settings')
@htmx_view('segments/pages/settings.html', 'segments/partials/settings_content.html')
def settings_view(request):
    """Module settings."""
    hub = _hub_id(request)
    settings = SegmentSettings.get_for_hub(hub)

    total_segments = Segment.objects.filter(hub_id=hub, is_deleted=False).count()
    total_active = Segment.objects.filter(hub_id=hub, is_deleted=False, is_active=True).count()
    total_rules = SegmentRule.objects.filter(
        segment__hub_id=hub, segment__is_deleted=False, is_deleted=False,
    ).count()

    if request.method == 'POST':
        try:
            settings.auto_refresh_minutes = int(request.POST.get('auto_refresh_minutes', 0))
        except (ValueError, TypeError):
            settings.auto_refresh_minutes = 0

        try:
            settings.max_segment_size = int(request.POST.get('max_segment_size', 10000))
        except (ValueError, TypeError):
            settings.max_segment_size = 10000

        settings.save()
        messages.success(request, _('Settings saved successfully'))

    return {
        'settings': settings,
        'total_segments': total_segments,
        'total_active': total_active,
        'total_rules': total_rules,
    }
