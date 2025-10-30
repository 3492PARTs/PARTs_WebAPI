"""
Tests for general.util module.
"""
import pytest
import pytz
from datetime import datetime
from general.util import date_time_to_mdyhm


class TestDateTimeToMdyhm:
    """Tests for date_time_to_mdyhm function."""

    def test_date_time_to_mdyhm_default_timezone(self):
        """Test date conversion with default Eastern timezone."""
        dt = datetime(2023, 12, 15, 14, 30, 0, tzinfo=pytz.UTC)
        result = date_time_to_mdyhm(dt)
        assert "12/15/2023" in result
        assert "AM" in result or "PM" in result

    def test_date_time_to_mdyhm_custom_timezone(self):
        """Test date conversion with custom timezone."""
        dt = datetime(2023, 6, 1, 12, 0, 0, tzinfo=pytz.UTC)
        result = date_time_to_mdyhm(dt, 'America/Los_Angeles')
        assert "06/01/2023" in result
        assert "AM" in result or "PM" in result

    def test_date_time_to_mdyhm_afternoon(self):
        """Test date conversion for afternoon time."""
        dt = datetime(2023, 3, 10, 20, 45, 0, tzinfo=pytz.UTC)
        result = date_time_to_mdyhm(dt)
        assert "03/10/2023" in result
        assert "PM" in result
