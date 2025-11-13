"""
Unit tests for user use cases.

These tests demonstrate how clean architecture enables
testing business logic without Django's test framework.
"""
import pytest
from unittest.mock import MagicMock, Mock
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from core.use_cases.user_use_cases import (
    GetUserUseCase,
    GetUsersUseCase,
    CreateUserUseCase,
    UpdateUserUseCase,
    CheckUserAccessUseCase,
)
from core.dto.user_dto import CreateUserDTO, UpdateUserDTO, UserDTO
from user.models import User


class TestGetUserUseCase:
    """Tests for GetUserUseCase."""
    
    def test_execute_returns_user_dto(self):
        """Test that execute returns a properly formatted UserDTO."""
        # Arrange
        mock_repo = MagicMock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.is_active = True
        mock_user.phone = "1234567890"
        mock_user.discord_user_id = "discord123"
        mock_user.phone_type_id = 1
        mock_user.img_id = None
        mock_user.img_ver = None
        mock_user.get_full_name.return_value = "Test User"
        
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.get_user_permissions.return_value = []
        mock_repo.get_user_groups.return_value = []
        
        use_case = GetUserUseCase(mock_repo)
        
        # Act
        result = use_case.execute(1)
        
        # Assert
        assert isinstance(result, UserDTO)
        assert result.id == 1
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.first_name == "Test"
        assert result.last_name == "User"
        assert result.name == "Test User"
        assert result.is_active is True
        
        mock_repo.get_by_id.assert_called_once_with(1)
    
    def test_execute_raises_when_user_not_found(self):
        """Test that execute raises ObjectDoesNotExist when user not found."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        
        use_case = GetUserUseCase(mock_repo)
        
        # Act & Assert
        with pytest.raises(ObjectDoesNotExist) as exc_info:
            use_case.execute(999)
        
        assert "User with id 999 not found" in str(exc_info.value)
        mock_repo.get_by_id.assert_called_once_with(999)
    
    def test_execute_includes_permissions_and_groups(self):
        """Test that execute includes user permissions and groups."""
        # Arrange
        mock_repo = MagicMock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.is_active = True
        mock_user.phone = None
        mock_user.discord_user_id = None
        mock_user.phone_type_id = None
        mock_user.img_id = None
        mock_user.img_ver = None
        mock_user.get_full_name.return_value = "Test User"
        
        mock_permission = Mock()
        mock_permission.id = 1
        mock_permission.name = "Can view users"
        mock_permission.codename = "view_user"
        
        mock_group = Mock()
        mock_group.id = 1
        mock_group.name = "Admins"
        
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.get_user_permissions.return_value = [mock_permission]
        mock_repo.get_user_groups.return_value = [mock_group]
        
        use_case = GetUserUseCase(mock_repo)
        
        # Act
        result = use_case.execute(1)
        
        # Assert
        assert len(result.permissions) == 1
        assert result.permissions[0]["id"] == 1
        assert result.permissions[0]["codename"] == "view_user"
        
        assert len(result.groups) == 1
        assert result.groups[0]["id"] == 1
        assert result.groups[0]["name"] == "Admins"


class TestCreateUserUseCase:
    """Tests for CreateUserUseCase."""
    
    def test_execute_creates_user_successfully(self):
        """Test successful user creation."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_email.return_value = None
        mock_repo.get_by_username.return_value = None
        
        mock_created_user = Mock(spec=User)
        mock_created_user.id = 1
        mock_created_user.username = "newuser"
        mock_created_user.email = "new@example.com"
        mock_created_user.first_name = "New"
        mock_created_user.last_name = "User"
        mock_created_user.is_active = False
        mock_created_user.get_full_name.return_value = "New User"
        
        mock_repo.create.return_value = mock_created_user
        
        use_case = CreateUserUseCase(mock_repo)
        
        dto = CreateUserDTO(
            username="newuser",
            email="new@example.com",
            password="SecurePassword123!",
            first_name="New",
            last_name="User"
        )
        
        # Act
        result = use_case.execute(dto)
        
        # Assert
        assert isinstance(result, UserDTO)
        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.is_active is False  # Initially inactive
        
        mock_repo.get_by_email.assert_called_once_with("new@example.com")
        mock_repo.get_by_username.assert_called_once_with("newuser")
        mock_repo.create.assert_called_once()
    
    def test_execute_raises_when_email_exists(self):
        """Test that execute raises ValueError when email already exists."""
        # Arrange
        mock_repo = MagicMock()
        mock_existing_user = Mock(spec=User)
        mock_repo.get_by_email.return_value = mock_existing_user
        
        use_case = CreateUserUseCase(mock_repo)
        
        dto = CreateUserDTO(
            username="newuser",
            email="existing@example.com",
            password="SecurePassword123!",
            first_name="New",
            last_name="User"
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(dto)
        
        assert "User already exists with that email" in str(exc_info.value)
    
    def test_execute_raises_when_username_exists(self):
        """Test that execute raises ValueError when username already exists."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_email.return_value = None
        mock_existing_user = Mock(spec=User)
        mock_repo.get_by_username.return_value = mock_existing_user
        
        use_case = CreateUserUseCase(mock_repo)
        
        dto = CreateUserDTO(
            username="existinguser",
            email="new@example.com",
            password="SecurePassword123!",
            first_name="New",
            last_name="User"
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(dto)
        
        assert "User already exists with that username" in str(exc_info.value)


class TestUpdateUserUseCase:
    """Tests for UpdateUserUseCase."""
    
    def test_execute_updates_user_fields(self):
        """Test that execute updates user fields correctly."""
        # Arrange
        mock_repo = MagicMock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "old@example.com"
        mock_user.first_name = "Old"
        mock_user.last_name = "Name"
        mock_user.is_active = True
        mock_user.phone = None
        mock_user.discord_user_id = None
        mock_user.phone_type_id = None
        mock_user.get_full_name.return_value = "New Name"
        
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.get_user_groups.return_value = []
        
        use_case = UpdateUserUseCase(mock_repo)
        
        dto = UpdateUserDTO(
            user_id=1,
            first_name="New",
            email="new@example.com",
            phone="1234567890"
        )
        
        # Act
        result = use_case.execute(dto)
        
        # Assert
        assert result.email == "new@example.com"
        assert result.first_name == "New"
        assert result.phone == "1234567890"
        
        mock_repo.get_by_id.assert_called_once_with(1)
        mock_user.save.assert_called_once()
    
    def test_execute_raises_when_user_not_found(self):
        """Test that execute raises ObjectDoesNotExist when user not found."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        
        use_case = UpdateUserUseCase(mock_repo)
        
        dto = UpdateUserDTO(user_id=999, first_name="New")
        
        # Act & Assert
        with pytest.raises(ObjectDoesNotExist) as exc_info:
            use_case.execute(dto)
        
        assert "User with id 999 not found" in str(exc_info.value)
    
    def test_execute_updates_groups(self):
        """Test that execute updates user groups correctly."""
        # Arrange
        mock_repo = MagicMock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.is_active = True
        mock_user.phone = None
        mock_user.discord_user_id = None
        mock_user.phone_type_id = None
        mock_user.get_full_name.return_value = "Test User"
        
        mock_group = Mock()
        mock_group.name = "OldGroup"
        
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.get_user_groups.return_value = [mock_group]
        
        use_case = UpdateUserUseCase(mock_repo)
        
        dto = UpdateUserDTO(
            user_id=1,
            groups=["NewGroup"]
        )
        
        # Act
        result = use_case.execute(dto)
        
        # Assert
        mock_repo.add_user_to_groups.assert_called_once_with(1, ["NewGroup"])
        mock_repo.remove_user_from_groups.assert_called_once_with(1, ["OldGroup"])


class TestCheckUserAccessUseCase:
    """Tests for CheckUserAccessUseCase."""
    
    def test_execute_grants_access_when_user_has_permission(self):
        """Test that execute grants access when user has required permission."""
        # Arrange
        mock_repo = MagicMock()
        
        mock_permission = Mock()
        mock_permission.codename = "admin"
        
        mock_repo.get_user_permissions.return_value = [mock_permission]
        
        use_case = CheckUserAccessUseCase(mock_repo)
        
        # Act
        result = use_case.execute(1, ["admin"])
        
        # Assert
        assert result is True
    
    def test_execute_denies_access_when_user_lacks_permission(self):
        """Test that execute denies access when user lacks permission."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_user_permissions.return_value = []
        
        use_case = CheckUserAccessUseCase(mock_repo)
        
        # Act
        result = use_case.execute(1, ["admin"])
        
        # Assert
        assert result is False
    
    def test_execute_grants_access_with_any_permission(self):
        """Test that execute grants access when user has any of the required permissions."""
        # Arrange
        mock_repo = MagicMock()
        
        mock_permission = Mock()
        mock_permission.codename = "view_user"
        
        mock_repo.get_user_permissions.return_value = [mock_permission]
        
        use_case = CheckUserAccessUseCase(mock_repo)
        
        # Act
        result = use_case.execute(1, ["admin", "view_user", "edit_user"])
        
        # Assert
        assert result is True
    
    def test_execute_grants_access_when_no_permissions_required(self):
        """Test that execute grants access when no permissions are required."""
        # Arrange
        mock_repo = MagicMock()
        
        use_case = CheckUserAccessUseCase(mock_repo)
        
        # Act
        result = use_case.execute(1, [])
        
        # Assert
        assert result is True
        # Repo should not be called when no permissions required
        mock_repo.get_user_permissions.assert_not_called()
