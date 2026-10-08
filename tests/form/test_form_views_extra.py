"""
Extra coverage for form/views.py line 200.
Line 200: form.util.send_email_notification(response) called for 'team-app' / 'team-cntct'.
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestSaveAnswersEmailNotification:
    """Line 200: send_email_notification is called for team-app / team-cntct forms."""

    url = "/form/save-answers/"

    def test_team_app_triggers_email_notification(self, api_client, test_user):
        """Line 200: form_typ=='team-app' → send_email_notification called."""
        api_client.force_authenticate(user=test_user)
        mock_response = MagicMock()

        with patch("form.views.form.util.save_answers", return_value=mock_response) as mock_save, \
             patch("form.views.form.util.send_email_notification") as mock_notify, \
             patch("form.views.SaveResponseSerializer") as MockSerializer:
            instance = MockSerializer.return_value
            instance.is_valid.return_value = True
            instance.validated_data = {
                "form_typ": "team-app",
                "response_id": None,
                "time": "2099-01-01T00:00:00Z",
                "archive_ind": "n",
                "answers": [],
            }
            response = api_client.post(
                self.url,
                {"form_typ": "team-app"},
                format="json",
            )

        mock_notify.assert_called_once_with(mock_response)
        assert response.status_code == 200

    def test_team_cntct_triggers_email_notification(self, api_client, test_user):
        """Line 200: form_typ=='team-cntct' → send_email_notification called."""
        api_client.force_authenticate(user=test_user)
        mock_response = MagicMock()

        with patch("form.views.form.util.save_answers", return_value=mock_response) as mock_save, \
             patch("form.views.form.util.send_email_notification") as mock_notify, \
             patch("form.views.SaveResponseSerializer") as MockSerializer:
            instance = MockSerializer.return_value
            instance.is_valid.return_value = True
            instance.validated_data = {
                "form_typ": "team-cntct",
                "response_id": None,
                "time": "2099-01-01T00:00:00Z",
                "archive_ind": "n",
                "answers": [],
            }
            response = api_client.post(
                self.url,
                {"form_typ": "team-cntct"},
                format="json",
            )

        mock_notify.assert_called_once_with(mock_response)
        assert response.status_code == 200

    def test_other_form_typ_no_email_notification(self, api_client, test_user):
        """Line 199 condition False: no send_email_notification for other form types."""
        api_client.force_authenticate(user=test_user)
        mock_response = MagicMock()

        with patch("form.views.form.util.save_answers", return_value=mock_response), \
             patch("form.views.form.util.send_email_notification") as mock_notify, \
             patch("form.views.SaveResponseSerializer") as MockSerializer:
            instance = MockSerializer.return_value
            instance.is_valid.return_value = True
            instance.validated_data = {
                "form_typ": "other",
                "response_id": None,
                "time": "2099-01-01T00:00:00Z",
                "archive_ind": "n",
                "answers": [],
            }
            response = api_client.post(
                self.url,
                {"form_typ": "other"},
                format="json",
            )

        mock_notify.assert_not_called()
        assert response.status_code == 200
