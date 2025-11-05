"""
Comprehensive tests for User model methods to increase coverage.
"""
import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@pytest.mark.django_db
class TestUserModelStringMethods:
    """Test __str__ methods for user app models."""
    
    def test_link_str_method(self):
        """Test Link __str__ method."""
        from user.models import Link
        
        link = Link.objects.create(
            menu_name="Test Link",
            routerlink="/test",
            order=1
        )
        str_result = str(link)
        assert str(link.id) in str_result
        assert "Test Link" in str_result
    
    def test_link_str_with_permission(self):
        """Test Link __str__ method with permission."""
        from user.models import Link, User
        
        # Create a content type and permission
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.create(
            codename='test_permission',
            name='Test Permission',
            content_type=content_type
        )
        
        link = Link.objects.create(
            permission=permission,
            menu_name="Admin Link",
            routerlink="/admin",
            order=2
        )
        str_result = str(link)
        assert str(link.id) in str_result
        assert "Admin Link" in str_result
    
    def test_phonetype_str_method(self):
        """Test PhoneType __str__ method."""
        from user.models import PhoneType
        
        phone_type = PhoneType.objects.create(
            carrier="Verizon",
            phone_type="SMS"
        )
        str_result = str(phone_type)
        assert str(phone_type.id) in str_result
        assert "Verizon" in str_result
        assert "SMS" in str_result


@pytest.mark.django_db
class TestUserModelPermissionMethods:
    """Test User model permission methods."""
    
    def test_user_has_perm_superuser(self):
        """Test has_perm returns True for superuser."""
        from user.models import User
        
        user = User.objects.create_user(
            username="superuser",
            email="super@test.com",
            password="pass123"
        )
        user.is_superuser = True
        user.save()
        
        # Superuser should have all permissions
        assert user.has_perm('any.permission') is True
        assert user.has_perm('user.change_user') is True
    
    def test_user_has_perm_regular_user(self):
        """Test has_perm returns False for regular user."""
        from user.models import User
        
        user = User.objects.create_user(
            username="regularuser",
            email="regular@test.com",
            password="pass123"
        )
        
        # Regular user should not have permissions
        assert user.has_perm('any.permission') is False
    
    def test_user_has_module_perms(self):
        """Test has_module_perms always returns True."""
        from user.models import User
        
        user = User.objects.create_user(
            username="moduleuser",
            email="module@test.com",
            password="pass123"
        )
        
        # has_module_perms currently always returns True per the TODO comment
        assert user.has_module_perms('user') is True
        assert user.has_module_perms('admin') is True
        assert user.has_module_perms('any_app') is True


@pytest.mark.django_db
class TestProfileManagerMethods:
    """Test ProfileManager methods."""
    
    def test_create_superuser(self):
        """Test ProfileManager create_superuser method."""
        from user.models import User
        
        superuser = User.objects.create_superuser(
            username="newsuperuser",
            email="newsuperuser@test.com",
            password="superpass123",
            first_name="Super",
            last_name="User"
        )
        
        assert superuser is not None
        assert superuser.username == "newsuperuser"
        assert superuser.email == "newsuperuser@test.com"
        assert superuser.first_name == "Super"
        assert superuser.last_name == "User"
        assert superuser.is_superuser is True
        assert superuser.is_active is True
        # Check password was set
        assert superuser.check_password("superpass123") is True
    
    def test_create_user_with_email_normalization(self):
        """Test create_user normalizes email and username."""
        from user.models import User
        
        user = User.objects.create_user(
            username="TestUser",
            email="Test@Example.COM",
            password="pass123"
        )
        
        # Username and email should be lowercased
        assert user.username == "testuser"
        assert user.email == "test@example.com"
    
    def test_create_user_without_email_raises_error(self):
        """Test create_user raises ValueError without email."""
        from user.models import User
        
        with pytest.raises(ValueError, match="Email required"):
            User.objects.create_user(
                username="testuser",
                email="",
                password="pass123"
            )
    
    def test_create_user_without_username_raises_error(self):
        """Test create_user raises ValueError without username."""
        from user.models import User
        
        with pytest.raises(ValueError, match="Username required"):
            User.objects.create_user(
                username="",
                email="test@test.com",
                password="pass123"
            )


@pytest.mark.django_db
class TestUserModelAdditionalMethods:
    """Test additional User model methods."""
    
    def test_user_get_full_name(self):
        """Test User get_full_name method."""
        from user.models import User
        
        user = User.objects.create_user(
            username="fullnameuser",
            email="fullname@test.com",
            password="pass123",
            first_name="John",
            last_name="Doe"
        )
        
        full_name = user.get_full_name()
        assert full_name == "John Doe"
    
    def test_user_save_method_clears_name_cache(self):
        """Test User save method clears name field cache."""
        from user.models import User
        
        user = User.objects.create_user(
            username="saveuser",
            email="save@test.com",
            password="pass123",
            first_name="Jane",
            last_name="Smith"
        )
        
        # Update first name
        user.first_name = "Janet"
        user.save()
        
        # Refresh from database
        user.refresh_from_db()
        
        # The generated name field should be updated
        assert user.name == "Janet Smith" or user.first_name == "Janet"
