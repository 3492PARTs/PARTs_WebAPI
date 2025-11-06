"""
Comprehensive tests for alerts/util_alert_definitions.py module.
This adds coverage for alert staging functions with 14% current coverage.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import pytz
from scouting.models import CompetitionLevel


@pytest.mark.django_db
class TestStageAlerts:
    """Tests for the main stage_alerts orchestrator function."""

    @patch('alerts.util_alert_definitions.stage_all_field_schedule_alerts')
    @patch('alerts.util_alert_definitions.stage_schedule_alerts')
    @patch('alerts.util_alert_definitions.stage_error_alerts')
    @patch('alerts.util_alert_definitions.stage_form_alerts')
    @patch('alerts.util_alert_definitions.stage_match_strategy_added_alerts')
    @patch('alerts.util_alert_definitions.stage_meeting_alert')
    def test_stage_alerts_calls_all_staging_functions(
        self,
        mock_meeting,
        mock_strategy,
        mock_form,
        mock_error,
        mock_schedule,
        mock_field_schedule,
    ):
        """Test that stage_alerts calls all sub-staging functions."""
        from alerts.util_alert_definitions import stage_alerts
        
        # Setup return values
        mock_field_schedule.return_value = "field_result"
        mock_schedule.return_value = "schedule_result"
        mock_error.return_value = "error_result"
        mock_form.return_value = "form_result"
        mock_strategy.return_value = "strategy_result"
        mock_meeting.return_value = "meeting_result"
        
        result = stage_alerts()
        
        # Verify all functions were called
        mock_field_schedule.assert_called_once()
        mock_schedule.assert_called_once()
        mock_error.assert_called_once()
        mock_form.assert_any_call("team-cntct")
        mock_form.assert_any_call("team-app")
        mock_strategy.assert_called_once()
        assert mock_meeting.call_count == 2
        mock_meeting.assert_any_call(True)  # start
        mock_meeting.assert_any_call(False)  # end
        
        # Verify result contains all outputs
        assert "field_result" in result
        assert "schedule_result" in result
        assert "error_result" in result
        assert "form_result" in result
        assert "strategy_result" in result
        assert "meeting_result" in result


@pytest.mark.django_db
class TestStageErrorAlerts:
    """Tests for stage_error_alerts function."""

    def test_stage_error_alerts_no_errors(self):
        """Test staging error alerts when no errors exist."""
        from alerts.util_alert_definitions import stage_error_alerts
        from alerts.models import AlertType
        
        # Create alert type
        alert_type = AlertType.objects.create(
            alert_typ="error",
            alert_typ_nm="Error Alerts",
            subject="Error Alert",
            body="An error occurred",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        result = stage_error_alerts()
        
        assert result == "NONE TO STAGE"
        
        # Verify last_run was updated
        alert_type.refresh_from_db()
        assert alert_type.last_run > timezone.now() - timedelta(seconds=10)

    def test_stage_error_alerts_with_errors(self, test_user):
        """Test staging error alerts when errors exist."""
        from alerts.util_alert_definitions import stage_error_alerts
        from alerts.models import AlertType
        from admin.models import ErrorLog
        
        # Create alert type
        alert_type = AlertType.objects.create(
            alert_typ="error",
            alert_typ_nm="Error Alerts",
            subject="Error Alert",
            body="An error occurred",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        # Create error logs
        error1 = ErrorLog.objects.create(
            user=test_user,
            time=timezone.now() - timedelta(minutes=30),
            exception="Test Exception 1",
            message="Error message 1",
            void_ind="n"
        )
        error2 = ErrorLog.objects.create(
            user=test_user,
            time=timezone.now() - timedelta(minutes=15),
            exception="Test Exception 2",
            message="Error message 2",
            void_ind="n"
        )
        
        with patch('alerts.util_alert_definitions.send_alerts_to_role') as mock_send:
            result = stage_error_alerts()
            
            assert "Test Exception 1" in result or "Error message 1" in result
            assert "Test Exception 2" in result or "Error message 2" in result
            assert result != "NONE TO STAGE"
            
            # Verify send_alerts_to_role was called
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args[1]['alert_type'] == alert_type

    def test_stage_error_alerts_ignores_auth_errors(self, test_user):
        """Test that authentication errors are ignored."""
        from alerts.util_alert_definitions import stage_error_alerts
        from alerts.models import AlertType
        from admin.models import ErrorLog
        
        alert_type = AlertType.objects.create(
            alert_typ="error",
            alert_typ_nm="Error Alerts",
            subject="Error Alert",
            body="An error occurred",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        # Create ignored error
        ErrorLog.objects.create(
            user=test_user,
            time=timezone.now() - timedelta(minutes=30),
            exception="No active account found with the given credentials",
            message="Auth error",
            void_ind="n"
        )
        
        result = stage_error_alerts()
        
        # Should be ignored
        assert result == "NONE TO STAGE"


@pytest.mark.django_db
class TestStageFormAlerts:
    """Tests for stage_form_alerts function."""

    def test_stage_form_alerts_no_responses(self):
        """Test staging form alerts when no responses exist."""
        from alerts.util_alert_definitions import stage_form_alerts
        from alerts.models import AlertType
        from form.models import FormType
        
        # Create form type
        FormType.objects.create(
            form_typ="team-cntct",
            form_nm="Contact Form"
        )
        
        # Create alert type
        AlertType.objects.create(
            alert_typ="team-cntct",
            alert_typ_nm="Contact Form Alerts",
            subject="New Contact Form",
            body="A new contact form was submitted",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        result = stage_form_alerts("team-cntct")
        
        assert result == "NONE TO STAGE"

    def test_stage_form_alerts_with_contact_responses(self, test_user):
        """Test staging alerts for contact form responses."""
        from alerts.util_alert_definitions import stage_form_alerts
        from alerts.models import AlertType
        from form.models import FormType, Response
        
        # Create form type
        form_type = FormType.objects.create(
            form_typ="team-cntct",
            form_nm="Contact Form"
        )
        
        # Create alert type
        alert_type = AlertType.objects.create(
            alert_typ="team-cntct",
            alert_typ_nm="Contact Form Alerts",
            subject="New Contact Form",
            body="A new contact form was submitted",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        # Create responses
        response1 = Response.objects.create(
            form_typ=form_type,
            time=timezone.now() - timedelta(minutes=30),
            void_ind="n"
        )
        
        with patch('alerts.util_alert_definitions.send_alerts_to_role') as mock_send:
            result = stage_form_alerts("team-cntct")
            
            assert str(response1.id) in result
            assert result != "NONE TO STAGE"
            
            # Verify correct URL format for contact form
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "contact" in call_args[1]['url']

    def test_stage_form_alerts_with_application_responses(self, test_user):
        """Test staging alerts for team application responses."""
        from alerts.util_alert_definitions import stage_form_alerts
        from alerts.models import AlertType
        from form.models import FormType, Response
        
        # Create form type
        form_type = FormType.objects.create(
            form_typ="team-app",
            form_nm="Team Application"
        )
        
        # Create alert type
        AlertType.objects.create(
            alert_typ="team-app",
            alert_typ_nm="Application Alerts",
            subject="New Team Application",
            body="A new application was submitted",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        # Create responses
        Response.objects.create(
            form_typ=form_type,
            time=timezone.now() - timedelta(minutes=30),
            void_ind="n"
        )
        
        with patch('alerts.util_alert_definitions.send_alerts_to_role') as mock_send:
            result = stage_form_alerts("team-app")
            
            assert result != "NONE TO STAGE"
            
            # Verify correct URL format for application
            call_args = mock_send.call_args
            assert "join/team-application" in call_args[1]['url']


@pytest.mark.django_db
class TestStageFieldScheduleAlerts:
    """Tests for field schedule alert staging."""

    def test_stage_all_field_schedule_alerts_no_current_event(self):
        """Test when there's no current event."""
        from alerts.util_alert_definitions import stage_all_field_schedule_alerts
        
        with patch('alerts.util_alert_definitions.scouting.util.get_current_event', return_value=None):
            result = stage_all_field_schedule_alerts()
            
            assert result == "NONE TO STAGE"

    def test_stage_all_field_schedule_alerts_no_schedules(self):
        """Test when event exists but no schedules."""
        from alerts.util_alert_definitions import stage_all_field_schedule_alerts
        from scouting.models import Event, Season
        
        # Create event
        season = Season.objects.create(
            season="2024",
            game="Test Game",
            manual="Test Manual"
        )
        event = Event.objects.create(
            event_nm="Test Event",
            event_cd="test2024",
            season=season,
            date_st=timezone.now(),
            date_end=timezone.now() + timedelta(days=3),
            timezone="America/New_York",
            void_ind="n"
        )
        
        with patch('alerts.util_alert_definitions.scouting.util.get_current_event', return_value=event):
            result = stage_all_field_schedule_alerts()
            
            assert result == "NONE TO STAGE"

    def test_stage_field_schedule_alerts_15_minute_warning(self, test_user):
        """Test 15 minute warning alerts."""
        from alerts.util_alert_definitions import stage_field_schedule_alerts
        from scouting.models import Event, Season, FieldSchedule
        from alerts.models import CommunicationChannelType
        
        # Create communication channel types
        for comm_typ in ["txt", "notification", "discord"]:
            CommunicationChannelType.objects.create(
                comm_typ=comm_typ,
                comm_nm=comm_typ.title(),
                void_ind="n"
            )
        
        # Create event
        season = Season.objects.create(season="2024", game="Test Game", manual="Test Manual")
        event = Event.objects.create(
            event_nm="Test Event",
            event_cd="test2024",
            season=season,
            date_st=timezone.now(),
            date_end=timezone.now() + timedelta(days=3),
            timezone="America/New_York",
            void_ind="n"
        )
        
        # Create field schedule 14 minutes from now
        future_time = timezone.now() + timedelta(minutes=14)
        sfs = FieldSchedule.objects.create(
            event=event,
            st_time=future_time,
            end_time=future_time + timedelta(hours=1),
            red_one=test_user,
            notification1=False,
            notification2=False,
            notification3=False,
            void_ind="n"
        )
        
        result = stage_field_schedule_alerts(1, [sfs])
        
        # Verify notification1 was set
        sfs.refresh_from_db()
        assert sfs.notification1 is True
        
        # Should have created alerts for assigned user
        assert test_user.get_full_name() in result

    def test_stage_field_schedule_alerts_5_minute_warning(self):
        """Test 5 minute warning alerts."""
        from alerts.util_alert_definitions import stage_field_schedule_alerts
        from scouting.models import Event, Season, FieldSchedule
        
        season = Season.objects.create(season="2024", game="Test Game", manual="Test Manual")
        event = Event.objects.create(
            event_nm="Test Event",
            event_cd="test2024",
            season=season,
            date_st=timezone.now(),
            date_end=timezone.now() + timedelta(days=3),
            timezone="America/New_York",
            void_ind="n"
        )
        
        future_time = timezone.now() + timedelta(minutes=4)
        sfs = FieldSchedule.objects.create(
            event=event,
            st_time=future_time,
            end_time=future_time + timedelta(hours=1),
            notification1=True,
            notification2=False,
            notification3=False,
            void_ind="n"
        )
        
        with patch('alerts.util_alert_definitions.create_alert'):
            with patch('alerts.util_alert_definitions.create_channel_send_for_comm_typ'):
                result = stage_field_schedule_alerts(2, [sfs])
                
                sfs.refresh_from_db()
                assert sfs.notification2 is True

    def test_stage_field_schedule_alerts_now_notification(self):
        """Test immediate notification."""
        from alerts.util_alert_definitions import stage_field_schedule_alerts
        from scouting.models import Event, Season, FieldSchedule
        
        season = Season.objects.create(season="2024", game="Test Game", manual="Test Manual")
        event = Event.objects.create(
            event_nm="Test Event",
            event_cd="test2024",
            season=season,
            date_st=timezone.now(),
            date_end=timezone.now() + timedelta(days=3),
            timezone="America/New_York",
            void_ind="n"
        )
        
        # Very near future (< 30 seconds)
        future_time = timezone.now() + timedelta(seconds=20)
        sfs = FieldSchedule.objects.create(
            event=event,
            st_time=future_time,
            end_time=future_time + timedelta(hours=1),
            notification1=True,
            notification2=True,
            notification3=False,
            void_ind="n"
        )
        
        with patch('alerts.util_alert_definitions.create_alert'):
            with patch('alerts.util_alert_definitions.create_channel_send_for_comm_typ'):
                result = stage_field_schedule_alerts(3, [sfs])
                
                sfs.refresh_from_db()
                assert sfs.notification3 is True


