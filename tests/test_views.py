"""Tests for segments views."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboard:
    """Dashboard view tests."""

    def test_dashboard_loads(self, auth_client):
        """Test dashboard page loads."""
        url = reverse('segments:dashboard')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_dashboard_htmx(self, auth_client):
        """Test dashboard HTMX partial."""
        url = reverse('segments:dashboard')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication."""
        url = reverse('segments:dashboard')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestSegmentViews:
    """Segment view tests."""

    def test_list_loads(self, auth_client):
        """Test list view loads."""
        url = reverse('segments:segments_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_htmx(self, auth_client):
        """Test list HTMX partial."""
        url = reverse('segments:segments_list')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_list_search(self, auth_client):
        """Test list search."""
        url = reverse('segments:segments_list')
        response = auth_client.get(url, {'q': 'test'})
        assert response.status_code == 200

    def test_list_sort(self, auth_client):
        """Test list sorting."""
        url = reverse('segments:segments_list')
        response = auth_client.get(url, {'sort': 'created_at', 'dir': 'desc'})
        assert response.status_code == 200

    def test_export_csv(self, auth_client):
        """Test CSV export."""
        url = reverse('segments:segments_list')
        response = auth_client.get(url, {'export': 'csv'})
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self, auth_client):
        """Test Excel export."""
        url = reverse('segments:segments_list')
        response = auth_client.get(url, {'export': 'excel'})
        assert response.status_code == 200

    def test_add_form_loads(self, auth_client):
        """Test add form loads."""
        url = reverse('segments:segment_add')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_post(self, auth_client):
        """Test creating via POST."""
        url = reverse('segments:segment_add')
        data = {
            'name': 'New Name',
            'description': 'Test description',
            'color': 'New Color',
            'is_active': 'on',
            'is_dynamic': 'on',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_edit_form_loads(self, auth_client, segment):
        """Test edit form loads."""
        url = reverse('segments:segment_edit', args=[segment.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_post(self, auth_client, segment):
        """Test editing via POST."""
        url = reverse('segments:segment_edit', args=[segment.pk])
        data = {
            'name': 'Updated Name',
            'description': 'Test description',
            'color': 'Updated Color',
            'is_active': '',
            'is_dynamic': '',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_delete(self, auth_client, segment):
        """Test soft delete via POST."""
        url = reverse('segments:segment_delete', args=[segment.pk])
        response = auth_client.post(url)
        assert response.status_code == 200
        segment.refresh_from_db()
        assert segment.is_deleted is True

    def test_toggle_status(self, auth_client, segment):
        """Test toggle active status."""
        url = reverse('segments:segment_toggle_status', args=[segment.pk])
        original = segment.is_active
        response = auth_client.post(url)
        assert response.status_code == 200
        segment.refresh_from_db()
        assert segment.is_active != original

    def test_bulk_delete(self, auth_client, segment):
        """Test bulk delete."""
        url = reverse('segments:segments_bulk_action')
        response = auth_client.post(url, {'ids': str(segment.pk), 'action': 'delete'})
        assert response.status_code == 200
        segment.refresh_from_db()
        assert segment.is_deleted is True

    def test_list_requires_auth(self, client):
        """Test list requires authentication."""
        url = reverse('segments:segments_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestSettings:
    """Settings view tests."""

    def test_settings_loads(self, auth_client):
        """Test settings page loads."""
        url = reverse('segments:settings')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_settings_requires_auth(self, client):
        """Test settings requires authentication."""
        url = reverse('segments:settings')
        response = client.get(url)
        assert response.status_code == 302

