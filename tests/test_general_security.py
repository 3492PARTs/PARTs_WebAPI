"""
Tests for general.security module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.response import Response

from general.security import (
    has_access,
    access_response,
    get_user_permissions,
    get_user_groups,
    ret_message,
)


@pytest.mark.django_db
class TestHasAccess:
    """Tests for has_access function."""

    def test_has_access_with_single_permission(self, test_user):
        """Test has_access with a single permission string."""
        # Mock at the service layer instead of get_user_permissions
        with patch("general.services.authorization_service.PermissionRepository") as MockRepo:
            mock_repo_instance = MagicMock()
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = [Mock()]  # Has permission
            mock_repo_instance.get_user_permissions.return_value = mock_queryset
            MockRepo.return_value = mock_repo_instance
            
            result = has_access(test_user.id, "test_permission")
            
            assert result is True

    def test_has_access_with_list_of_permissions(self, test_user):
        """Test has_access with a list of permissions."""
        # Mock at the service layer instead of get_user_permissions  
        with patch("general.services.authorization_service.PermissionRepository") as MockRepo:
            mock_repo_instance = MagicMock()
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = [Mock(), Mock()]  # Has permissions
            mock_repo_instance.get_user_permissions.return_value = mock_queryset
            MockRepo.return_value = mock_repo_instance
            
            result = has_access(test_user.id, ["perm1", "perm2"])
            
            assert result is True

    def test_has_access_no_permission(self, test_user):
        """Test has_access when user doesn't have permission."""
        # Mock at the service layer instead of get_user_permissions
        with patch("general.services.authorization_service.PermissionRepository") as MockRepo:
            mock_repo_instance = MagicMock()
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value = []  # No permissions
            mock_repo_instance.get_user_permissions.return_value = mock_queryset
            MockRepo.return_value = mock_repo_instance
            
            result = has_access(test_user.id, "missing_permission")
            
            assert result is False


@pytest.mark.django_db
class TestAccessResponse:
    """Tests for access_response function."""

    def test_access_response_with_permission(self, test_user):
        """Test access_response when user has permission."""
        mock_fun = Mock(return_value="success")
        
        # Patch at the service layer instead of the wrapper function
        with patch("general.services.authorization_service.AuthorizationService.has_access", return_value=True):
            result = access_response("test_endpoint", test_user.id, "test_perm", "error msg", mock_fun)
            
            assert result == "success"
            mock_fun.assert_called_once()

    def test_access_response_without_permission(self, test_user):
        """Test access_response when user doesn't have permission."""
        mock_fun = Mock()
        
        # Patch at the service layer instead of the wrapper function
        with patch("general.services.authorization_service.AuthorizationService.has_access", return_value=False):
            result = access_response("test_endpoint", test_user.id, "test_perm", "error msg", mock_fun)
            
            assert isinstance(result, Response)
            assert result.data["error"] is True
            assert "do not have access" in result.data["retMessage"]
            mock_fun.assert_not_called()

    def test_access_response_with_exception(self, test_user, default_user):
        """Test access_response when function raises exception."""
        mock_fun = Mock(side_effect=Exception("Test exception"))
        
        with patch("general.services.authorization_service.AuthorizationService.has_access", return_value=True), \
             patch("general.security.ErrorLog") as MockErrorLog:
            mock_log_instance = MagicMock()
            MockErrorLog.return_value = mock_log_instance
            
            result = access_response("test_endpoint", test_user.id, "test_perm", "error msg", mock_fun)
            
            assert isinstance(result, Response)
            assert result.data["error"] is True


@pytest.mark.django_db
class TestGetUserPermissions:
    """Tests for get_user_permissions function."""

    def test_get_user_permissions_as_queryset(self, test_user):
        """Test get_user_permissions returning queryset."""
        # Mock at the service layer
        with patch("general.services.authorization_service.PermissionRepository") as MockRepo:
            mock_repo_instance = MagicMock()
            mock_queryset = MagicMock()
            mock_repo_instance.get_user_permissions.return_value = mock_queryset
            MockRepo.return_value = mock_repo_instance
            
            result = get_user_permissions(test_user.id, as_list=False)
            
            assert result == mock_queryset

    def test_get_user_permissions_as_list(self, test_user):
        """Test get_user_permissions returning list."""
        perm1, perm2 = Mock(), Mock()
        # Mock at the service layer
        with patch("general.services.authorization_service.PermissionRepository") as MockRepo:
            mock_repo_instance = MagicMock()
            mock_queryset = MagicMock()
            mock_queryset.__iter__.return_value = iter([perm1, perm2])
            mock_repo_instance.get_user_permissions.return_value = mock_queryset
            MockRepo.return_value = mock_repo_instance
            
            result = get_user_permissions(test_user.id, as_list=True)
            
            assert result == [perm1, perm2]


