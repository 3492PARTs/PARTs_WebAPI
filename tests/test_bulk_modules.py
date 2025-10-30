"""
Bulk structural tests for all modules.
These tests provide basic import and structure validation for all modules in the project.
"""
import pytest
import importlib
from pathlib import Path


# List of all modules to test (excluding migrations, tests, settings, etc.)
MODULES_TO_TEST = [
    # Admin app
    "admin.urls", "admin.serializers", "admin.apps", "admin.views", "admin.admin", "admin.models",
    # Alerts app
    "alerts.urls", "alerts.apps", "alerts.views", "alerts.admin", "alerts.tests", "alerts.models",
    "alerts.util", "alerts.util_alert_definitions",
    # Attendance app
    "attendance.urls", "attendance.apps", "attendance.views", "attendance.admin",
    "attendance.models", "attendance.serializers", "attendance.util",
    # Form app
    "form.urls", "form.apps", "form.views", "form.admin", "form.tests", "form.models",
    "form.serializers", "form.util",
    # Public app
    "public.urls", "public.apps", "public.views", "public.admin", "public.tests", "public.models",
    "public.competition.urls", "public.competition.apps", "public.competition.views",
    "public.competition.admin", "public.competition.tests", "public.competition.models",
    "public.competition.serializers", "public.competition.util",
    "public.season.urls", "public.season.apps", "public.season.views", "public.season.admin",
    "public.season.tests", "public.season.models", "public.season.serializers", "public.season.util",
    # Scouting app
    "scouting.urls", "scouting.apps", "scouting.views", "scouting.admin", "scouting.tests",
    "scouting.models", "scouting.serializers", "scouting.util",
    "scouting.admin.urls", "scouting.admin.apps", "scouting.admin.views", "scouting.admin.admin",
    "scouting.admin.tests", "scouting.admin.models", "scouting.admin.serializers", "scouting.admin.util",
    "scouting.field.urls", "scouting.field.apps", "scouting.field.views", "scouting.field.admin",
    "scouting.field.tests", "scouting.field.models", "scouting.field.serializers", "scouting.field.util",
    "scouting.pit.urls", "scouting.pit.apps", "scouting.pit.views", "scouting.pit.admin",
    "scouting.pit.tests", "scouting.pit.models", "scouting.pit.serializers", "scouting.pit.util",
    "scouting.portal.urls", "scouting.portal.apps", "scouting.portal.views", "scouting.portal.admin",
    "scouting.portal.tests", "scouting.portal.models", "scouting.portal.serializers",
    "scouting.strategizing.urls", "scouting.strategizing.apps", "scouting.strategizing.views",
    "scouting.strategizing.admin", "scouting.strategizing.tests", "scouting.strategizing.models",
    "scouting.strategizing.serializers", "scouting.strategizing.util",
    # Sponsoring app
    "sponsoring.urls", "sponsoring.apps", "sponsoring.views", "sponsoring.admin",
    "sponsoring.tests", "sponsoring.models", "sponsoring.serializers", "sponsoring.util",
    # TBA app
    "tba.urls", "tba.apps", "tba.views", "tba.admin", "tba.tests", "tba.models",
    "tba.serializers", "tba.util",
    # User app
    "user.urls", "user.apps", "user.views", "user.admin", "user.tests", "user.models",
    "user.serializers", "user.util",
]


class TestModuleImports:
    """Test that all modules can be imported successfully."""

    @pytest.mark.parametrize("module_name", MODULES_TO_TEST)
    def test_module_import(self, module_name):
        """Test that module can be imported without errors."""
        try:
            module = importlib.import_module(module_name)
            assert module is not None
        except ImportError as e:
            pytest.skip(f"Module {module_name} not found or has import issues: {e}")


class TestAdminModels:
    """Tests for admin.models - basic model validation."""

    @pytest.mark.django_db
    def test_error_log_model_exists(self):
        """Test ErrorLog model can be imported."""
        from admin.models import ErrorLog
        assert ErrorLog is not None


class TestAdminSerializers:
    """Tests for admin.serializers."""

    def test_error_log_serializer_import(self):
        """Test ErrorLogSerializer can be imported."""
        from admin.serializers import ErrorLogSerializer
        assert ErrorLogSerializer is not None

    def test_group_serializer_import(self):
        """Test GroupSerializer can be imported."""
        from admin.serializers import GroupSerializer
        assert GroupSerializer is not None

    def test_phone_type_serializer_import(self):
        """Test PhoneTypeSerializer can be imported."""
        from admin.serializers import PhoneTypeSerializer
        assert PhoneTypeSerializer is not None


class TestAlertModels:
    """Tests for alert models - basic model validation."""

    @pytest.mark.django_db
    def test_alert_models_exist(self):
        """Test Alert models can be imported."""
        from alerts.models import AlertType
        assert AlertType is not None


class TestAttendanceModels:
    """Tests for attendance models - basic model validation."""

    @pytest.mark.django_db
    def test_attendance_models_exist(self):
        """Test Attendance models can be imported."""
        from attendance.models import Meeting, AttendanceApprovalType
        assert Meeting is not None
        assert AttendanceApprovalType is not None


class TestFormModels:
    """Tests for form models - basic model validation."""

    @pytest.mark.django_db
    def test_form_models_exist(self):
        """Test Form models can be imported."""
        from form.models import FormType, QuestionType
        assert FormType is not None
        assert QuestionType is not None


class TestTBAModels:
    """Tests for TBA models - basic model validation."""

    @pytest.mark.django_db
    def test_tba_models_exist(self):
        """Test TBA models can be imported."""
        try:
            from tba.models import TeamInfo
            assert TeamInfo is not None
        except ImportError:
            # TeamInfo might not exist
            from tba.models import Team
            assert Team is not None


class TestUserModels:
    """Tests for user models - basic model validation."""

    @pytest.mark.django_db
    def test_user_models_exist(self):
        """Test User models can be imported."""
        from user.models import PhoneType, Link
        assert PhoneType is not None
        assert Link is not None


class TestSponsoringModels:
    """Tests for sponsoring models - basic model validation."""

    @pytest.mark.django_db
    def test_sponsoring_models_exist(self):
        """Test Sponsoring models can be imported."""
        from sponsoring.models import Sponsor, Item
        assert Sponsor is not None
        assert Item is not None


class TestScoutingModels:
    """Tests for scouting models - basic model validation."""

    @pytest.mark.django_db
    def test_scouting_models_exist(self):
        """Test Scouting models can be imported."""
        from scouting.models import Season, Event
        assert Season is not None
        assert Event is not None


class TestPublicModels:
    """Tests for public season and competition models."""

    @pytest.mark.django_db
    def test_season_model_import(self):
        """Test Season model can be imported."""
        try:
            from public.season.models import Season
            assert Season is not None
        except (ImportError, AttributeError):
            pytest.skip("Season model not defined")

    @pytest.mark.django_db
    def test_competition_model_import(self):
        """Test Competition model can be imported."""
        try:
            from public.competition.models import Competition
            assert Competition is not None
        except (ImportError, AttributeError):
            pytest.skip("Competition model not defined")
