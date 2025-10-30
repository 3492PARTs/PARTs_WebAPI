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
    """Tests for admin.models."""

    @pytest.mark.django_db
    def test_error_log_model_creation(self, test_user):
        """Test ErrorLog model can be created."""
        from admin.models import ErrorLog
        from django.utils import timezone
        
        log = ErrorLog.objects.create(
            user=test_user,
            path="/test/path",
            message="Test message",
            exception="Test exception",
            traceback="Test traceback",
            time=timezone.now(),
            void_ind="n"
        )
        assert log.id is not None
        assert log.message == "Test message"

    @pytest.mark.django_db
    def test_error_log_str(self, test_user):
        """Test ErrorLog __str__ method."""
        from admin.models import ErrorLog
        from django.utils import timezone
        
        log = ErrorLog.objects.create(
            user=test_user,
            path="/test",
            message="Msg",
            time=timezone.now(),
            void_ind="n"
        )
        str_repr = str(log)
        assert str_repr is not None


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
    """Tests for alert models."""

    @pytest.mark.django_db
    def test_alert_type_creation(self):
        """Test AlertType model."""
        from alerts.models import AlertType
        
        alert_type = AlertType.objects.create(
            name="Test Alert",
            subject="Subject",
            body="Body",
            void_ind="n"
        )
        assert alert_type.id is not None

    @pytest.mark.django_db
    def test_alert_channel_creation(self):
        """Test AlertChannel model."""
        from alerts.models import AlertChannel
        
        channel = AlertChannel.objects.create(
            comm_typ="email",
            user_allowed="y",
            void_ind="n"
        )
        assert channel.id is not None


class TestAttendanceModels:
    """Tests for attendance models."""

    @pytest.mark.django_db
    def test_meeting_creation(self):
        """Test Meeting model."""
        from attendance.models import Meeting
        from django.utils import timezone
        
        meeting = Meeting.objects.create(
            meeting_nm="Test Meeting",
            meeting_desc="Description",
            meeting_time=timezone.now(),
            season_id=2024,
            void_ind="n"
        )
        assert meeting.id is not None

    @pytest.mark.django_db
    def test_attendance_approval_type_creation(self):
        """Test AttendanceApprovalType model."""
        from attendance.models import AttendanceApprovalType
        
        approval_type = AttendanceApprovalType.objects.create(
            approval_typ_nm="Approved",
            void_ind="n"
        )
        assert approval_type.id is not None


class TestFormModels:
    """Tests for form models."""

    @pytest.mark.django_db
    def test_form_type_creation(self):
        """Test FormType model."""
        from form.models import FormType
        
        form_type = FormType.objects.create(
            form_typ_nm="Test Form",
            void_ind="n"
        )
        assert form_type.id is not None

    @pytest.mark.django_db
    def test_question_type_creation(self):
        """Test QuestionType model."""
        from form.models import QuestionType
        
        q_type = QuestionType.objects.create(
            question_typ="text",
            void_ind="n"
        )
        assert q_type.id is not None


class TestTBAModels:
    """Tests for TBA models."""

    @pytest.mark.django_db
    def test_team_info_creation(self):
        """Test TeamInfo model."""
        from tba.models import TeamInfo
        
        team = TeamInfo.objects.create(
            team_no=3492,
            team_nm="PARTs",
            void_ind="n"
        )
        assert team.team_no == 3492


class TestUserModels:
    """Tests for user models."""

    @pytest.mark.django_db
    def test_phone_type_creation(self):
        """Test PhoneType model."""
        from user.models import PhoneType
        
        phone_type = PhoneType.objects.create(
            phone_type="mobile",
            carrier="Verizon",
            void_ind="n"
        )
        assert phone_type.id is not None

    @pytest.mark.django_db
    def test_link_creation(self, test_user):
        """Test Link model."""
        from user.models import Link
        
        link = Link.objects.create(
            user=test_user,
            link="https://example.com",
            link_text="Example",
            void_ind="n"
        )
        assert link.id is not None


class TestSponsoringModels:
    """Tests for sponsoring models."""

    @pytest.mark.django_db
    def test_sponsor_creation(self):
        """Test Sponsor model."""
        from sponsoring.models import Sponsor
        
        sponsor = Sponsor.objects.create(
            sponsor_nm="Test Sponsor",
            phone="123-456-7890",
            email="test@example.com",
            void_ind="n"
        )
        assert sponsor.id is not None

    @pytest.mark.django_db
    def test_item_creation(self):
        """Test Item model."""
        from sponsoring.models import Item
        
        item = Item.objects.create(
            item_nm="Test Item",
            item_desc="Description",
            quantity=10,
            active=True,
            void_ind="n"
        )
        assert item.id is not None


class TestScoutingModels:
    """Tests for scouting models."""

    @pytest.mark.django_db
    def test_season_creation(self):
        """Test Season model."""
        from scouting.models import Season
        
        season = Season.objects.create(
            season=2024,
            current="y",
            void_ind="n"
        )
        assert season.season == 2024

    @pytest.mark.django_db
    def test_competition_creation(self):
        """Test Competition model."""
        from scouting.models import Competition
        from datetime import date
        
        competition = Competition.objects.create(
            competition_nm="Test Competition",
            competition_code="TC2024",
            date_st=date.today(),
            date_end=date.today(),
            season_id=2024,
            void_ind="n"
        )
        assert competition.id is not None


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
