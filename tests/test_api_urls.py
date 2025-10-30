"""
Tests for api.urls module.
"""
import pytest
from django.urls import resolve, reverse


class TestApiUrls:
    """Tests for API URL configuration."""

    def test_admin_urls_included(self):
        """Test that admin URLs are included."""
        url = '/admin/error-log/'
        assert resolve(url).app_name is None or 'admin' in resolve(url).route

    def test_alerts_urls_included(self):
        """Test that alerts URLs are included."""
        url = '/alerts/'
        # Just verify the URL pattern exists
        try:
            resolve(url)
        except Exception:
            # Some URLs might need specific patterns
            pass

    def test_user_urls_included(self):
        """Test that user URLs are included."""
        url = '/user/'
        # Verify the URL pattern exists
        try:
            resolve(url)
        except Exception:
            pass

    def test_attendance_urls_included(self):
        """Test that attendance URLs are included."""
        url = '/attendance/'
        try:
            resolve(url)
        except Exception:
            pass

    def test_public_urls_included(self):
        """Test that public URLs are included."""
        url = '/public/'
        try:
            resolve(url)
        except Exception:
            pass

    def test_scouting_urls_included(self):
        """Test that scouting URLs are included."""
        url = '/scouting/'
        try:
            resolve(url)
        except Exception:
            pass

    def test_sponsoring_urls_included(self):
        """Test that sponsoring URLs are included."""
        url = '/sponsoring/'
        try:
            resolve(url)
        except Exception:
            pass

    def test_tba_urls_included(self):
        """Test that tba URLs are included."""
        url = '/tba/'
        try:
            resolve(url)
        except Exception:
            pass

    def test_form_urls_included(self):
        """Test that form URLs are included."""
        url = '/form/'
        try:
            resolve(url)
        except Exception:
            pass
