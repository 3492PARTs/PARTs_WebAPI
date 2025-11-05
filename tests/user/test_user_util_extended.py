"""
Extended comprehensive tests for user/util.py functions.
Focuses on increasing coverage from 33% to higher levels.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


@pytest.mark.django_db
class TestSaveUser:
    """Tests for save_user function."""

    def test_save_user_basic_update(self, test_user):
        """Test basic user profile update."""
        from user.util import save_user
        
        data = {
            'username': test_user.username,
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'discord_user_id': 'discord123',
            'phone': '1234567890',
            'phone_type_id': None,
            'is_active': True
        }
        
        result = save_user(data)
        
        assert result.first_name == 'Updated'
        assert result.last_name == 'Name'
        assert result.email == 'updated@example.com'
        assert result.discord_user_id == 'discord123'
        assert result.phone == '1234567890'
        assert result.is_active is True

    def test_save_user_with_groups(self, test_user):
        """Test user update with group assignments."""
        from user.util import save_user
        
        # Create test groups
        group1 = Group.objects.create(name='TestGroup1')
        group2 = Group.objects.create(name='TestGroup2')
        
        data = {
            'username': test_user.username,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'discord_user_id': '',
            'phone': '',
            'is_active': True,
            'groups': [
                {'name': 'TestGroup1'},
                {'name': 'TestGroup2'}
            ]
        }
        
        result = save_user(data)
        
        user_groups = list(result.groups.values_list('name', flat=True))
        assert 'TestGroup1' in user_groups
        assert 'TestGroup2' in user_groups

    def test_save_user_remove_groups(self, test_user):
        """Test removing user from groups."""
        from user.util import save_user
        
        # Create groups and add user to them
        group1 = Group.objects.create(name='RemoveGroup1')
        group2 = Group.objects.create(name='RemoveGroup2')
        test_user.groups.add(group1, group2)
        
        # Update user with only one group
        data = {
            'username': test_user.username,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'discord_user_id': '',
            'phone': '',
            'is_active': True,
            'groups': [
                {'name': 'RemoveGroup1'}
            ]
        }
        
        result = save_user(data)
        
        user_groups = list(result.groups.values_list('name', flat=True))
        assert 'RemoveGroup1' in user_groups
        assert 'RemoveGroup2' not in user_groups

    def test_save_user_email_lowercase(self, test_user):
        """Test that email is converted to lowercase."""
        from user.util import save_user
        
        data = {
            'username': test_user.username,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'UPPERCASE@EXAMPLE.COM',
            'discord_user_id': '',
            'phone': '',
            'is_active': True
        }
        
        result = save_user(data)
        
        assert result.email == 'uppercase@example.com'


@pytest.mark.django_db
class TestGetUsersInGroup:
    """Tests for get_users_in_group function."""

    def test_get_users_in_group(self, test_user):
        """Test retrieving users in a specific group."""
        from user.util import get_users_in_group
        
        # Create a group and add user
        group = Group.objects.create(name='TestGroupFilter')
        test_user.groups.add(group)
        test_user.is_active = True
        test_user.save()
        
        users = get_users_in_group('TestGroupFilter')
        
        assert test_user in users

    def test_get_users_in_group_empty(self):
        """Test retrieving users from empty group."""
        from user.util import get_users_in_group
        
        Group.objects.create(name='EmptyGroup')
        
        users = get_users_in_group('EmptyGroup')
        
        assert len(users) == 0


@pytest.mark.django_db
class TestGetUsersWithPermission:
    """Tests for get_users_with_permission function."""

    def test_get_users_with_permission(self, test_user):
        """Test retrieving users with a specific permission."""
        from user.util import get_users_with_permission
        
        # Create permission and group
        content_type = ContentType.objects.get_for_model(Permission)
        permission = Permission.objects.create(
            codename='test_permission',
            name='Test Permission',
            content_type=content_type
        )
        group = Group.objects.create(name='PermissionGroup')
        group.permissions.add(permission)
        
        # Add user to group
        test_user.groups.add(group)
        test_user.is_active = True
        test_user.save()
        
        users = get_users_with_permission('test_permission')
        
        assert test_user in users

    def test_get_users_with_permission_multiple_groups(self, test_user):
        """Test users with permission through multiple groups."""
        from user.util import get_users_with_permission
        from user.models import User
        
        # Create permission and multiple groups with same permission
        content_type = ContentType.objects.get_for_model(Permission)
        permission = Permission.objects.create(
            codename='shared_permission',
            name='Shared Permission',
            content_type=content_type
        )
        group1 = Group.objects.create(name='PermGroup1')
        group2 = Group.objects.create(name='PermGroup2')
        group1.permissions.add(permission)
        group2.permissions.add(permission)
        
        # Add user to both groups
        test_user.groups.add(group1, group2)
        test_user.is_active = True
        test_user.save()
        
        users = get_users_with_permission('shared_permission')
        
        # Should return user only once (distinct)
        assert test_user in users
        assert users.filter(id=test_user.id).count() == 1


@pytest.mark.django_db
class TestSaveGroup:
    """Tests for save_group function."""

    def test_save_group_create_new(self):
        """Test creating a new group."""
        from user.util import save_group
        
        data = {
            'name': 'NewGroup',
            'permissions': []
        }
        
        save_group(data)
        
        assert Group.objects.filter(name='NewGroup').exists()

    def test_save_group_update_existing(self):
        """Test updating an existing group."""
        from user.util import save_group
        
        group = Group.objects.create(name='OldName')
        
        data = {
            'id': group.id,
            'name': 'UpdatedName',
            'permissions': []
        }
        
        save_group(data)
        
        group.refresh_from_db()
        assert group.name == 'UpdatedName'

    def test_save_group_with_permissions(self):
        """Test saving group with permissions."""
        from user.util import save_group
        
        content_type = ContentType.objects.get_for_model(Permission)
        perm1 = Permission.objects.create(
            codename='perm1',
            name='Permission 1',
            content_type=content_type
        )
        perm2 = Permission.objects.create(
            codename='perm2',
            name='Permission 2',
            content_type=content_type
        )
        
        data = {
            'name': 'GroupWithPerms',
            'permissions': [
                {'id': perm1.id},
                {'id': perm2.id}
            ]
        }
        
        save_group(data)
        
        group = Group.objects.get(name='GroupWithPerms')
        assert perm1 in group.permissions.all()
        assert perm2 in group.permissions.all()

    def test_save_group_remove_permissions(self):
        """Test removing permissions from a group."""
        from user.util import save_group
        
        content_type = ContentType.objects.get_for_model(Permission)
        perm1 = Permission.objects.create(
            codename='remove_perm1',
            name='Remove Permission 1',
            content_type=content_type
        )
        perm2 = Permission.objects.create(
            codename='remove_perm2',
            name='Remove Permission 2',
            content_type=content_type
        )
        
        group = Group.objects.create(name='GroupRemovePerms')
        group.permissions.add(perm1, perm2)
        
        # Update group to only have perm1
        data = {
            'id': group.id,
            'name': 'GroupRemovePerms',
            'permissions': [
                {'id': perm1.id}
            ]
        }
        
        save_group(data)
        
        group.refresh_from_db()
        assert perm1 in group.permissions.all()
        assert perm2 not in group.permissions.all()


@pytest.mark.django_db
class TestDeleteGroup:
    """Tests for delete_group function."""

    def test_delete_group_basic(self):
        """Test deleting a basic group."""
        from user.util import delete_group
        
        group = Group.objects.create(name='DeleteMe')
        group_id = group.id
        
        delete_group(group_id)
        
        assert not Group.objects.filter(id=group_id).exists()

    def test_delete_group_with_scout_auth(self):
        """Test deleting group with associated ScoutAuthGroup."""
        from user.util import delete_group
        from scouting.models import ScoutAuthGroup
        
        group = Group.objects.create(name='ScoutGroup')
        
        # Create ScoutAuthGroup
        ScoutAuthGroup.objects.create(group=group)
        
        group_id = group.id
        delete_group(group_id)
        
        # Both should be deleted
        assert not Group.objects.filter(id=group_id).exists()
        assert not ScoutAuthGroup.objects.filter(group_id=group_id).exists()


@pytest.mark.django_db
class TestSavePermission:
    """Tests for save_permission function."""

    def test_save_permission_create_new(self):
        """Test creating a new permission."""
        from user.util import save_permission
        
        # Create a valid content type with id=-1 for testing
        from django.contrib.contenttypes.models import ContentType
        ContentType.objects.get_or_create(
            id=-1,
            defaults={'app_label': 'custom', 'model': 'custom'}
        )
        
        data = {
            'name': 'New Permission',
            'codename': 'new_permission'
        }
        
        save_permission(data)
        
        perm = Permission.objects.get(codename='new_permission')
        assert perm.name == 'New Permission'
        assert perm.content_type_id == -1

    def test_save_permission_update_existing(self):
        """Test updating an existing permission."""
        from user.util import save_permission
        from django.contrib.contenttypes.models import ContentType
        
        # Create a valid content type with id=-1 for testing
        ContentType.objects.get_or_create(
            id=-1,
            defaults={'app_label': 'custom', 'model': 'custom'}
        )
        
        content_type = ContentType.objects.get_for_model(Permission)
        perm = Permission.objects.create(
            codename='old_code',
            name='Old Name',
            content_type=content_type
        )
        
        data = {
            'id': perm.id,
            'name': 'Updated Name',
            'codename': 'updated_code'
        }
        
        save_permission(data)
        
        perm.refresh_from_db()
        assert perm.name == 'Updated Name'
        assert perm.codename == 'updated_code'


@pytest.mark.django_db
class TestDeletePermission:
    """Tests for delete_permission function."""

    def test_delete_permission(self):
        """Test deleting a permission."""
        from user.util import delete_permission
        
        content_type = ContentType.objects.get_for_model(Permission)
        perm = Permission.objects.create(
            codename='delete_me',
            name='Delete Me',
            content_type=content_type
        )
        perm_id = perm.id
        
        delete_permission(perm_id)
        
        assert not Permission.objects.filter(id=perm_id).exists()


@pytest.mark.django_db
class TestDeletePhoneType:
    """Tests for delete_phone_type function."""

    def test_delete_phone_type_success(self):
        """Test successful phone type deletion."""
        from user.util import delete_phone_type
        from user.models import PhoneType
        
        phone_type = PhoneType.objects.create(
            carrier='TestCarrier',
            phone_type='SMS'
        )
        phone_type_id = phone_type.id
        
        delete_phone_type(phone_type_id)
        
        assert not PhoneType.objects.filter(id=phone_type_id).exists()

    def test_delete_phone_type_with_users_raises_error(self, test_user):
        """Test that deleting phone type with users raises error."""
        from user.util import delete_phone_type
        from user.models import PhoneType
        
        phone_type = PhoneType.objects.create(
            carrier='InUseCarrier',
            phone_type='SMS'
        )
        
        # Assign phone type to user
        test_user.phone_type = phone_type
        test_user.save()
        
        with pytest.raises(ValueError, match="Can't delete, there are users tied to this phone type."):
            delete_phone_type(phone_type.id)


@pytest.mark.django_db
class TestRunSecurityAudit:
    """Tests for run_security_audit function."""

    def test_run_security_audit_returns_users_with_groups(self, test_user):
        """Test that security audit returns only active users with groups."""
        from user.util import run_security_audit
        from user.models import User
        
        # Create users - one with groups, one without
        group = Group.objects.create(name='AuditGroup')
        
        test_user.is_active = True
        test_user.groups.add(group)
        test_user.save()
        
        user_no_groups = User.objects.create_user(
            username='nogroups',
            email='nogroups@example.com',
            password='password',
            first_name='No',
            last_name='Groups'
        )
        user_no_groups.is_active = True
        user_no_groups.save()
        
        result = run_security_audit()
        
        assert test_user in result
        assert user_no_groups not in result

    def test_run_security_audit_empty(self):
        """Test security audit with no users having groups."""
        from user.util import run_security_audit
        
        result = run_security_audit()
        
        # Should return empty list or only users that have groups
        assert isinstance(result, list)


@pytest.mark.django_db
class TestSaveLink:
    """Tests for save_link function."""

    def test_save_link_create_new(self):
        """Test creating a new link."""
        from user.util import save_link
        from user.models import Link
        
        data = {
            'menu_name': 'Home',
            'routerlink': '/home',
            'order': 1,
            'permission': None
        }
        
        save_link(data)
        
        link = Link.objects.get(menu_name='Home')
        assert link.routerlink == '/home'
        assert link.order == 1
        assert link.permission_id is None

    def test_save_link_update_existing(self):
        """Test updating an existing link."""
        from user.util import save_link
        from user.models import Link
        
        link = Link.objects.create(
            menu_name='Old Name',
            routerlink='/old',
            order=1
        )
        
        data = {
            'id': link.id,
            'menu_name': 'Updated Name',
            'routerlink': '/updated',
            'order': 2,
            'permission': None
        }
        
        save_link(data)
        
        link.refresh_from_db()
        assert link.menu_name == 'Updated Name'
        assert link.routerlink == '/updated'
        assert link.order == 2

    def test_save_link_with_permission(self):
        """Test saving link with permission."""
        from user.util import save_link
        from user.models import Link
        
        content_type = ContentType.objects.get_for_model(Permission)
        permission = Permission.objects.create(
            codename='link_perm',
            name='Link Permission',
            content_type=content_type
        )
        
        data = {
            'menu_name': 'Admin Link',
            'routerlink': '/admin',
            'order': 1,
            'permission': {'id': permission.id}
        }
        
        save_link(data)
        
        link = Link.objects.get(menu_name='Admin Link')
        assert link.permission_id == permission.id


@pytest.mark.django_db
class TestDeleteLink:
    """Tests for delete_link function."""

    def test_delete_link(self):
        """Test deleting a link."""
        from user.util import delete_link
        from user.models import Link
        
        link = Link.objects.create(
            menu_name='Delete Me',
            routerlink='/delete',
            order=1
        )
        link_id = link.id
        
        delete_link(link_id)
        
        assert not Link.objects.filter(id=link_id).exists()


@pytest.mark.django_db
class TestGetPhoneTypes:
    """Tests for get_phone_types function."""

    def test_get_phone_types(self):
        """Test retrieving phone types."""
        from user.util import get_phone_types
        from user.models import PhoneType
        
        PhoneType.objects.create(carrier='Carrier1', phone_type='SMS')
        PhoneType.objects.create(carrier='Carrier2', phone_type='MMS')
        
        result = get_phone_types()
        
        assert result.count() == 2


@pytest.mark.django_db
class TestGetGroups:
    """Tests for get_groups function."""

    def test_get_groups(self):
        """Test retrieving all groups."""
        from user.util import get_groups
        
        Group.objects.create(name='Group1')
        Group.objects.create(name='Group2')
        
        result = get_groups()
        
        assert result.count() >= 2


@pytest.mark.django_db
class TestGetPermissions:
    """Tests for get_permissions function."""

    def test_get_permissions_filters_by_content_type(self):
        """Test that get_permissions filters by content_type_id=-1."""
        from user.util import get_permissions
        from django.contrib.contenttypes.models import ContentType
        
        # Create a valid content type with id=-1 for testing
        ContentType.objects.get_or_create(
            id=-1,
            defaults={'app_label': 'custom', 'model': 'custom'}
        )
        
        # Create permission with content_type_id=-1
        perm1 = Permission.objects.create(
            codename='custom_perm',
            name='Custom Permission',
            content_type_id=-1
        )
        
        # Create permission with different content_type
        content_type = ContentType.objects.get_for_model(Permission)
        perm2 = Permission.objects.create(
            codename='other_perm',
            name='Other Permission',
            content_type=content_type
        )
        
        result = get_permissions()
        
        assert perm1 in result
        assert perm2 not in result


@pytest.mark.django_db
class TestGetLinks:
    """Tests for get_links function."""

    def test_get_links(self):
        """Test retrieving all links ordered by order."""
        from user.util import get_links
        from user.models import Link
        
        Link.objects.create(menu_name='Link1', routerlink='/link1', order=2)
        Link.objects.create(menu_name='Link2', routerlink='/link2', order=1)
        
        result = get_links()
        
        assert result.count() == 2
        # Should be ordered by order field
        assert result.first().order == 1
