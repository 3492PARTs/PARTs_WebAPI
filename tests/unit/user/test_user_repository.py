"""
Unit tests for UserRepository.

These tests validate the repository layer's data access operations.
"""
import pytest
from django.contrib.auth.models import Group
from user.models import User, PhoneType
from user.repositories.user_repository import UserRepository


@pytest.mark.django_db
class TestUserRepository:
    """Test UserRepository data access methods."""
    
    def test_get_by_id(self):
        """Test retrieving a user by ID."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        repo = UserRepository()
        result = repo.get_by_id(user.id)
        
        assert result == user
        assert result.username == "testuser"
    
    def test_get_by_username(self):
        """Test retrieving a user by username."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        repo = UserRepository()
        result = repo.get_by_username("testuser")
        
        assert result == user
    
    def test_get_by_email(self):
        """Test retrieving a user by email."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        repo = UserRepository()
        result = repo.get_by_email("test@example.com")
        
        assert result == user
    
    def test_get_by_email_not_found(self):
        """Test retrieving non-existent user by email returns None."""
        repo = UserRepository()
        result = repo.get_by_email("nonexistent@example.com")
        
        assert result is None
    
    def test_filter_users_all(self):
        """Test filtering users without criteria returns all users."""
        User.objects.create_user(username="user1", email="u1@example.com", password="pass")
        User.objects.create_user(username="user2", email="u2@example.com", password="pass")
        
        repo = UserRepository()
        result = repo.filter_users()
        
        assert result.count() >= 2
    
    def test_filter_users_active_only(self):
        """Test filtering for active users."""
        active_user = User.objects.create_user(
            username="active",
            email="active@example.com",
            password="pass"
        )
        active_user.is_active = True
        active_user.save()
        
        inactive_user = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="pass"
        )
        inactive_user.is_active = False
        inactive_user.save()
        
        repo = UserRepository()
        result = repo.filter_users(active=True)
        
        assert active_user in result
        assert inactive_user not in result
    
    def test_filter_users_exclude_admin(self):
        """Test filtering to exclude admin users."""
        admin_group = Group.objects.create(name="Admin")
        
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="pass"
        )
        admin_user.groups.add(admin_group)
        
        regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="pass"
        )
        
        repo = UserRepository()
        result = repo.filter_users(exclude_admin=True)
        
        assert regular_user in result
        assert admin_user not in result
    
    def test_update_user(self):
        """Test updating user fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass",
            first_name="Old"
        )
        
        repo = UserRepository()
        updated = repo.update_user(user, first_name="New", last_name="Name")
        
        assert updated.first_name == "New"
        assert updated.last_name == "Name"
        
        # Verify it's persisted
        refreshed = User.objects.get(id=user.id)
        assert refreshed.first_name == "New"
    
    def test_create_user(self):
        """Test creating a new user."""
        repo = UserRepository()
        user = repo.create_user(
            username="newuser",
            email="new@example.com",
            password="password123",
            first_name="New",
            last_name="User"
        )
        
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.first_name == "New"
        assert user.check_password("password123")
    
    def test_get_user_groups(self):
        """Test retrieving user's groups."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass"
        )
        group1 = Group.objects.create(name="Group1")
        group2 = Group.objects.create(name="Group2")
        user.groups.add(group1, group2)
        
        repo = UserRepository()
        groups = repo.get_user_groups(user)
        
        assert groups.count() == 2
        assert group1 in groups
        assert group2 in groups
    
    def test_add_user_to_group(self):
        """Test adding a user to a group."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass"
        )
        group = Group.objects.create(name="TestGroup")
        
        repo = UserRepository()
        repo.add_user_to_group(user, group)
        
        assert group in user.groups.all()
    
    def test_remove_user_from_group(self):
        """Test removing a user from a group."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass"
        )
        group = Group.objects.create(name="TestGroup")
        user.groups.add(group)
        
        repo = UserRepository()
        repo.remove_user_from_group(user, group)
        
        assert group not in user.groups.all()
    
    def test_get_phone_types(self):
        """Test retrieving all phone types."""
        PhoneType.objects.create(carrier="Verizon", phone_type="SMS")
        PhoneType.objects.create(carrier="AT&T", phone_type="SMS")
        
        repo = UserRepository()
        phone_types = repo.get_phone_types()
        
        assert phone_types.count() >= 2
    
    def test_phone_type_has_users(self):
        """Test checking if phone type has associated users."""
        phone_type = PhoneType.objects.create(carrier="Verizon", phone_type="SMS")
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass"
        )
        user.phone_type = phone_type
        user.save()
        
        repo = UserRepository()
        result = repo.phone_type_has_users(phone_type)
        
        assert result is True
    
    def test_get_users_in_group(self):
        """Test getting users in a specific group."""
        group = Group.objects.create(name="TestGroup")
        
        user1 = User.objects.create_user(
            username="user1",
            email="u1@example.com",
            password="pass"
        )
        user1.is_active = True
        user1.groups.add(group)
        user1.save()
        
        user2 = User.objects.create_user(
            username="user2",
            email="u2@example.com",
            password="pass"
        )
        user2.is_active = False
        user2.groups.add(group)
        user2.save()
        
        repo = UserRepository()
        
        # Test active only
        active_users = repo.get_users_in_group("TestGroup", active_only=True)
        assert user1 in active_users
        assert user2 not in active_users
        
        # Test all users
        all_users = repo.get_users_in_group("TestGroup", active_only=False)
        assert user1 in all_users
        assert user2 in all_users
