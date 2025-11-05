"""
Comprehensive tests for Alerts model methods to increase coverage.
"""
import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestAlertsModelStringMethods:
    """Test __str__ methods for alerts app models."""
    
    def test_communication_channel_type_str(self):
        """Test CommunicationChannelType __str__ method."""
        from alerts.models import CommunicationChannelType
        
        channel = CommunicationChannelType.objects.create(
            comm_typ="email",
            comm_nm="Email Notifications"
        )
        str_result = str(channel)
        assert "email" in str_result
        assert "Email Notifications" in str_result
    
    def test_alert_type_str(self):
        """Test AlertType __str__ method."""
        from alerts.models import AlertType
        
        alert_type = AlertType.objects.create(
            alert_typ="meeting_reminder",
            alert_typ_nm="Meeting Reminder",
            subject="Don't forget the meeting",
            body="Meeting tomorrow at 3pm",
            last_run=timezone.now()
        )
        
        str_result = str(alert_type)
        assert "meeting_reminder" in str_result
        assert "Meeting Reminder" in str_result
    
    def test_alert_str(self):
        """Test Alert __str__ method."""
        from alerts.models import Alert
        from user.models import User
        
        user = User.objects.create_user(
            username="alertuser",
            email="alert@test.com",
            password="pass123"
        )
        
        alert = Alert.objects.create(
            user=user,
            subject="Test Alert",
            body="This is a test alert"
        )
        
        str_result = str(alert)
        assert str(alert.id) in str_result
        assert "Test Alert" in str_result
    
    def test_channel_send_str(self):
        """Test ChannelSend __str__ method."""
        from alerts.models import ChannelSend, Alert, CommunicationChannelType
        from user.models import User
        
        user = User.objects.create_user(
            username="channeluser",
            email="channel@test.com",
            password="pass123"
        )
        
        channel = CommunicationChannelType.objects.create(
            comm_typ="sms",
            comm_nm="SMS Notifications"
        )
        
        alert = Alert.objects.create(
            user=user,
            subject="Channel Test",
            body="Test channel send"
        )
        
        channel_send = ChannelSend.objects.create(
            comm_typ=channel,
            alert=alert
        )
        
        str_result = str(channel_send)
        assert str(channel_send.id) in str_result
    
    def test_alerted_resource_str(self):
        """Test AlertedResource __str__ method."""
        from alerts.models import AlertedResource, AlertType
        
        alert_type = AlertType.objects.create(
            alert_typ="resource_alert",
            alert_typ_nm="Resource Alert",
            last_run=timezone.now()
        )
        
        alerted_resource = AlertedResource.objects.create(
            alert_typ=alert_type,
            foreign_id="12345"
        )
        
        str_result = str(alerted_resource)
        assert str(alerted_resource.id) in str_result
        assert "12345" in str_result


@pytest.mark.django_db
class TestAlertsModelFields:
    """Test alerts model field behaviors."""
    
    def test_communication_channel_type_void_default(self):
        """Test CommunicationChannelType void_ind default value."""
        from alerts.models import CommunicationChannelType
        
        channel = CommunicationChannelType.objects.create(
            comm_typ="discord",
            comm_nm="Discord Notifications"
        )
        
        assert channel.void_ind == "n"
    
    def test_alert_type_void_default(self):
        """Test AlertType void_ind default value."""
        from alerts.models import AlertType
        
        alert_type = AlertType.objects.create(
            alert_typ="test_type",
            alert_typ_nm="Test Type",
            last_run=timezone.now()
        )
        
        assert alert_type.void_ind == "n"
    
    def test_alert_staged_time_default(self):
        """Test Alert staged_time default value."""
        from alerts.models import Alert
        from user.models import User
        
        user = User.objects.create_user(
            username="timeuser",
            email="time@test.com",
            password="pass123"
        )
        
        alert = Alert.objects.create(
            user=user,
            subject="Time Test",
            body="Testing default time"
        )
        
        # staged_time should be set automatically
        assert alert.staged_time is not None
        assert alert.void_ind == "n"
    
    def test_channel_send_defaults(self):
        """Test ChannelSend default values."""
        from alerts.models import ChannelSend, Alert, CommunicationChannelType
        from user.models import User
        
        user = User.objects.create_user(
            username="defaultuser",
            email="default@test.com",
            password="pass123"
        )
        
        channel = CommunicationChannelType.objects.create(
            comm_typ="webpush",
            comm_nm="Web Push Notifications"
        )
        
        alert = Alert.objects.create(
            user=user,
            subject="Default Test",
            body="Testing defaults"
        )
        
        channel_send = ChannelSend.objects.create(
            comm_typ=channel,
            alert=alert
        )
        
        assert channel_send.tries == 0
        assert channel_send.void_ind == "n"
        assert channel_send.sent_time is None
        assert channel_send.dismissed_time is None
    
    def test_alerted_resource_time_default(self):
        """Test AlertedResource time default value."""
        from alerts.models import AlertedResource
        
        resource = AlertedResource.objects.create(
            foreign_id="67890"
        )
        
        assert resource.time is not None
        assert resource.void_ind == "n"
