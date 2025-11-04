"""
Unit tests for AuthorizationService.

These tests validate the authorization service's access control logic.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from rest_framework.response import Response
from general.services.authorization_service import AuthorizationService


class TestAuthorizationService:
    """Test AuthorizationService access control logic."""
    
    def test_has_access_with_single_permission_returns_true(self):
        """Test has_access returns True when user has the required permission."""
        # Arrange
        mock_permission_repo = Mock()
        mock_user_repo = Mock()
        
        mock_user = Mock(id=1)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_permissions = MagicMock()
        mock_permissions.filter.return_value = [Mock()]  # Has permission
        mock_permission_repo.get_user_permissions.return_value = mock_permissions
        
        service = AuthorizationService(
            permission_repo=mock_permission_repo,
            user_repo=mock_user_repo
        )
        
        # Act
        result = service.has_access(1, "test_permission")
        
        # Assert
        assert result is True
        mock_user_repo.get_by_id.assert_called_once_with(1)
        mock_permission_repo.get_user_permissions.assert_called_once_with(mock_user)
        mock_permissions.filter.assert_called_once_with(codename__in=["test_permission"])
    
    def test_has_access_with_list_of_permissions_returns_true(self):
        """Test has_access returns True when user has any of the required permissions."""
        # Arrange
        mock_permission_repo = Mock()
        mock_user_repo = Mock()
        
        mock_user = Mock(id=1)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_permissions = MagicMock()
        mock_permissions.filter.return_value = [Mock(), Mock()]  # Has permissions
        mock_permission_repo.get_user_permissions.return_value = mock_permissions
        
        service = AuthorizationService(
            permission_repo=mock_permission_repo,
            user_repo=mock_user_repo
        )
        
        # Act
        result = service.has_access(1, ["perm1", "perm2"])
        
        # Assert
        assert result is True
        mock_permissions.filter.assert_called_once_with(codename__in=["perm1", "perm2"])
    
    def test_has_access_without_permission_returns_false(self):
        """Test has_access returns False when user doesn't have permission."""
        # Arrange
        mock_permission_repo = Mock()
        mock_user_repo = Mock()
        
        mock_user = Mock(id=1)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_permissions = MagicMock()
        mock_permissions.filter.return_value = []  # No permissions
        mock_permission_repo.get_user_permissions.return_value = mock_permissions
        
        service = AuthorizationService(
            permission_repo=mock_permission_repo,
            user_repo=mock_user_repo
        )
        
        # Act
        result = service.has_access(1, "missing_permission")
        
        # Assert
        assert result is False
    
    def test_execute_with_access_check_executes_function_when_has_access(self):
        """Test execute_with_access_check runs function when user has access."""
        # Arrange
        mock_permission_repo = Mock()
        mock_user_repo = Mock()
        
        mock_user = Mock(id=1)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_permissions = MagicMock()
        mock_permissions.filter.return_value = [Mock()]  # Has permission
        mock_permission_repo.get_user_permissions.return_value = mock_permissions
        
        service = AuthorizationService(
            permission_repo=mock_permission_repo,
            user_repo=mock_user_repo
        )
        
        mock_function = Mock(return_value=Response({"data": "success"}))
        
        # Act
        result = service.execute_with_access_check(
            "test_endpoint",
            1,
            "test_perm",
            "error message",
            mock_function
        )
        
        # Assert
        mock_function.assert_called_once()
        assert result.data == {"data": "success"}
    
    def test_execute_with_access_check_returns_error_when_no_access(self):
        """Test execute_with_access_check returns error when user lacks access."""
        # Arrange
        mock_permission_repo = Mock()
        mock_user_repo = Mock()
        
        mock_user = Mock(id=1)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_permissions = MagicMock()
        mock_permissions.filter.return_value = []  # No permission
        mock_permission_repo.get_user_permissions.return_value = mock_permissions
        
        service = AuthorizationService(
            permission_repo=mock_permission_repo,
            user_repo=mock_user_repo
        )
        
        mock_function = Mock()
        
        # Act
        result = service.execute_with_access_check(
            "test_endpoint",
            1,
            "test_perm",
            "error message",
            mock_function
        )
        
        # Assert
        mock_function.assert_not_called()
        assert result.data["error"] is True
        assert "do not have access" in result.data["retMessage"]
    
    def test_execute_with_access_check_handles_exception(self):
        """Test execute_with_access_check handles exceptions from function."""
        # Arrange
        mock_permission_repo = Mock()
        mock_user_repo = Mock()
        
        mock_user = Mock(id=1)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_permissions = MagicMock()
        mock_permissions.filter.return_value = [Mock()]  # Has permission
        mock_permission_repo.get_user_permissions.return_value = mock_permissions
        
        service = AuthorizationService(
            permission_repo=mock_permission_repo,
            user_repo=mock_user_repo
        )
        
        mock_function = Mock(side_effect=Exception("Test exception"))
        
        # Act
        with patch('general.services.authorization_service.User'):
            result = service.execute_with_access_check(
                "test_endpoint",
                1,
                "test_perm",
                "error message",
                mock_function
            )
        
        # Assert
        assert result.data["error"] is True
    
    def test_get_user_permissions(self):
        """Test getting user permissions."""
        # Arrange
        mock_permission_repo = Mock()
        mock_user_repo = Mock()
        
        mock_user = Mock(id=1)
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_permissions = [Mock(codename="perm1"), Mock(codename="perm2")]
        mock_permission_repo.get_user_permissions.return_value = mock_permissions
        
        service = AuthorizationService(
            permission_repo=mock_permission_repo,
            user_repo=mock_user_repo
        )
        
        # Act
        result = service.get_user_permissions(1)
        
        # Assert
        assert result == mock_permissions
        mock_user_repo.get_by_id.assert_called_once_with(1)
        mock_permission_repo.get_user_permissions.assert_called_once_with(mock_user)
    
    def test_initialization_with_default_repos(self):
        """Test service initializes with default repositories."""
        # Act
        with patch('general.services.authorization_service.PermissionRepository') as MockPermRepo, \
             patch('general.services.authorization_service.UserRepository') as MockUserRepo:
            service = AuthorizationService()
        
        # Assert
        MockPermRepo.assert_called_once()
        MockUserRepo.assert_called_once()
    
    def test_initialization_with_custom_repos(self):
        """Test service initializes with custom repositories."""
        # Arrange
        mock_perm_repo = Mock()
        mock_user_repo = Mock()
        
        # Act
        service = AuthorizationService(
            permission_repo=mock_perm_repo,
            user_repo=mock_user_repo
        )
        
        # Assert
        assert service.permission_repo == mock_perm_repo
        assert service.user_repo == mock_user_repo