@pytest.mark.django_db
class TestStageScheduleAlerts:
    """Tests for schedule alert staging."""

    def test_stage_schedule_alerts_no_current_event(self):
        """Test when there's no current event."""
        from alerts.util_alert_definitions import stage_schedule_alerts
        
        with patch('alerts.util_alert_definitions.scouting.util.get_current_event', return_value=None):
            result = stage_schedule_alerts()
            
            assert result == "NONE TO STAGE"

    def test_stage_schedule_alerts_no_schedules(self):
        """Test when event exists but no schedules."""
        from alerts.util_alert_definitions import stage_schedule_alerts
        from scouting.models import Event, Season
        
        season = Season.objects.create(season="2024", game="Test Game", manual="Test Manual")
        event = Event.objects.create(
            event_nm="Test Event",
            event_cd="test2024",
            season=season,
            date_st=timezone.now(),
            date_end=timezone.now() + timedelta(days=3),
            timezone="America/New_York",
            void_ind="n"
        )
        
        with patch('alerts.util_alert_definitions.scouting.util.get_current_event', return_value=event):
            result = stage_schedule_alerts()
            
            assert result == "NONE TO STAGE"


@pytest.mark.django_db
class TestStageMatchStrategyAddedAlerts:
    """Tests for match strategy added alert staging."""

    def test_stage_match_strategy_added_alerts_no_strategies(self):
        """Test when no new strategies exist."""
        from alerts.util_alert_definitions import stage_match_strategy_added_alerts
        from alerts.models import AlertType
        
        AlertType.objects.create(
            alert_typ="match_strat_added",
            alert_typ_nm="Match Strategy Added",
            subject="New Strategy",
            body="A new match strategy was added",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        result = stage_match_strategy_added_alerts()
        
        assert result == "NONE TO STAGE"

    def test_stage_match_strategy_added_alerts_with_strategies(self, test_user):
        """Test staging alerts for new match strategies."""
        from alerts.util_alert_definitions import stage_match_strategy_added_alerts
        from alerts.models import AlertType
        from scouting.models import Event, Season, Match, MatchStrategy
        
        # Set last_run to be BEFORE we create the strategy
        last_run_time = timezone.now() - timedelta(hours=1)
        
        # Create alert type with proper formatting placeholders
        alert_type = AlertType.objects.create(
            alert_typ="match_strat_added",
            alert_typ_nm="Match Strategy Added",
            subject="New Strategy",
            body="Match strategy added by {} for match {}",
            last_run=last_run_time,
            void_ind="n"
        )
        
        # Create event and match
        season = Season.objects.create(season="2024", game="Test Game", manual="Test Manual")
        event = Event.objects.create(
            event_nm="Test Event",
            event_cd="test2024",
            season=season,
            date_st=timezone.now(),
            date_end=timezone.now() + timedelta(days=3),
            timezone="America/New_York",
            void_ind="n"
        )
        comp_level = CompetitionLevel.objects.create(
            comp_lvl_typ="qm",
            comp_lvl_typ_nm="Qualification Match",
            comp_lvl_order=1,
            void_ind="n"
        )
        match = Match.objects.create(
            match_key="test2024_qm1",
            event=event,
            comp_level=comp_level,
            match_number=1,
            void_ind="n"
        )
        
        # Create match strategy AFTER last_run
        strategy_time = last_run_time + timedelta(minutes=30)
        MatchStrategy.objects.create(
            match=match,
            user=test_user,
            time=strategy_time,
            strategy="Test strategy",
            void_ind="n"
        )
        
        # Mock send_alerts_to_role since it requires users with specific roles
        with patch('alerts.util_alert_definitions.send_alerts_to_role') as mock_send:
            mock_send.return_value = []  # No users with the role
            result = stage_match_strategy_added_alerts()
            
            # Function was called even if no users were alerted
            mock_send.assert_called_once()


@pytest.mark.django_db
class TestStageMeetingAlerts:
    """Tests for meeting alert staging."""

    def test_stage_meeting_alert_start_no_meetings(self):
        """Test staging start meeting alerts when no meetings exist."""
        from alerts.util_alert_definitions import stage_meeting_alert
        from alerts.models import AlertType
        
        AlertType.objects.create(
            alert_typ="meeting_start",
            alert_typ_nm="Meeting Start",
            subject="Meeting Starting",
            body="A meeting is starting",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        result = stage_meeting_alert(True)
        
        assert result == "NONE TO STAGE"

    def test_stage_meeting_alert_end_no_meetings(self):
        """Test staging end meeting alerts when no meetings exist."""
        from alerts.util_alert_definitions import stage_meeting_alert
        from alerts.models import AlertType
        
        AlertType.objects.create(
            alert_typ="meeting_end",
            alert_typ_nm="Meeting End",
            subject="Meeting Ending",
            body="A meeting is ending",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        result = stage_meeting_alert(False)
        
        assert result == "NONE TO STAGE"

    def test_stage_meeting_alert_start_with_upcoming_meeting(self, default_user):
        """Test staging alerts for upcoming meetings."""
        from alerts.util_alert_definitions import stage_meeting_alert
        from alerts.models import AlertType, CommunicationChannelType
        from attendance.models import Meeting, MeetingType
        from scouting.models import Season
        
        # Create communication channel types
        CommunicationChannelType.objects.create(
            comm_typ="discord",
            comm_nm="Discord",
            void_ind="n"
        )
        
        AlertType.objects.create(
            alert_typ="meeting_start",
            alert_typ_nm="Meeting Start",
            subject="Meeting Starting",
            body="A meeting is starting",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        season = Season.objects.create(season="2024", game="Test Game", manual="Test Manual")
        meeting_type = MeetingType.objects.create(
            meeting_typ="reg",
            meeting_nm="Regular Meeting",
            void_ind="n"
        )
        
        # Create meeting starting in 10 minutes
        Meeting.objects.create(
            season=season,
            meeting_typ=meeting_type,
            title="Test Meeting",
            description="Test Description",
            start=timezone.now() + timedelta(minutes=10),
            end=timezone.now() + timedelta(hours=1),
            void_ind="n"
        )
        
        result = stage_meeting_alert(True)
        
        # Should have staged alerts
        assert result != "NONE TO STAGE"

    def test_stage_meeting_alert_end_with_ending_meeting(self, default_user):
        """Test staging alerts for ending meetings."""
        from alerts.util_alert_definitions import stage_meeting_alert
        from alerts.models import AlertType, CommunicationChannelType
        from attendance.models import Meeting, MeetingType
        from scouting.models import Season
        
        # Create communication channel types
        CommunicationChannelType.objects.create(
            comm_typ="discord",
            comm_nm="Discord",
            void_ind="n"
        )
        
        AlertType.objects.create(
            alert_typ="meeting_end",
            alert_typ_nm="Meeting End",
            subject="Meeting Ending",
            body="A meeting is ending",
            last_run=timezone.now() - timedelta(hours=1),
            void_ind="n"
        )
        
        season = Season.objects.create(season="2024", game="Test Game", manual="Test Manual")
        meeting_type = MeetingType.objects.create(
            meeting_typ="reg",
            meeting_nm="Regular Meeting",
            void_ind="n"
        )
        
        # Create meeting ending now (within the window)
        Meeting.objects.create(
            season=season,
            meeting_typ=meeting_type,
            title="Test Meeting",
            description="Test Description",
            start=timezone.now() - timedelta(hours=1),
            end=timezone.now() - timedelta(seconds=30),
            void_ind="n"
        )
        
        result = stage_meeting_alert(False)
        
        # Should have staged alerts
        assert result != "NONE TO STAGE"