@pytest.mark.django_db
class TestGetUserGroups:
    """Tests for get_user_groups function."""

    def test_get_user_groups(self, test_user):
        """Test get_user_groups returns user's groups."""
        with patch("general.security.User") as MockUser:
            mock_user = MagicMock()
            mock_groups = MagicMock()
            mock_user.groups.all.return_value = mock_groups
            MockUser.objects.get.return_value = mock_user
            
            result = get_user_groups(test_user.id)
            
            assert result == mock_groups
            MockUser.objects.get.assert_called_once_with(id=test_user.id)


@pytest.mark.django_db
class TestRetMessage:
    """Tests for ret_message function."""

    def test_ret_message_success(self):
        """Test ret_message for success case."""
        result = ret_message("Success message", error=False)
        
        assert isinstance(result, Response)
        assert result.data["retMessage"] == "Success message"
        assert result.data["error"] is False
        assert result.data["errorMessage"] == ""

    def test_ret_message_with_error_message(self):
        """Test ret_message with custom error message."""
        error_dict = {"field": "error"}
        result = ret_message("Message", error=False, error_message=error_dict)
        
        assert isinstance(result, Response)
        assert '"field": "error"' in result.data["errorMessage"]

    def test_ret_message_error_creates_log(self, test_user):
        """Test ret_message creates error log on error."""
        User = get_user_model()
        
        with patch("general.security.User") as MockUser:
            MockUser.objects.get.return_value = test_user
            MockUser.DoesNotExist = User.DoesNotExist
            
            with patch("general.security.ErrorLog") as MockErrorLog:
                mock_log_instance = MagicMock()
                MockErrorLog.return_value = mock_log_instance
                
                result = ret_message(
                    "Error message",
                    error=True,
                    path="/test/path",
                    user_id=test_user.id,
                    exception=Exception("Test"),
                )
                
                assert isinstance(result, Response)
                assert result.data["error"] is True
                MockErrorLog.assert_called()
                mock_log_instance.save.assert_called_once()

    def test_ret_message_error_user_not_found(self):
        """Test ret_message when user doesn't exist."""
        User = get_user_model()
        
        with patch("general.security.User") as MockUser:
            mock_default_user = MagicMock(username="default", first_name="", last_name="")
            
            def get_side_effect(id):
                if id == 999:
                    raise User.DoesNotExist()
                return mock_default_user
            
            MockUser.objects.get.side_effect = get_side_effect
            MockUser.DoesNotExist = User.DoesNotExist
            
            with patch("general.security.ErrorLog") as MockErrorLog:
                mock_log_instance = MagicMock()
                MockErrorLog.return_value = mock_log_instance
                
                result = ret_message(
                    "Error",
                    error=True,
                    path="/test",
                    user_id=999,
                    exception=Exception("Test"),
                )
                
                assert isinstance(result, Response)
                assert result.data["error"] is True

    def test_ret_message_error_log_save_fails(self, test_user):
        """Test ret_message when error log save fails."""
        User = get_user_model()
        
        with patch("general.security.User") as MockUser:
            MockUser.objects.get.return_value = test_user
            MockUser.DoesNotExist = User.DoesNotExist
            
            with patch("general.security.ErrorLog") as MockErrorLog:
                mock_log_instance = MagicMock()
                mock_log_instance.save.side_effect = [Exception("Save failed"), None]
                MockErrorLog.return_value = mock_log_instance
                
                result = ret_message(
                    "Error",
                    error=True,
                    path="/test",
                    user_id=test_user.id,
                    exception=Exception("Test"),
                )
                
                assert isinstance(result, Response)

    def test_ret_message_critical_error(self, test_user):
        """Test ret_message when both error log saves fail."""
        User = get_user_model()
        
        with patch("general.security.User") as MockUser:
            MockUser.objects.get.return_value = test_user
            MockUser.DoesNotExist = User.DoesNotExist
            
            with patch("general.security.ErrorLog") as MockErrorLog:
                mock_log_instance = MagicMock()
                mock_log_instance.save.side_effect = Exception("Critical save failed")
                MockErrorLog.return_value = mock_log_instance
                
                result = ret_message(
                    "Error",
                    error=True,
                    path="/test",
                    user_id=test_user.id,
                    exception=Exception("Test"),
                )
                
                assert isinstance(result, Response)
                assert "Critical Error" in result.data["retMessage"]
