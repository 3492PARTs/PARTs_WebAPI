"""
Unit tests for PermissionService.

These tests validate the service layer's permission business logic with mocked repositories.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from user.services.permission_service import PermissionService


class TestPermissionService:
    """Test PermissionService business logic."""
    
    def test_get_all_groups(self):
        """Test getting all groups."""
        # Arrange
        mock_repo = Mock()
        mock_groups = [Mock(name="Group1"), Mock(name="Group2")]
        mock_repo.get_all_groups.return_value = MagicMock(__iter__=lambda x: iter(mock_groups))
        
        service = PermissionService(permission_repo=mock_repo)
        
        # Act
        result = service.get_all_groups()
        
        # Assert
        assert len(result) == 2
        mock_repo.get_all_groups.assert_called_once()
    
    def test_save_group_new(self):
        """Test creating a new group."""
        # Arrange
        mock_repo = Mock()
        mock_group = Mock(id=1, name="NewGroup")
        mock_repo.create_group.return_value = mock_group
        
        service = PermissionService(permission_repo=mock_repo)
        
        data = {
            "id": None,
            "name": "NewGroup",
            "permissions": []
        }
        
        # Act
        result = service.save_group(data)
        
        # Assert
        assert result == mock_group
        mock_repo.create_group.assert_called_once_with("NewGroup")
    
    def test_save_group_existing(self):
        """Test updating an existing group."""
        # Arrange
        mock_repo = Mock()
        mock_group = Mock(id=1, name="OldName")
        mock_repo.get_group_by_id.return_value = mock_group
        mock_repo.update_group.return_value = mock_group
        mock_repo.get_group_permissions.return_value = MagicMock(
            values_list=Mock(return_value=[])
        )
        
        service = PermissionService(permission_repo=mock_repo)
        
        data = {
            "id": 1,
            "name": "NewName",
            "permissions": []
        }
        
        # Act
        result = service.save_group(data)
        
        # Assert
        assert result == mock_group
        mock_repo.get_group_by_id.assert_called_once_with(1)
        mock_repo.update_group.assert_called_once_with(mock_group, "NewName")
    
    def test_save_group_with_permissions(self):
        """Test saving group with permission changes."""
        # Arrange
        mock_repo = Mock()
        mock_group = Mock(id=1)
        mock_perm1 = Mock(id=1)
        mock_perm2 = Mock(id=2)
        
        mock_repo.create_group.return_value = mock_group
        mock_repo.get_group_permissions.return_value = MagicMock(
            values_list=Mock(return_value=[])
        )
        mock_repo.get_permission_by_id.side_effect = [mock_perm1, mock_perm2]
        
        service = PermissionService(permission_repo=mock_repo)
        
        data = {
            "id": None,
            "name": "TestGroup",
            "permissions": [
                {"id": 1},
                {"id": 2}
            ]
        }
        
        # Act
        result = service.save_group(data)
        
        # Assert
        assert mock_repo.add_permission_to_group.call_count == 2
    
    def test_delete_group(self):
        """Test deleting a group."""
        # Arrange
        mock_repo = Mock()
        mock_group = Mock(id=1)
        mock_repo.get_group_by_id.return_value = mock_group
        
        service = PermissionService(permission_repo=mock_repo)
        
        # Act
        with patch('user.services.permission_service.ScoutAuthGroup') as MockScoutAuth:
            MockScoutAuth.objects.get.side_effect = MockScoutAuth.DoesNotExist
            service.delete_group(1)
        
        # Assert
        mock_repo.delete_group.assert_called_once_with(mock_group)
    
    def test_delete_group_with_scout_auth(self):
        """Test deleting a group that has scout auth group."""
        # Arrange
        mock_repo = Mock()
        mock_group = Mock(id=1)
        mock_repo.get_group_by_id.return_value = mock_group
        
        service = PermissionService(permission_repo=mock_repo)
        
        # Act
        with patch('user.services.permission_service.ScoutAuthGroup') as MockScoutAuth:
            mock_scout_auth = Mock()
            MockScoutAuth.objects.get.return_value = mock_scout_auth
            service.delete_group(1)
        
        # Assert
        mock_scout_auth.delete.assert_called_once()
        mock_repo.delete_group.assert_called_once()
    
    def test_get_all_permissions(self):
        """Test getting all custom permissions."""
        # Arrange
        mock_repo = Mock()
        mock_perms = [Mock(id=1), Mock(id=2)]
        mock_repo.get_custom_permissions.return_value = MagicMock(__iter__=lambda x: iter(mock_perms))
        
        service = PermissionService(permission_repo=mock_repo)
        
        # Act
        result = service.get_all_permissions()
        
        # Assert
        assert len(result) == 2
        mock_repo.get_custom_permissions.assert_called_once()
    
    def test_save_permission_new(self):
        """Test creating a new permission."""
        # Arrange
        mock_repo = Mock()
        mock_perm = Mock(id=1)
        mock_repo.create_permission.return_value = mock_perm
        
        service = PermissionService(permission_repo=mock_repo)
        
        data = {
            "id": None,
            "name": "Test Permission",
            "codename": "test_perm"
        }
        
        # Act
        result = service.save_permission(data)
        
        # Assert
        assert result == mock_perm
        mock_repo.create_permission.assert_called_once_with(
            name="Test Permission",
            codename="test_perm"
        )
    
    def test_save_permission_existing(self):
        """Test updating an existing permission."""
        # Arrange
        mock_repo = Mock()
        mock_perm = Mock(id=1)
        mock_repo.get_permission_by_id.return_value = mock_perm
        mock_repo.update_permission.return_value = mock_perm
        
        service = PermissionService(permission_repo=mock_repo)
        
        data = {
            "id": 1,
            "name": "Updated Permission",
            "codename": "updated_perm"
        }
        
        # Act
        result = service.save_permission(data)
        
        # Assert
        assert result == mock_perm
        mock_repo.update_permission.assert_called_once_with(
            mock_perm,
            name="Updated Permission",
            codename="updated_perm"
        )
    
    def test_delete_permission(self):
        """Test deleting a permission."""
        # Arrange
        mock_repo = Mock()
        mock_perm = Mock(id=1)
        mock_repo.get_permission_by_id.return_value = mock_perm
        
        service = PermissionService(permission_repo=mock_repo)
        
        # Act
        service.delete_permission(1)
        
        # Assert
        mock_repo.delete_permission.assert_called_once_with(mock_perm)
    
    def test_get_all_links(self):
        """Test getting all navigation links."""
        # Arrange
        mock_repo = Mock()
        mock_links = [Mock(id=1), Mock(id=2)]
        mock_repo.get_all_links.return_value = MagicMock(__iter__=lambda x: iter(mock_links))
        
        service = PermissionService(permission_repo=mock_repo)
        
        # Act
        result = service.get_all_links()
        
        # Assert
        assert len(result) == 2
        mock_repo.get_all_links.assert_called_once()
    
    def test_save_link_new(self):
        """Test creating a new link."""
        # Arrange
        mock_repo = Mock()
        mock_link = Mock(id=1)
        mock_repo.create_link.return_value = mock_link
        
        service = PermissionService(permission_repo=mock_repo)
        
        data = {
            "id": None,
            "menu_name": "Test Link",
            "routerlink": "/test",
            "order": 1,
            "permission": {"id": 1}
        }
        
        # Act
        result = service.save_link(data)
        
        # Assert
        assert result == mock_link
        mock_repo.create_link.assert_called_once_with(
            menu_name="Test Link",
            routerlink="/test",
            order=1,
            permission_id=1
        )
    
    def test_save_link_existing(self):
        """Test updating an existing link."""
        # Arrange
        mock_repo = Mock()
        mock_link = Mock(id=1)
        mock_repo.get_link_by_id.return_value = mock_link
        mock_repo.update_link.return_value = mock_link
        
        service = PermissionService(permission_repo=mock_repo)
        
        data = {
            "id": 1,
            "menu_name": "Updated Link",
            "routerlink": "/updated",
            "order": 2,
            "permission": None
        }
        
        # Act
        result = service.save_link(data)
        
        # Assert
        assert result == mock_link
        mock_repo.update_link.assert_called_once()
    
    def test_delete_link(self):
        """Test deleting a link."""
        # Arrange
        mock_repo = Mock()
        mock_link = Mock(id=1)
        mock_repo.get_link_by_id.return_value = mock_link
        
        service = PermissionService(permission_repo=mock_repo)
        
        # Act
        service.delete_link(1)
        
        # Assert
        mock_repo.delete_link.assert_called_once_with(mock_link)
