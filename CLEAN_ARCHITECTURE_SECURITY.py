"""
Clean architecture implementation for security and access control.

This module demonstrates how to handle authentication and authorization
using clean architecture principles.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


# ============================================================================
# Domain Layer: Security Interfaces
# ============================================================================

class IAuthenticationService(ABC):
    """
    Interface for authentication operations.
    
    Abstracts away Django's authentication system.
    """
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[int]:
        """
        Authenticate a user with credentials.
        
        Args:
            username: Username or email
            password: User password
            
        Returns:
            User ID if authenticated, None otherwise
        """
        pass
    
    @abstractmethod
    def generate_tokens(self, user_id: int) -> dict:
        """
        Generate JWT tokens for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dictionary with 'access' and 'refresh' tokens
        """
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh an access token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dictionary with new 'access' token
        """
        pass


class IAuthorizationService(ABC):
    """
    Interface for authorization operations.
    
    Handles permission checking independent of Django's permission system.
    """
    
    @abstractmethod
    def has_permission(self, user_id: int, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_id: The user ID
            permission: Permission codename
            
        Returns:
            True if user has permission, False otherwise
        """
        pass
    
    @abstractmethod
    def has_any_permission(self, user_id: int, permissions: List[str]) -> bool:
        """
        Check if user has at least one of the specified permissions.
        
        Args:
            user_id: The user ID
            permissions: List of permission codenames
            
        Returns:
            True if user has any permission, False otherwise
        """
        pass
    
    @abstractmethod
    def has_all_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """
        Check if user has all specified permissions.
        
        Args:
            user_id: The user ID
            permissions: List of permission codenames
            
        Returns:
            True if user has all permissions, False otherwise
        """
        pass
    
    @abstractmethod
    def is_in_group(self, user_id: int, group_name: str) -> bool:
        """
        Check if user belongs to a specific group.
        
        Args:
            user_id: The user ID
            group_name: Name of the group
            
        Returns:
            True if user is in group, False otherwise
        """
        pass


# ============================================================================
# DTOs for Security
# ============================================================================

@dataclass
class AuthenticationDTO:
    """DTO for authentication credentials."""
    username: str
    password: str


@dataclass
class TokensDTO:
    """DTO for JWT tokens."""
    access_token: str
    refresh_token: str


@dataclass
class AuthorizationCheckDTO:
    """DTO for authorization check result."""
    user_id: int
    has_access: bool
    reason: Optional[str] = None


# ============================================================================
# Use Cases for Authentication & Authorization
# ============================================================================

class AuthenticateUserUseCase:
    """
    Use case for authenticating a user.
    
    Handles the business logic for user login.
    """
    
    def __init__(
        self,
        auth_service: IAuthenticationService,
        user_repository: 'IUserRepository'
    ):
        self.auth_service = auth_service
        self.user_repository = user_repository
    
    def execute(self, dto: AuthenticationDTO) -> Optional[TokensDTO]:
        """
        Authenticate user and generate tokens.
        
        Args:
            dto: Authentication credentials
            
        Returns:
            TokensDTO if authenticated, None otherwise
        """
        # Authenticate
        user_id = self.auth_service.authenticate(dto.username, dto.password)
        if not user_id:
            return None
        
        # Check if user is active
        user = self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        # Generate tokens
        tokens = self.auth_service.generate_tokens(user_id)
        
        return TokensDTO(
            access_token=tokens['access'],
            refresh_token=tokens['refresh']
        )


class CheckUserAccessUseCase:
    """
    Use case for checking user access to resources.
    
    Encapsulates authorization logic.
    """
    
    def __init__(self, auth_service: IAuthorizationService):
        self.auth_service = auth_service
    
    def execute(
        self,
        user_id: int,
        required_permissions: List[str],
        require_all: bool = False
    ) -> AuthorizationCheckDTO:
        """
        Check if user has required permissions.
        
        Args:
            user_id: The user ID
            required_permissions: List of required permission codenames
            require_all: If True, user must have all permissions; if False, any permission
            
        Returns:
            AuthorizationCheckDTO with result
        """
        if not required_permissions:
            return AuthorizationCheckDTO(
                user_id=user_id,
                has_access=True,
                reason="No permissions required"
            )
        
        if require_all:
            has_access = self.auth_service.has_all_permissions(user_id, required_permissions)
            reason = None if has_access else f"User missing one or more required permissions: {', '.join(required_permissions)}"
        else:
            has_access = self.auth_service.has_any_permission(user_id, required_permissions)
            reason = None if has_access else f"User does not have any of: {', '.join(required_permissions)}"
        
        return AuthorizationCheckDTO(
            user_id=user_id,
            has_access=has_access,
            reason=reason
        )


# ============================================================================
# Infrastructure Layer: Django Implementation
# ============================================================================

from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from rest_framework_simplejwt.tokens import RefreshToken
from user.models import User


class DjangoAuthenticationService(IAuthenticationService):
    """
    Django implementation of authentication service.
    
    Wraps Django's authentication system.
    """
    
    def authenticate(self, username: str, password: str) -> Optional[int]:
        """Authenticate using Django's auth system."""
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            return user.id
        return None
    
    def generate_tokens(self, user_id: int) -> dict:
        """Generate JWT tokens using djangorestframework-simplejwt."""
        user = User.objects.get(id=user_id)
        refresh = RefreshToken.for_user(user)
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token."""
        refresh = RefreshToken(refresh_token)
        return {
            'access': str(refresh.access_token)
        }


class DjangoAuthorizationService(IAuthorizationService):
    """
    Django implementation of authorization service.
    
    Wraps Django's permission system.
    """
    
    def has_permission(self, user_id: int, permission: str) -> bool:
        """Check if user has a specific permission."""
        try:
            user = User.objects.get(id=user_id)
            return user.groups.filter(
                permissions__codename=permission
            ).exists()
        except User.DoesNotExist:
            return False
    
    def has_any_permission(self, user_id: int, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        try:
            user = User.objects.get(id=user_id)
            return user.groups.filter(
                permissions__codename__in=permissions
            ).exists()
        except User.DoesNotExist:
            return False
    
    def has_all_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """Check if user has all specified permissions."""
        for permission in permissions:
            if not self.has_permission(user_id, permission):
                return False
        return True
    
    def is_in_group(self, user_id: int, group_name: str) -> bool:
        """Check if user belongs to a group."""
        try:
            user = User.objects.get(id=user_id)
            return user.groups.filter(name=group_name).exists()
        except User.DoesNotExist:
            return False


# ============================================================================
# Presentation Layer: Views with Authorization
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.di_container import resolve
from general.security import ret_message


class SecureView(APIView):
    """
    Base class for views that require authentication and authorization.
    
    Provides common authorization checking functionality.
    """
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    # Override these in subclasses
    required_permissions: List[str] = []
    require_all_permissions: bool = False
    
    def check_access(self, request) -> tuple[bool, Optional[str]]:
        """
        Check if user has required permissions.
        
        Args:
            request: The HTTP request
            
        Returns:
            Tuple of (has_access, error_message)
        """
        if not self.required_permissions:
            return True, None
        
        # Resolve authorization service
        auth_service = resolve(IAuthorizationService)
        
        # Execute authorization use case
        use_case = CheckUserAccessUseCase(auth_service)
        result = use_case.execute(
            request.user.id,
            self.required_permissions,
            self.require_all_permissions
        )
        
        return result.has_access, result.reason
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to check authorization before handling request.
        """
        has_access, error_message = self.check_access(request)
        
        if not has_access:
            return ret_message(
                error_message or "You do not have access to this resource.",
                True,
                self.get_endpoint(),
                request.user.id,
            )
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_endpoint(self) -> str:
        """Get endpoint path for logging. Override in subclasses."""
        return getattr(self, 'endpoint', 'unknown/')


# Example usage:
class AdminOnlyView(SecureView):
    """
    Example view that requires admin permission.
    """
    
    endpoint = "admin-only/"
    required_permissions = ["admin"]
    
    def get(self, request):
        return Response({"message": "Admin access granted"})


class MultiPermissionView(SecureView):
    """
    Example view that requires any of multiple permissions.
    """
    
    endpoint = "multi-permission/"
    required_permissions = ["admin", "scoutadmin", "user_view"]
    require_all_permissions = False  # User needs ANY of these
    
    def get(self, request):
        return Response({"message": "Access granted"})


class StrictPermissionView(SecureView):
    """
    Example view that requires all specified permissions.
    """
    
    endpoint = "strict-permission/"
    required_permissions = ["admin", "user_edit"]
    require_all_permissions = True  # User needs ALL of these
    
    def get(self, request):
        return Response({"message": "Full access granted"})


# ============================================================================
# Dependency Registration
# ============================================================================

# Add to core/di_container.py register_dependencies():
"""
from core.interfaces.security import IAuthenticationService, IAuthorizationService
from infrastructure.services.security import DjangoAuthenticationService, DjangoAuthorizationService

container.register_factory(
    IAuthenticationService,
    lambda: DjangoAuthenticationService()
)

container.register_factory(
    IAuthorizationService,
    lambda: DjangoAuthorizationService()
)
"""
