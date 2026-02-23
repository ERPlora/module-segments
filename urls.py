from django.urls import path
from . import views

app_name = 'segments'

urlpatterns = [
    # Segment list
    path('', views.segment_list, name='list'),

    # Segment CRUD
    path('add/', views.segment_add, name='add'),
    path('<uuid:segment_id>/', views.segment_detail, name='detail'),
    path('<uuid:segment_id>/edit/', views.segment_edit, name='edit'),
    path('<uuid:segment_id>/delete/', views.segment_delete, name='delete'),

    # Segment actions
    path('<uuid:segment_id>/refresh/', views.segment_refresh, name='refresh'),
    path('<uuid:segment_id>/export/', views.segment_export, name='export'),

    # Rules
    path('<uuid:segment_id>/rules/add/', views.rule_add, name='rule_add'),
    path('<uuid:segment_id>/rules/<uuid:rule_id>/edit/', views.rule_edit, name='rule_edit'),
    path('<uuid:segment_id>/rules/<uuid:rule_id>/delete/', views.rule_delete, name='rule_delete'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
