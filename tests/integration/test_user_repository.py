"""
Integration tests for user repository.

These tests verify that the repository correctly interacts
with Django's ORM and database.
"""
import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from infrastructure.repositories.user_repository import DjangoUserRepository
from user.models import User


@pytest.mark.django_db
class TestDjangoUserRepository:
    """Integration tests for DjangoUserRepository."""
    
    def test_get_by_id_returns_user(self):
        """Test that get_by_id returns the correct user."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_by_id(user.id)
        
        # Assert
        assert result is not None
        assert result.id == user.id
        assert result.username == "testuser"
        assert result.email == "test@example.com"
    
    def test_get_by_id_returns_none_when_not_found(self):
        """Test that get_by_id returns None when user doesn't exist."""
        # Arrange
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_by_id(99999)
        
        # Assert
        assert result is None
    
    def test_get_by_username_returns_user(self):
        """Test that get_by_username returns the correct user."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_by_username("testuser")
        
        # Assert
        assert result is not None
        assert result.id == user.id
        assert result.username == "testuser"
    
    def test_get_by_username_is_case_insensitive(self):
        """Test that get_by_username is case insensitive."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_by_username("TESTUSER")
        
        # Assert
        assert result is not None
        assert result.id == user.id
    
    def test_get_by_email_returns_user(self):
        """Test that get_by_email returns the correct user."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_by_email("test@example.com")
        
        # Assert
        assert result is not None
        assert result.id == user.id
        assert result.email == "test@example.com"
    
    def test_get_by_email_is_case_insensitive(self):
        """Test that get_by_email is case insensitive."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_by_email("TEST@EXAMPLE.COM")
        
        # Assert
        assert result is not None
        assert result.id == user.id
    
    def test_get_all_returns_all_users(self):
        """Test that get_all returns all users."""
        # Arrange
        User.objects.create(username="user1", email="user1@example.com", first_name="A", last_name="User")
        User.objects.create(username="user2", email="user2@example.com", first_name="B", last_name="User")
        User.objects.create(username="user3", email="user3@example.com", first_name="C", last_name="User")
        
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_all()
        
        # Assert
        assert result.count() == 3
    
    def test_create_creates_new_user(self):
        """Test that create creates a new user."""
        # Arrange
        repo = DjangoUserRepository()
        
        # Act
        user = repo.create(
            username="newuser",
            email="new@example.com",
            first_name="New",
            last_name="User"
        )
        
        # Assert
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert User.objects.filter(username="newuser").exists()
    
    def test_update_updates_user_fields(self):
        """Test that update modifies user fields."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="old@example.com",
            first_name="Old",
            last_name="Name"
        )
        repo = DjangoUserRepository()
        
        # Act
        updated_user = repo.update(
            user.id,
            first_name="New",
            email="new@example.com"
        )
        
        # Assert
        assert updated_user.first_name == "New"
        assert updated_user.email == "new@example.com"
        assert updated_user.last_name == "Name"  # Unchanged
        
        # Verify in database
        user.refresh_from_db()
        assert user.first_name == "New"
        assert user.email == "new@example.com"
    
    def test_delete_removes_user(self):
        """Test that delete removes a user."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        user_id = user.id
        repo = DjangoUserRepository()
        
        # Act
        repo.delete(user_id)
        
        # Assert
        assert not User.objects.filter(id=user_id).exists()
    
    def test_exists_returns_true_when_user_exists(self):
        """Test that exists returns True when user exists."""
        # Arrange
        User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        repo = DjangoUserRepository()
        
        # Act
        result = repo.exists(username="testuser")
        
        # Assert
        assert result is True
    
    def test_exists_returns_false_when_user_does_not_exist(self):
        """Test that exists returns False when user doesn't exist."""
        # Arrange
        repo = DjangoUserRepository()
        
        # Act
        result = repo.exists(username="nonexistent")
        
        # Assert
        assert result is False
    
    def test_get_active_users_returns_only_active_users(self):
        """Test that get_active_users returns only active users."""
        # Arrange
        User.objects.create(username="active1", email="a1@example.com", is_active=True, first_name="A", last_name="User")
        User.objects.create(username="active2", email="a2@example.com", is_active=True, first_name="B", last_name="User")
        User.objects.create(username="inactive", email="i@example.com", is_active=False, first_name="C", last_name="User")
        
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_active_users()
        
        # Assert
        assert result.count() == 2
        assert all(user.is_active for user in result)
    
    def test_get_user_groups_returns_user_groups(self):
        """Test that get_user_groups returns the correct groups."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        group1 = Group.objects.create(name="Group1")
        group2 = Group.objects.create(name="Group2")
        user.groups.add(group1, group2)
        
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_user_groups(user.id)
        
        # Assert
        assert result.count() == 2
        group_names = [g.name for g in result]
        assert "Group1" in group_names
        assert "Group2" in group_names
    
    def test_get_user_permissions_returns_permissions_from_groups(self):
        """Test that get_user_permissions returns permissions from user's groups."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Create a group with permissions
        group = Group.objects.create(name="TestGroup")
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.create(
            codename="test_permission",
            name="Can test",
            content_type=content_type
        )
        group.permissions.add(permission)
        user.groups.add(group)
        
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_user_permissions(user.id)
        
        # Assert
        assert result.count() >= 1
        permission_codenames = [p.codename for p in result]
        assert "test_permission" in permission_codenames
    
    def test_add_user_to_groups_adds_user_to_groups(self):
        """Test that add_user_to_groups correctly adds user to groups."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        group1 = Group.objects.create(name="Group1")
        group2 = Group.objects.create(name="Group2")
        
        repo = DjangoUserRepository()
        
        # Act
        repo.add_user_to_groups(user.id, ["Group1", "Group2"])
        
        # Assert
        user_groups = user.groups.all()
        assert user_groups.count() == 2
        group_names = [g.name for g in user_groups]
        assert "Group1" in group_names
        assert "Group2" in group_names
    
    def test_remove_user_from_groups_removes_user_from_groups(self):
        """Test that remove_user_from_groups correctly removes user from groups."""
        # Arrange
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        group1 = Group.objects.create(name="Group1")
        group2 = Group.objects.create(name="Group2")
        user.groups.add(group1, group2)
        
        repo = DjangoUserRepository()
        
        # Act
        repo.remove_user_from_groups(user.id, ["Group1"])
        
        # Assert
        user_groups = user.groups.all()
        assert user_groups.count() == 1
        assert user_groups.first().name == "Group2"
    
    def test_get_users_in_group_returns_correct_users(self):
        """Test that get_users_in_group returns users in the specified group."""
        # Arrange
        group = Group.objects.create(name="TestGroup")
        
        user1 = User.objects.create(username="user1", email="u1@example.com", is_active=True, first_name="A", last_name="User")
        user2 = User.objects.create(username="user2", email="u2@example.com", is_active=True, first_name="B", last_name="User")
        user3 = User.objects.create(username="user3", email="u3@example.com", is_active=True, first_name="C", last_name="User")
        
        user1.groups.add(group)
        user2.groups.add(group)
        # user3 not in group
        
        repo = DjangoUserRepository()
        
        # Act
        result = repo.get_users_in_group("TestGroup")
        
        # Assert
        assert result.count() == 2
        usernames = [u.username for u in result]
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" not in usernames
