"""
Unit tests for PermissionRepository.

These tests validate the repository layer's permission data access operations.
"""
import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from user.models import User, Link
from user.repositories.permission_repository import PermissionRepository


@pytest.mark.django_db
class TestPermissionRepository:
    """Test PermissionRepository data access methods."""
    
    def test_get_user_permissions(self):
        """Test retrieving all permissions for a user."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="pass"
        )
        
        # Create permissions and group
        perm1 = Permission.objects.create(
            name="Test Permission 1",
            codename="test_perm1",
            content_type_id=-1
        )
        perm2 = Permission.objects.create(
            name="Test Permission 2",
            codename="test_perm2",
            content_type_id=-1
        )
        
        group = Group.objects.create(name="TestGroup")
        group.permissions.add(perm1, perm2)
        user.groups.add(group)
        
        repo = PermissionRepository()
        permissions = repo.get_user_permissions(user)
        
        assert permissions.count() == 2
        assert perm1 in permissions
        assert perm2 in permissions
    
    def test_get_all_groups(self):
        """Test retrieving all groups."""
        Group.objects.create(name="Group1")
        Group.objects.create(name="Group2")
        
        repo = PermissionRepository()
        groups = repo.get_all_groups()
        
        assert groups.count() >= 2
    
    def test_get_group_by_id(self):
        """Test retrieving a group by ID."""
        group = Group.objects.create(name="TestGroup")
        
        repo = PermissionRepository()
        result = repo.get_group_by_id(group.id)
        
        assert result == group
    
    def test_get_group_by_name(self):
        """Test retrieving a group by name."""
        group = Group.objects.create(name="TestGroup")
        
        repo = PermissionRepository()
        result = repo.get_group_by_name("TestGroup")
        
        assert result == group
    
    def test_create_group(self):
        """Test creating a new group."""
        repo = PermissionRepository()
        group = repo.create_group("NewGroup")
        
        assert group.name == "NewGroup"
        assert Group.objects.filter(name="NewGroup").exists()
    
    def test_update_group(self):
        """Test updating a group's name."""
        group = Group.objects.create(name="OldName")
        
        repo = PermissionRepository()
        updated = repo.update_group(group, "NewName")
        
        assert updated.name == "NewName"
        assert Group.objects.filter(name="NewName").exists()
    
    def test_delete_group(self):
        """Test deleting a group."""
        group = Group.objects.create(name="TestGroup")
        group_id = group.id
        
        repo = PermissionRepository()
        repo.delete_group(group)
        
        assert not Group.objects.filter(id=group_id).exists()
    
    def test_add_permission_to_group(self):
        """Test adding a permission to a group."""
        group = Group.objects.create(name="TestGroup")
        permission = Permission.objects.create(
            name="Test Permission",
            codename="test_perm",
            content_type_id=-1
        )
        
        repo = PermissionRepository()
        repo.add_permission_to_group(group, permission)
        
        assert permission in group.permissions.all()
    
    def test_remove_permission_from_group(self):
        """Test removing a permission from a group."""
        group = Group.objects.create(name="TestGroup")
        permission = Permission.objects.create(
            name="Test Permission",
            codename="test_perm",
            content_type_id=-1
        )
        group.permissions.add(permission)
        
        repo = PermissionRepository()
        repo.remove_permission_from_group(group, permission)
        
        assert permission not in group.permissions.all()
    
    def test_get_group_permissions(self):
        """Test retrieving all permissions for a group."""
        group = Group.objects.create(name="TestGroup")
        perm1 = Permission.objects.create(
            name="Perm1",
            codename="perm1",
            content_type_id=-1
        )
        perm2 = Permission.objects.create(
            name="Perm2",
            codename="perm2",
            content_type_id=-1
        )
        group.permissions.add(perm1, perm2)
        
        repo = PermissionRepository()
        permissions = repo.get_group_permissions(group)
        
        assert permissions.count() == 2
        assert perm1 in permissions
        assert perm2 in permissions
    
    def test_get_custom_permissions(self):
        """Test retrieving custom permissions."""
        Permission.objects.create(
            name="Custom Perm",
            codename="custom",
            content_type_id=-1
        )
        
        repo = PermissionRepository()
        permissions = repo.get_custom_permissions()
        
        assert permissions.filter(codename="custom").exists()
    
    def test_get_permission_by_id(self):
        """Test retrieving a permission by ID."""
        perm = Permission.objects.create(
            name="Test",
            codename="test",
            content_type_id=-1
        )
        
        repo = PermissionRepository()
        result = repo.get_permission_by_id(perm.id)
        
        assert result == perm
    
    def test_get_permission_by_codename(self):
        """Test retrieving a permission by codename."""
        perm = Permission.objects.create(
            name="Test",
            codename="test_code",
            content_type_id=-1
        )
        
        repo = PermissionRepository()
        result = repo.get_permission_by_codename("test_code")
        
        assert result == perm
    
    def test_create_permission(self):
        """Test creating a new permission."""
        repo = PermissionRepository()
        perm = repo.create_permission("Test Permission", "test_perm")
        
        assert perm.name == "Test Permission"
        assert perm.codename == "test_perm"
        assert perm.content_type_id == -1
    
    def test_update_permission(self):
        """Test updating a permission."""
        perm = Permission.objects.create(
            name="Old",
            codename="old",
            content_type_id=-1
        )
        
        repo = PermissionRepository()
        updated = repo.update_permission(perm, "New", "new")
        
        assert updated.name == "New"
        assert updated.codename == "new"
    
    def test_delete_permission(self):
        """Test deleting a permission."""
        perm = Permission.objects.create(
            name="Test",
            codename="test",
            content_type_id=-1
        )
        perm_id = perm.id
        
        repo = PermissionRepository()
        repo.delete_permission(perm)
        
        assert not Permission.objects.filter(id=perm_id).exists()
    
    def test_get_all_links(self):
        """Test retrieving all navigation links."""
        Link.objects.create(menu_name="Link1", routerlink="/link1", order=1)
        Link.objects.create(menu_name="Link2", routerlink="/link2", order=2)
        
        repo = PermissionRepository()
        links = repo.get_all_links()
        
        assert links.count() >= 2
    
    def test_get_accessible_links(self):
        """Test retrieving accessible links based on permissions."""
        perm = Permission.objects.create(
            name="Test",
            codename="test",
            content_type_id=-1
        )
        
        link1 = Link.objects.create(
            menu_name="Protected",
            routerlink="/protected",
            order=1,
            permission=perm
        )
        link2 = Link.objects.create(
            menu_name="Public",
            routerlink="/public",
            order=2,
            permission=None
        )
        
        repo = PermissionRepository()
        links = repo.get_accessible_links([perm])
        
        assert link1 in links
        assert link2 in links
    
    def test_create_link(self):
        """Test creating a new link."""
        perm = Permission.objects.create(
            name="Test",
            codename="test",
            content_type_id=-1
        )
        
        repo = PermissionRepository()
        link = repo.create_link(
            menu_name="Test Link",
            routerlink="/test",
            order=1,
            permission_id=perm.id
        )
        
        assert link.menu_name == "Test Link"
        assert link.routerlink == "/test"
        assert link.permission == perm
    
    def test_update_link(self):
        """Test updating a link."""
        link = Link.objects.create(
            menu_name="Old",
            routerlink="/old",
            order=1
        )
        
        repo = PermissionRepository()
        updated = repo.update_link(link, menu_name="New", routerlink="/new")
        
        assert updated.menu_name == "New"
        assert updated.routerlink == "/new"
    
    def test_delete_link(self):
        """Test deleting a link."""
        link = Link.objects.create(
            menu_name="Test",
            routerlink="/test",
            order=1
        )
        link_id = link.id
        
        repo = PermissionRepository()
        repo.delete_link(link)
        
        assert not Link.objects.filter(id=link_id).exists()
