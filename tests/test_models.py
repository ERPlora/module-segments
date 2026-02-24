"""Tests for segments models."""
import pytest
from django.utils import timezone

from segments.models import Segment


@pytest.mark.django_db
class TestSegment:
    """Segment model tests."""

    def test_create(self, segment):
        """Test Segment creation."""
        assert segment.pk is not None
        assert segment.is_deleted is False

    def test_str(self, segment):
        """Test string representation."""
        assert str(segment) is not None
        assert len(str(segment)) > 0

    def test_soft_delete(self, segment):
        """Test soft delete."""
        pk = segment.pk
        segment.is_deleted = True
        segment.deleted_at = timezone.now()
        segment.save()
        assert not Segment.objects.filter(pk=pk).exists()
        assert Segment.all_objects.filter(pk=pk).exists()

    def test_queryset_excludes_deleted(self, hub_id, segment):
        """Test default queryset excludes deleted."""
        segment.is_deleted = True
        segment.deleted_at = timezone.now()
        segment.save()
        assert Segment.objects.filter(hub_id=hub_id).count() == 0

    def test_toggle_active(self, segment):
        """Test toggling is_active."""
        original = segment.is_active
        segment.is_active = not original
        segment.save()
        segment.refresh_from_db()
        assert segment.is_active != original


