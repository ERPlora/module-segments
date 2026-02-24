from django.urls import path
from . import views

app_name = 'segments'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Segment
    path('segments/', views.segments_list, name='segments_list'),
    path('segments/add/', views.segment_add, name='segment_add'),
    path('segments/<uuid:pk>/edit/', views.segment_edit, name='segment_edit'),
    path('segments/<uuid:pk>/delete/', views.segment_delete, name='segment_delete'),
    path('segments/<uuid:pk>/toggle/', views.segment_toggle_status, name='segment_toggle_status'),
    path('segments/bulk/', views.segments_bulk_action, name='segments_bulk_action'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
