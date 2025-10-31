"""
Comprehensive tests for alerts app.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from rest_framework.test import force_authenticate
from django.utils.timezone import now


@pytest.mark.django_db
class TestAlertsUtil:
    """Tests for alerts utility functions."""

    def test_create_alert_basic(self, test_user):
        """Test creating a basic alert."""
        from alerts.util import create_alert
        from alerts.models import Alert
        
        alert = create_alert(
            test_user,
            "Test Subject",
            "Test Body",
            alert_url="http://test.com"
        )
        
        assert alert.id is not None
        assert alert.user == test_user
        assert alert.subject == "Test Subject"
        assert alert.body == "Test Body"
        assert alert.url == "http://test.com"
        assert alert.void_ind == "n"

    def test_create_alert_with_type(self, test_user):
        """Test creating an alert with alert type."""
        from alerts.util import create_alert
        from alerts.models import AlertType
        
        alert_type = AlertType.objects.create(
            alert_typ="test_type",
            alert_typ_nm="Test Type",
            last_run=now(),
            void_ind="n"
        )
        
        alert = create_alert(
            test_user,
            "Test Subject",
            "Test Body",
            alert_typ=alert_type
        )
        
        assert alert.alert_typ == alert_type

    def test_create_alert_truncates_long_body(self, test_user):
        """Test that alert body is truncated to 4000 characters."""
        from alerts.util import create_alert
        
        long_body = "x" * 5000
        alert = create_alert(
            test_user,
            "Test Subject",
            long_body
        )
        
        assert len(alert.body) == 4000

    def test_create_channel_send_for_comm_typ(self, test_user):
        """Test creating a channel send for communication type."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ
        from alerts.models import CommunicationChannelType, ChannelSend
        
        # Create communication type
        comm_type = CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test", "Body")
        channel_send = create_channel_send_for_comm_typ(alert, "email")
        
        assert channel_send.id is not None
        assert channel_send.comm_typ == comm_type
        assert channel_send.alert == alert
        assert channel_send.void_ind == "n"
        assert channel_send.tries == 0

    def test_send_alerts_no_pending(self):
        """Test send_alerts when no alerts are pending."""
        from alerts.util import send_alerts
        
        result = send_alerts()
        
        assert result == "NONE TO SEND"

    def test_send_alerts_email_success(self, test_user):
        """Test sending email alerts successfully."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, send_alerts
        from alerts.models import CommunicationChannelType
        
        # Create communication type
        CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test Email", "Body", alert_url="http://test.com")
        create_channel_send_for_comm_typ(alert, "email")
        
        with patch('alerts.util.send_message.send_email') as mock_send:
            result = send_alerts()
            
            mock_send.assert_called_once()
            assert "Email" in result
            assert test_user.get_full_name() in result

    def test_send_alerts_notification_success(self, test_user):
        """Test sending notification alerts successfully."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, send_alerts
        from alerts.models import CommunicationChannelType
        
        CommunicationChannelType.objects.create(
            comm_typ="notification",
            comm_nm="Notification",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test Notification", "Body")
        create_channel_send_for_comm_typ(alert, "notification")
        
        with patch('alerts.util.send_message.send_webpush', return_value="Webpush sent") as mock_send:
            result = send_alerts()
            
            mock_send.assert_called_once()
            assert "Webpush sent" in result

    def test_send_alerts_txt_with_phone(self, test_user):
        """Test sending text alerts when user has phone."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, send_alerts
        from alerts.models import CommunicationChannelType
        from user.models import PhoneType
        
        # Setup phone type
        phone_type = PhoneType.objects.create(
            carrier="Test",
            phone_type="@test.com"
        )
        test_user.phone = "1234567890"
        test_user.phone_type = phone_type
        test_user.save()
        
        CommunicationChannelType.objects.create(
            comm_typ="txt",
            comm_nm="Text",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test Text", "Body")
        create_channel_send_for_comm_typ(alert, "txt")
        
        with patch('alerts.util.send_message.send_email') as mock_send:
            result = send_alerts()
            
            mock_send.assert_called_once()
            assert "Phone" in result

    def test_send_alerts_txt_without_phone(self, test_user):
        """Test sending text alerts when user has no phone."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, send_alerts
        from alerts.models import CommunicationChannelType, ChannelSend
        
        CommunicationChannelType.objects.create(
            comm_typ="txt",
            comm_nm="Text",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test Text", "Body")
        cs = create_channel_send_for_comm_typ(alert, "txt")
        
        result = send_alerts()
        
        assert "Phone FAILED" in result
        cs.refresh_from_db()
        assert cs.tries == 1

    def test_send_alerts_discord(self, test_user):
        """Test sending discord alerts."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, send_alerts
        from alerts.models import CommunicationChannelType
        
        test_user.discord_user_id = "123456"
        test_user.save()
        
        CommunicationChannelType.objects.create(
            comm_typ="discord",
            comm_nm="Discord",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test Discord", "Body")
        create_channel_send_for_comm_typ(alert, "discord")
        
        with patch('alerts.util.send_message.send_discord_notification') as mock_send:
            result = send_alerts()
            
            mock_send.assert_called_once()
            assert "Discord" in result

    def test_send_alerts_message_not_configured(self, test_user):
        """Test sending message type (not configured)."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, send_alerts
        from alerts.models import CommunicationChannelType
        
        CommunicationChannelType.objects.create(
            comm_typ="message",
            comm_nm="Message",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test Message", "Body")
        create_channel_send_for_comm_typ(alert, "message")
        
        result = send_alerts()
        
        assert "message not configured" in result

    def test_send_alerts_exception_handling(self, test_user, system_user):
        """Test send_alerts exception handling."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, send_alerts
        from alerts.models import CommunicationChannelType, ChannelSend
        
        CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test", "Body")
        cs = create_channel_send_for_comm_typ(alert, "email")
        
        with patch('alerts.util.send_message.send_email', side_effect=Exception("Send failed")):
            result = send_alerts()
            
            assert "error occurred" in result
            cs.refresh_from_db()
            assert cs.tries == 1

    def test_send_alerts_max_tries(self, test_user):
        """Test that alerts with 4+ tries are not sent."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, send_alerts
        from alerts.models import CommunicationChannelType, ChannelSend
        
        CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test", "Body")
        cs = create_channel_send_for_comm_typ(alert, "email")
        cs.tries = 4
        cs.save()
        
        result = send_alerts()
        
        assert result == "NONE TO SEND"

    def test_get_user_alerts(self, test_user):
        """Test getting user alerts."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, get_user_alerts
        from alerts.models import CommunicationChannelType
        
        comm_type = CommunicationChannelType.objects.create(
            comm_typ="notification",
            comm_nm="Notification",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test Alert", "Body", alert_url="http://test.com")
        cs = create_channel_send_for_comm_typ(alert, "notification")
        
        alerts = get_user_alerts(test_user.id, "notification")
        
        assert len(alerts) == 1
        assert alerts[0]['id'] == alert.id
        assert alerts[0]['subject'] == "Test Alert"
        assert alerts[0]['body'] == "Body"
        assert alerts[0]['url'] == "http://test.com"

    def test_dismiss_alert(self, test_user):
        """Test dismissing an alert."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ, dismiss_alert
        from alerts.models import CommunicationChannelType, ChannelSend
        
        CommunicationChannelType.objects.create(
            comm_typ="notification",
            comm_nm="Notification",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test", "Body")
        cs = create_channel_send_for_comm_typ(alert, "notification")
        
        dismiss_alert(cs.id)
        
        cs.refresh_from_db()
        assert cs.dismissed_time is not None

    def test_send_alerts_to_role(self, test_user, admin_user):
        """Test sending alerts to users with a role."""
        from alerts.util import send_alerts_to_role
        from alerts.models import CommunicationChannelType, Alert, ChannelSend
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        
        # Setup permission
        content_type = ContentType.objects.get_for_model(Permission)
        permission = Permission.objects.create(
            codename='test_role',
            name='Test Role',
            content_type=content_type
        )
        group = Group.objects.create(name='TestGroup')
        group.permissions.add(permission)
        test_user.groups.add(group)
        test_user.is_active = True
        test_user.save()
        
        CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email",
            void_ind="n"
        )
        
        alerts = send_alerts_to_role(
            "Role Alert",
            "Alert for role members",
            "test_role",
            ["email"],
            url="http://test.com"
        )
        
        assert len(alerts) > 0
        assert alerts[0].subject == "Role Alert"
        assert ChannelSend.objects.filter(alert__in=alerts).exists()

    def test_send_alerts_to_role_ignore_user(self, test_user):
        """Test sending alerts to role ignoring specific user."""
        from alerts.util import send_alerts_to_role
        from alerts.models import CommunicationChannelType
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(Permission)
        permission = Permission.objects.create(
            codename='test_ignore',
            name='Test Ignore',
            content_type=content_type
        )
        group = Group.objects.create(name='IgnoreGroup')
        group.permissions.add(permission)
        test_user.groups.add(group)
        test_user.is_active = True
        test_user.save()
        
        CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email",
            void_ind="n"
        )
        
        alerts = send_alerts_to_role(
            "Role Alert",
            "Body",
            "test_ignore",
            ["email"],
            ignore_user_id=test_user.id
        )
        
        # Should be empty since we're ignoring the only user
        assert len(alerts) == 0

    def test_get_alert_type(self):
        """Test getting alert type."""
        from alerts.util import get_alert_type
        from alerts.models import AlertType
        
        alert_type = AlertType.objects.create(
            alert_typ="test_get",
            alert_typ_nm="Test Get",
            last_run=now(),
            void_ind="n"
        )
        
        result = get_alert_type("test_get")
        
        assert result == alert_type


@pytest.mark.django_db
class TestAlertsViews:
    """Tests for alerts views."""

    def test_stage_alerts_view_success(self, api_rf):
        """Test StageAlertsView GET success."""
        from alerts.views import StageAlertsView
        
        with patch('alerts.views.alerts.util_alert_definitions.stage_alerts', return_value="Staged successfully"):
            request = api_rf.get('/alerts/stage/')
            view = StageAlertsView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert "STAGE ALERTS" in str(response.data)
            assert "Staged successfully" in str(response.data)

    def test_stage_alerts_view_exception(self, api_rf, system_user):
        """Test StageAlertsView GET exception handling."""
        from alerts.views import StageAlertsView
        
        with patch('alerts.views.alerts.util_alert_definitions.stage_alerts', side_effect=Exception("Staging error")):
            request = api_rf.get('/alerts/stage/')
            view = StageAlertsView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_send_alerts_view_success(self, api_rf):
        """Test SendAlertsView GET success."""
        from alerts.views import SendAlertsView
        
        with patch('alerts.views.send_alerts', return_value="Sent successfully"):
            request = api_rf.get('/alerts/send/')
            view = SendAlertsView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert "SEND ALERTS" in str(response.data)
            assert "Sent successfully" in str(response.data)

    def test_send_alerts_view_exception(self, api_rf, system_user):
        """Test SendAlertsView GET exception handling."""
        from alerts.views import SendAlertsView
        
        with patch('alerts.views.send_alerts', side_effect=Exception("Send error")):
            request = api_rf.get('/alerts/send/')
            view = SendAlertsView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_run_alerts_view_success(self, api_rf):
        """Test RunAlertsView GET success."""
        from alerts.views import RunAlertsView
        
        with patch('alerts.views.alerts.util_alert_definitions.stage_alerts', return_value="Staged"), \
             patch('alerts.views.send_alerts', return_value="Sent"):
            request = api_rf.get('/alerts/run/')
            view = RunAlertsView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert "RUN ALERTS" in str(response.data)
            assert "STAGE ALERTS" in str(response.data)
            assert "SEND ALERTS" in str(response.data)

    def test_run_alerts_view_exception(self, api_rf, system_user):
        """Test RunAlertsView GET exception handling."""
        from alerts.views import RunAlertsView
        
        with patch('alerts.views.alerts.util_alert_definitions.stage_alerts', side_effect=Exception("Run error")):
            request = api_rf.get('/alerts/run/')
            view = RunAlertsView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_dismiss_alert_view_success(self, api_rf, test_user):
        """Test DismissAlertView GET success."""
        from alerts.views import DismissAlertView
        from alerts.util import create_alert, create_channel_send_for_comm_typ
        from alerts.models import CommunicationChannelType
        
        CommunicationChannelType.objects.create(
            comm_typ="notification",
            comm_nm="Notification",
            void_ind="n"
        )
        
        alert = create_alert(test_user, "Test", "Body")
        cs = create_channel_send_for_comm_typ(alert, "notification")
        
        request = api_rf.get(f'/alerts/dismiss/?channel_send_id={cs.id}')
        force_authenticate(request, user=test_user)
        view = DismissAlertView.as_view()
        response = view(request)
        
        assert response.status_code == 200
        cs.refresh_from_db()
        assert cs.dismissed_time is not None

    def test_dismiss_alert_view_exception(self, api_rf, test_user, system_user):
        """Test DismissAlertView GET exception handling."""
        from alerts.views import DismissAlertView
        
        with patch('alerts.views.dismiss_alert', side_effect=Exception("Dismiss error")):
            request = api_rf.get('/alerts/dismiss/?channel_send_id=999')
            force_authenticate(request, user=test_user)
            view = DismissAlertView.as_view()
            response = view(request)
            
            assert response.status_code == 200


@pytest.mark.django_db
class TestAlertsModels:
    """Tests for alerts models."""

    def test_communication_channel_type_str(self):
        """Test CommunicationChannelType string representation."""
        from alerts.models import CommunicationChannelType
        
        comm_type = CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email Channel",
            void_ind="n"
        )
        
        assert str(comm_type) == "email : Email Channel"

    def test_alert_str(self, test_user):
        """Test Alert string representation."""
        from alerts.models import Alert
        
        alert = Alert.objects.create(
            user=test_user,
            subject="Test Subject",
            body="Test Body",
            void_ind="n"
        )
        
        assert str(alert) == f"{alert.id} : Test Subject"

    def test_channel_send_str(self, test_user):
        """Test ChannelSend string representation."""
        from alerts.models import Alert, CommunicationChannelType, ChannelSend
        
        comm_type = CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email",
            void_ind="n"
        )
        alert = Alert.objects.create(
            user=test_user,
            subject="Test",
            body="Body",
            void_ind="n"
        )
        channel_send = ChannelSend.objects.create(
            comm_typ=comm_type,
            alert=alert,
            void_ind="n"
        )
        
        assert str(channel_send) == str(channel_send.id)
