"""
Segments Module Views
"""
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, render as django_render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.accounts.decorators import login_required, permission_required
from apps.core.htmx import htmx_view
from apps.core.services import export_to_csv, export_to_excel
from apps.modules_runtime.navigation import with_module_nav

from .models import Segment, SegmentRule, SegmentSettings

PER_PAGE_CHOICES = [10, 25, 50, 100]


# ======================================================================
# Dashboard
# ======================================================================

@login_required
@with_module_nav('segments', 'dashboard')
@htmx_view('segments/pages/index.html', 'segments/partials/dashboard_content.html')
def dashboard(request):
    hub_id = request.session.get('hub_id')
    return {
        'total_segments': Segment.objects.filter(hub_id=hub_id, is_deleted=False).count(),
    }


# ======================================================================
# Segment
# ======================================================================

SEGMENT_SORT_FIELDS = {
    'name': 'name',
    'color': 'color',
    'is_active': 'is_active',
    'is_dynamic': 'is_dynamic',
    'logic_operator': 'logic_operator',
    'customer_count': 'customer_count',
    'created_at': 'created_at',
}

def _build_segments_context(hub_id, per_page=10):
    qs = Segment.objects.filter(hub_id=hub_id, is_deleted=False).order_by('name')
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(1)
    return {
        'segments': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'name',
        'sort_dir': 'asc',
        'current_view': 'table',
        'per_page': per_page,
    }

def _render_segments_list(request, hub_id, per_page=10):
    ctx = _build_segments_context(hub_id, per_page)
    return django_render(request, 'segments/partials/segments_list.html', ctx)

@login_required
@with_module_nav('segments', 'list')
@htmx_view('segments/pages/segments.html', 'segments/partials/segments_content.html')
def segments_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'name')
    sort_dir = request.GET.get('dir', 'asc')
    page_number = request.GET.get('page', 1)
    current_view = request.GET.get('view', 'table')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    qs = Segment.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(color__icontains=search_query) | Q(logic_operator__icontains=search_query))

    order_by = SEGMENT_SORT_FIELDS.get(sort_field, 'name')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    export_format = request.GET.get('export')
    if export_format in ('csv', 'excel'):
        fields = ['name', 'color', 'is_active', 'is_dynamic', 'logic_operator', 'customer_count']
        headers = ['Name', 'Color', 'Is Active', 'Is Dynamic', 'Logic Operator', 'Customer Count']
        if export_format == 'csv':
            return export_to_csv(qs, fields=fields, headers=headers, filename='segments.csv')
        return export_to_excel(qs, fields=fields, headers=headers, filename='segments.xlsx')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'segments/partials/segments_list.html', {
            'segments': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'sort_field': sort_field,
            'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
        })

    return {
        'segments': page_obj, 'page_obj': page_obj,
        'search_query': search_query, 'sort_field': sort_field,
        'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
    }

@login_required
def segment_add(request):
    hub_id = request.session.get('hub_id')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        is_dynamic = request.POST.get('is_dynamic') == 'on'
        customer_count = int(request.POST.get('customer_count', 0) or 0)
        last_calculated_at = request.POST.get('last_calculated_at') or None
        logic_operator = request.POST.get('logic_operator', '').strip()
        obj = Segment(hub_id=hub_id)
        obj.name = name
        obj.description = description
        obj.color = color
        obj.is_active = is_active
        obj.is_dynamic = is_dynamic
        obj.customer_count = customer_count
        obj.last_calculated_at = last_calculated_at
        obj.logic_operator = logic_operator
        obj.save()
        return _render_segments_list(request, hub_id)
    return django_render(request, 'segments/partials/panel_segment_add.html', {})

@login_required
def segment_edit(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Segment, pk=pk, hub_id=hub_id, is_deleted=False)
    if request.method == 'POST':
        obj.name = request.POST.get('name', '').strip()
        obj.description = request.POST.get('description', '').strip()
        obj.color = request.POST.get('color', '').strip()
        obj.is_active = request.POST.get('is_active') == 'on'
        obj.is_dynamic = request.POST.get('is_dynamic') == 'on'
        obj.customer_count = int(request.POST.get('customer_count', 0) or 0)
        obj.last_calculated_at = request.POST.get('last_calculated_at') or None
        obj.logic_operator = request.POST.get('logic_operator', '').strip()
        obj.save()
        return _render_segments_list(request, hub_id)
    return django_render(request, 'segments/partials/panel_segment_edit.html', {'obj': obj})

@login_required
@require_POST
def segment_delete(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Segment, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return _render_segments_list(request, hub_id)

@login_required
@require_POST
def segment_toggle_status(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Segment, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_active = not obj.is_active
    obj.save(update_fields=['is_active', 'updated_at'])
    return _render_segments_list(request, hub_id)

@login_required
@require_POST
def segments_bulk_action(request):
    hub_id = request.session.get('hub_id')
    ids = [i.strip() for i in request.POST.get('ids', '').split(',') if i.strip()]
    action = request.POST.get('action', '')
    qs = Segment.objects.filter(hub_id=hub_id, is_deleted=False, id__in=ids)
    if action == 'activate':
        qs.update(is_active=True)
    elif action == 'deactivate':
        qs.update(is_active=False)
    elif action == 'delete':
        qs.update(is_deleted=True, deleted_at=timezone.now())
    return _render_segments_list(request, hub_id)


# ======================================================================
# Settings
# ======================================================================

@login_required
@permission_required('segments.manage_settings')
@with_module_nav('segments', 'settings')
@htmx_view('segments/pages/settings.html', 'segments/partials/settings_content.html')
def settings_view(request):
    hub_id = request.session.get('hub_id')
    config, _ = SegmentSettings.objects.get_or_create(hub_id=hub_id)
    if request.method == 'POST':
        config.auto_refresh_minutes = request.POST.get('auto_refresh_minutes', config.auto_refresh_minutes)
        config.max_segment_size = request.POST.get('max_segment_size', config.max_segment_size)
        config.save()
    return {'config': config}

