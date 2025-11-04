"""
Unit tests for UserService.

These tests validate the service layer's business logic with mocked repositories.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from user.services.user_service import UserService
from user.models import User


class TestUserService:
    """Test UserService business logic."""
    
    def test_get_user_info(self):
        """Test getting comprehensive user information."""
        # Arrange
        mock_user_repo = Mock()
        mock_permission_repo = Mock()
        
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.is_active = True
        mock_user.phone = "1234567890"
        mock_user.groups = []
        mock_user.phone_type = None
        mock_user.phone_type_id = None
        mock_user.img_id = None
        mock_user.img_ver = None
        mock_user.get_full_name.return_value = "Test User"
        
        mock_permissions = [Mock(codename="test_perm")]
        mock_links = [Mock(menu_name="Home")]
        
        mock_user_repo.get_by_id.return_value = mock_user
        mock_permission_repo.get_user_permissions.return_value = mock_permissions
        mock_permission_repo.get_accessible_links.return_value = mock_links
        
        service = UserService(
            user_repo=mock_user_repo,
            permission_repo=mock_permission_repo
        )
        
        # Act
        with patch('user.services.user_service.general.cloudinary.build_image_url') as mock_img:
            mock_img.return_value = "http://example.com/image.jpg"
            result = service.get_user_info(1)
        
        # Assert
        assert result["id"] == 1
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["is_active"] is True
        assert result["permissions"] == mock_permissions
        assert result["links"] == mock_links
        
        mock_user_repo.get_by_id.assert_called_once_with(1)
        mock_permission_repo.get_user_permissions.assert_called_once_with(mock_user)
    
    def test_get_users_active_only(self):
        """Test getting active users only."""
        # Arrange
        mock_user_repo = Mock()
        mock_users = [Mock(id=1), Mock(id=2)]
        mock_user_repo.filter_users.return_value = mock_users
        
        service = UserService(user_repo=mock_user_repo)
        
        # Act
        result = service.get_users(active=1, exclude_admin=False)
        
        # Assert
        assert result == mock_users
        mock_user_repo.filter_users.assert_called_once_with(
            active=True,
            exclude_admin=False
        )
    
    def test_get_users_exclude_admin(self):
        """Test getting users excluding admin."""
        # Arrange
        mock_user_repo = Mock()
        mock_users = [Mock(id=1)]
        mock_user_repo.filter_users.return_value = mock_users
        
        service = UserService(user_repo=mock_user_repo)
        
        # Act
        result = service.get_users(active=None, exclude_admin=True)
        
        # Assert
        assert result == mock_users
        mock_user_repo.filter_users.assert_called_once_with(
            active=None,
            exclude_admin=True
        )
    
    def test_update_user_basic_fields(self):
        """Test updating basic user fields."""
        # Arrange
        mock_user_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user_repo.get_by_username.return_value = mock_user
        mock_user_repo.update_user.return_value = mock_user
        
        service = UserService(user_repo=mock_user_repo)
        
        data = {
            "username": "testuser",
            "first_name": "New",
            "last_name": "Name",
            "email": "new@example.com",
            "discord_user_id": "12345",
            "phone": "1234567890",
            "phone_type_id": 1,
            "is_active": True
        }
        
        # Act
        result = service.update_user(data)
        
        # Assert
        assert result == mock_user
        mock_user_repo.get_by_username.assert_called_once_with("testuser")
        mock_user_repo.update_user.assert_called_once()
    
    def test_update_user_with_groups(self):
        """Test updating user with group changes."""
        # Arrange
        mock_user_repo = Mock()
        mock_permission_repo = Mock()
        
        mock_user = Mock(spec=User)
        mock_group1 = Mock(name="Group1")
        mock_group2 = Mock(name="Group2")
        
        mock_user_repo.get_by_username.return_value = mock_user
        mock_user_repo.update_user.return_value = mock_user
        mock_user_repo.get_user_groups.return_value = MagicMock(
            values_list=Mock(return_value=["OldGroup"])
        )
        mock_permission_repo.get_group_by_name.side_effect = [mock_group1, mock_group2]
        
        service = UserService(
            user_repo=mock_user_repo,
            permission_repo=mock_permission_repo
        )
        
        data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "is_active": True,
            "groups": [
                {"name": "Group1"},
                {"name": "Group2"}
            ]
        }
        
        # Act
        result = service.update_user(data)
        
        # Assert
        assert mock_user_repo.add_user_to_group.call_count == 2
    
    def test_get_users_in_group(self):
        """Test getting users in a specific group."""
        # Arrange
        mock_user_repo = Mock()
        mock_users = [Mock(id=1), Mock(id=2)]
        mock_user_repo.get_users_in_group.return_value = mock_users
        
        service = UserService(user_repo=mock_user_repo)
        
        # Act
        result = service.get_users_in_group("TestGroup")
        
        # Assert
        assert result == mock_users
        mock_user_repo.get_users_in_group.assert_called_once_with(
            "TestGroup",
            active_only=True
        )
    
    def test_get_users_with_permission(self):
        """Test getting users with a specific permission."""
        # Arrange
        mock_user_repo = Mock()
        mock_permission_repo = Mock()
        
        mock_permission = Mock()
        mock_group1 = Mock(name="Group1")
        mock_group2 = Mock(name="Group2")
        mock_permission.group_set.all.return_value = [mock_group1, mock_group2]
        
        mock_user1 = Mock(id=1)
        mock_user2 = Mock(id=2)
        
        mock_user_repo.get_users_in_group.side_effect = [
            [mock_user1],
            [mock_user2]
        ]
        
        mock_permission_repo.get_permission_by_codename.return_value = mock_permission
        
        service = UserService(
            user_repo=mock_user_repo,
            permission_repo=mock_permission_repo
        )
        
        # Act
        result = service.get_users_with_permission("test_perm")
        
        # Assert
        assert len(result) == 2
        assert mock_user1 in result
        assert mock_user2 in result
    
    def test_delete_phone_type_with_users_raises_error(self):
        """Test that deleting phone type with users raises error."""
        # Arrange
        mock_user_repo = Mock()
        mock_phone_type = Mock()
        
        mock_user_repo.get_phone_type_by_id.return_value = mock_phone_type
        mock_user_repo.phone_type_has_users.return_value = True
        
        service = UserService(user_repo=mock_user_repo)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Can't delete"):
            service.delete_phone_type(1)
    
    def test_delete_phone_type_without_users(self):
        """Test deleting phone type without users succeeds."""
        # Arrange
        mock_user_repo = Mock()
        mock_phone_type = Mock()
        
        mock_user_repo.get_phone_type_by_id.return_value = mock_phone_type
        mock_user_repo.phone_type_has_users.return_value = False
        
        service = UserService(user_repo=mock_user_repo)
        
        # Act
        service.delete_phone_type(1)
        
        # Assert
        mock_user_repo.delete_phone_type.assert_called_once_with(mock_phone_type)
    
    def test_run_security_audit(self):
        """Test running security audit."""
        # Arrange
        mock_user_repo = Mock()
        
        user_with_groups = Mock()
        user_with_groups.groups.exists.return_value = True
        
        user_without_groups = Mock()
        user_without_groups.groups.exists.return_value = False
        
        mock_user_repo.filter_users.return_value = [
            user_with_groups,
            user_without_groups
        ]
        
        service = UserService(user_repo=mock_user_repo)
        
        # Act
        result = service.run_security_audit()
        
        # Assert
        assert len(result) == 1
        assert user_with_groups in result
        assert user_without_groups not in result
