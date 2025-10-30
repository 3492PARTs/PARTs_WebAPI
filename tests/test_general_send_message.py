"""
Tests for general.send_message module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pywebpush import WebPushException

from general.send_message import (
    send_email,
    send_discord_notification,
    send_webpush,
    add_test_env_subject,
)


class TestSendEmail:
    """Tests for send_email function."""

    def test_send_email_single_recipient(self):
        """Test sending email to single recipient."""
        with patch("general.send_message.get_template") as mock_get_template, \
             patch("general.send_message.EmailMultiAlternatives") as MockEmail, \
             patch("general.send_message.add_test_env_subject", return_value="Test Subject"):
            
            mock_plaintext = MagicMock()
            mock_plaintext.render.return_value = "Plain text"
            mock_html = MagicMock()
            mock_html.render.return_value = "<html>HTML</html>"
            mock_get_template.side_effect = [mock_plaintext, mock_html]
            
            mock_email_instance = MagicMock()
            MockEmail.return_value = mock_email_instance
            
            send_email("test@example.com", "Subject", "template_name", {"key": "value"})
            
            MockEmail.assert_called_once()
            mock_email_instance.attach_alternative.assert_called_once_with("<html>HTML</html>", "text/html")
            mock_email_instance.send.assert_called_once()

    def test_send_email_multiple_recipients(self):
        """Test sending email to multiple recipients."""
        with patch("general.send_message.get_template") as mock_get_template, \
             patch("general.send_message.EmailMultiAlternatives") as MockEmail, \
             patch("general.send_message.add_test_env_subject", return_value="Test Subject"):
            
            mock_plaintext = MagicMock()
            mock_plaintext.render.return_value = "Plain text"
            mock_html = MagicMock()
            mock_html.render.return_value = "<html>HTML</html>"
            mock_get_template.side_effect = [mock_plaintext, mock_html]
            
            mock_email_instance = MagicMock()
            MockEmail.return_value = mock_email_instance
            
            send_email(["test1@example.com", "test2@example.com"], "Subject", "template", {})
            
            mock_email_instance.send.assert_called_once()


class TestSendDiscordNotification:
    """Tests for send_discord_notification function."""

    def test_send_discord_notification_success(self):
        """Test successful Discord notification."""
        with patch("general.send_message.requests.post") as mock_post, \
             patch("general.send_message.settings") as mock_settings, \
             patch("general.send_message.add_test_env_subject", return_value="Test Message"):
            
            mock_settings.DISCORD_NOTIFICATION_WEBHOOK = "https://discord.webhook"
            mock_response = MagicMock()
            mock_response.ok = True
            mock_post.return_value = mock_response
            
            send_discord_notification("Test message")
            
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]["json"]["content"] == "Test Message"

    def test_send_discord_notification_failure(self):
        """Test Discord notification failure."""
        with patch("general.send_message.requests.post") as mock_post, \
             patch("general.send_message.settings") as mock_settings, \
             patch("general.send_message.add_test_env_subject", return_value="Test Message"):
            
            mock_settings.DISCORD_NOTIFICATION_WEBHOOK = "https://discord.webhook"
            mock_response = MagicMock()
            mock_response.ok = False
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception, match="discord sending issue"):
                send_discord_notification("Test message")


class TestSendWebpush:
    """Tests for send_webpush function."""

    def test_send_webpush_success(self):
        """Test successful web push notification."""
        mock_user = MagicMock()
        
        with patch("general.send_message.send_user_notification") as mock_send, \
             patch("general.send_message.add_test_env_subject", return_value="Test Subject"):
            
            result = send_webpush(mock_user, "Subject", "Body text", 123)
            
            assert "Successfully sent Webpush" in result
            mock_send.assert_called_once()

    def test_send_webpush_exception(self):
        """Test web push with exception."""
        mock_user = MagicMock()
        
        with patch("general.send_message.send_user_notification") as mock_send, \
             patch("general.send_message.add_test_env_subject", return_value="Test Subject"), \
             patch("general.send_message.ret_message") as mock_ret_message:
            
            mock_send.side_effect = WebPushException("Push failed")
            
            result = send_webpush(mock_user, "Subject", "Body", 123)
            
            assert "error occurred" in result
            mock_ret_message.assert_called_once()

    def test_send_webpush_long_body(self):
        """Test web push with long body text."""
        mock_user = MagicMock()
        long_body = "x" * 5000
        
        with patch("general.send_message.send_user_notification") as mock_send, \
             patch("general.send_message.add_test_env_subject", return_value="Test"):
            
            send_webpush(mock_user, "Subject", long_body, 1)
            
            # Check that body is truncated in the payload
            call_args = mock_send.call_args
            payload = call_args[1]["payload"]
            assert len(payload["notification"]["body"]) == 3500


class TestAddTestEnvSubject:
    """Tests for add_test_env_subject function."""

    def test_add_test_env_subject_main(self):
        """Test add_test_env_subject in main environment."""
        with patch("general.send_message.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "main"
            result = add_test_env_subject("My Subject")
            assert result == "My Subject"

    def test_add_test_env_subject_test(self):
        """Test add_test_env_subject in test environment."""
        with patch("general.send_message.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "test"
            result = add_test_env_subject("My Subject")
            assert "TEST ENVIRONMENT" in result
            assert "test" in result
            assert "My Subject" in result

    def test_add_test_env_subject_dev(self):
        """Test add_test_env_subject in dev environment."""
        with patch("general.send_message.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "dev"
            result = add_test_env_subject("My Subject")
            assert "TEST ENVIRONMENT" in result
            assert "dev" in result
