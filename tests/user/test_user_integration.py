"""
Complex integration tests for user authentication and permission workflows.

This test file validates:
- Multi-level permission hierarchy (Viewer/Editor/Admin)
- Access control with error handling
- Permission-based function execution
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.django_db
class TestComplexUserAuthWorkflows:
    """Complex integration tests for user authentication and permission workflows."""

    def test_multi_level_permission_hierarchy(self):
        """Test complex permission hierarchy with groups and individual permissions."""
        from general.security import has_access, get_user_permissions, get_user_groups
        from django.contrib.auth.models import Permission, Group
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Setup: Create content type and permissions
        content_type = ContentType.objects.get_for_model(User)
        
        perm_view = Permission.objects.create(
            codename='view_user_profile',
            name='Can view user profile',
            content_type=content_type
        )
        
        perm_edit = Permission.objects.create(
            codename='edit_user_profile',
            name='Can edit user profile',
            content_type=content_type
        )
        
        perm_admin = Permission.objects.create(
            codename='admin_users',
            name='Can administer users',
            content_type=content_type
        )
        
        # Create groups with different permission levels
        viewer_group = Group.objects.create(name='Viewers')
        viewer_group.permissions.add(perm_view)
        
        editor_group = Group.objects.create(name='Editors')
        editor_group.permissions.add(perm_view, perm_edit)
        
        admin_group = Group.objects.create(name='Admins')
        admin_group.permissions.add(perm_view, perm_edit, perm_admin)
        
        # Create users with different group memberships
        viewer = User.objects.create_user(
            username='viewer',
            email='viewer@test.com',
            password='pass'
        )
        viewer.groups.add(viewer_group)
        
        editor = User.objects.create_user(
            username='editor',
            email='editor@test.com',
            password='pass'
        )
        editor.groups.add(editor_group)
        
        admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass'
        )
        admin.groups.add(admin_group)
        
        # Test: Verify permission hierarchy
        # Viewer should only have view permission
        assert has_access(viewer.id, 'view_user_profile')
        assert not has_access(viewer.id, 'edit_user_profile')
        assert not has_access(viewer.id, 'admin_users')
        
        # Editor should have view and edit
        assert has_access(editor.id, 'view_user_profile')
        assert has_access(editor.id, 'edit_user_profile')
        assert not has_access(editor.id, 'admin_users')
        
        # Admin should have all permissions
        assert has_access(admin.id, 'view_user_profile')
        assert has_access(admin.id, 'edit_user_profile')
        assert has_access(admin.id, 'admin_users')
        
        # Test: Check multiple permissions at once
        # has_access with list returns True if user has AT LEAST ONE of the permissions
        assert has_access(admin.id, ['view_user_profile', 'edit_user_profile', 'admin_users'])
        # Editor has edit_user_profile, so should return True even without admin_users
        assert has_access(editor.id, ['view_user_profile', 'edit_user_profile', 'admin_users'])
        # Viewer doesn't have admin_users or edit, but has view, so returns True
        assert has_access(viewer.id, ['view_user_profile', 'admin_users'])
        # Test single permission checks work as expected
        assert has_access(viewer.id, 'view_user_profile')
        assert not has_access(viewer.id, 'admin_users')

    def test_access_response_with_complex_error_handling(self, default_user):
        """Test access_response with complex error scenarios and logging."""
        from general.security import access_response
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass'
        )
        
        # Test 1: Function succeeds with permission
        mock_function = Mock(return_value={'status': 'success'})
        with patch('general.security.has_access', return_value=True):
            result = access_response(
                'test_endpoint',
                user.id,
                'test_permission',
                'Access denied',
                mock_function
            )
            
            assert result == {'status': 'success'}
            mock_function.assert_called_once()
        
        # Test 2: Function fails without permission
        mock_function = Mock()
        with patch('general.security.has_access', return_value=False):
            result = access_response(
                'test_endpoint',
                user.id,
                'test_permission',
                'Access denied',
                mock_function
            )
            
            assert result.data['error'] is True
            assert 'do not have access' in result.data['retMessage']
            mock_function.assert_not_called()
        
        # Test 3: Function raises exception and creates error log
        mock_function = Mock(side_effect=ValueError("Test error"))
        with patch('general.security.has_access', return_value=True), \
             patch('general.security.ErrorLog') as MockErrorLog:
            
            mock_log = MagicMock()
            MockErrorLog.return_value = mock_log
            
            result = access_response(
                'test_endpoint',
                user.id,
                'test_permission',
                'Error occurred',
                mock_function
            )
            
            assert result.data['error'] is True
            MockErrorLog.assert_called()
            mock_log.save.assert_called()
