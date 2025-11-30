"""
Use cases for user management.

Use cases contain the business logic and orchestrate operations
between repositories and external services. They are independent
of frameworks and can be easily tested.
"""
from typing import Optional, List, Dict, Any
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password

from core.dto.user_dto import (
    UserDTO,
    CreateUserDTO,
    UpdateUserDTO,
    PhoneTypeDTO,
    GroupDTO,
    PermissionDTO,
    LinkDTO,
)
from core.interfaces.user_repository import IUserRepository


class GetUserUseCase:
    """
    Use case for retrieving user information.
    
    This encapsulates the business logic for getting comprehensive
    user data including permissions and accessible links.
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, user_id: int) -> UserDTO:
        """
        Retrieve comprehensive user information.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            UserDTO containing user information
            
        Raises:
            ObjectDoesNotExist: If user not found
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ObjectDoesNotExist(f"User with id {user_id} not found")
        
        # Get user permissions
        permissions = self.user_repository.get_user_permissions(user_id)
        
        # Get user groups
        groups = self.user_repository.get_user_groups(user_id)
        
        # Build image URL (assuming cloudinary integration)
        image_url = None
        if user.img_id and user.img_ver:
            # This would call a cloudinary service in a real implementation
            image_url = f"cloudinary://{user.img_id}/{user.img_ver}"
        
        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            name=user.get_full_name(),
            is_active=user.is_active,
            phone=user.phone,
            discord_user_id=user.discord_user_id,
            phone_type_id=user.phone_type_id,
            image_url=image_url,
            groups=[{"id": g.id, "name": g.name} for g in groups],
            permissions=[{"id": p.id, "name": p.name, "codename": p.codename} for p in permissions],
        )


class GetUsersUseCase:
    """
    Use case for retrieving filtered list of users.
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, is_active: Optional[bool] = None, exclude_admin: bool = False) -> List[UserDTO]:
        """
        Retrieve filtered list of users.
        
        Args:
            is_active: Filter by active status (None for all users)
            exclude_admin: Whether to exclude admin users
            
        Returns:
            List of UserDTO objects
        """
        if is_active is None:
            users = self.user_repository.get_all()
        else:
            users = self.user_repository.get_users_by_active_status(is_active, exclude_admin)
        
        return [
            UserDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                name=user.get_full_name(),
                is_active=user.is_active,
                phone=user.phone,
                discord_user_id=user.discord_user_id,
                phone_type_id=user.phone_type_id,
            )
            for user in users
        ]


class CreateUserUseCase:
    """
    Use case for creating a new user.
    
    Handles user registration with validation and business rules.
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, dto: CreateUserDTO) -> UserDTO:
        """
        Create a new user.
        
        Args:
            dto: Data transfer object with user information
            
        Returns:
            UserDTO of created user
            
        Raises:
            ValidationError: If validation fails
            ValueError: If user already exists
        """
        # Validate password
        try:
            validate_password(dto.password)
        except ValidationError as e:
            raise ValidationError(f"Password validation failed: {e}")
        
        # Check if user exists
        if self.user_repository.get_by_email(dto.email.lower()):
            raise ValueError("User already exists with that email")
        
        if self.user_repository.get_by_username(dto.username.lower()):
            raise ValueError("User already exists with that username")
        
        # Create user (initially inactive for email confirmation)
        user = self.user_repository.create(
            username=dto.username.lower(),
            email=dto.email.lower(),
            first_name=dto.first_name,
            last_name=dto.last_name,
            is_active=False,
        )
        
        # Set password
        user.set_password(dto.password)
        user.save()
        
        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            name=user.get_full_name(),
            is_active=user.is_active,
        )


class UpdateUserUseCase:
    """
    Use case for updating user information.
    
    Handles updating user profile and group memberships.
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, dto: UpdateUserDTO) -> UserDTO:
        """
        Update user information.
        
        Args:
            dto: Data transfer object with update data
            
        Returns:
            Updated UserDTO
            
        Raises:
            ObjectDoesNotExist: If user not found
        """
        user = self.user_repository.get_by_id(dto.user_id)
        if not user:
            raise ObjectDoesNotExist(f"User with id {dto.user_id} not found")
        
        # Update fields if provided
        if dto.username:
            user.username = dto.username
        if dto.email:
            user.email = dto.email.lower()
        if dto.first_name:
            user.first_name = dto.first_name
        if dto.last_name:
            user.last_name = dto.last_name
        if dto.phone is not None:
            user.phone = dto.phone
        if dto.discord_user_id is not None:
            user.discord_user_id = dto.discord_user_id
        if dto.phone_type_id is not None:
            user.phone_type_id = dto.phone_type_id
        if dto.is_active is not None:
            user.is_active = dto.is_active
        
        user.save()
        
        # Update groups if provided
        if dto.groups is not None:
            # Add new groups
            self.user_repository.add_user_to_groups(dto.user_id, dto.groups)
            
            # Remove old groups not in the new list
            current_groups = self.user_repository.get_user_groups(dto.user_id)
            groups_to_remove = [g.name for g in current_groups if g.name not in dto.groups]
            if groups_to_remove:
                self.user_repository.remove_user_from_groups(dto.user_id, groups_to_remove)
        
        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            name=user.get_full_name(),
            is_active=user.is_active,
            phone=user.phone,
            discord_user_id=user.discord_user_id,
            phone_type_id=user.phone_type_id,
        )


class CheckUserAccessUseCase:
    """
    Use case for checking if a user has specific permissions.
    
    Encapsulates the authorization logic.
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, user_id: int, required_permissions: List[str]) -> bool:
        """
        Check if user has at least one of the required permissions.
        
        Args:
            user_id: The user ID
            required_permissions: List of permission codenames
            
        Returns:
            True if user has access, False otherwise
        """
        if not required_permissions:
            return True
        
        user_permissions = self.user_repository.get_user_permissions(user_id)
        user_permission_codenames = {p.codename for p in user_permissions}
        
        return any(perm in user_permission_codenames for perm in required_permissions)


class GetUsersInGroupUseCase:
    """
    Use case for retrieving users in a specific group.
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, group_name: str) -> List[UserDTO]:
        """
        Get all active users in a group.
        
        Args:
            group_name: Name of the group
            
        Returns:
            List of UserDTO objects
        """
        users = self.user_repository.get_users_in_group(group_name)
        
        return [
            UserDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                name=user.get_full_name(),
                is_active=user.is_active,
            )
            for user in users
        ]


class GetUsersWithPermissionUseCase:
    """
    Use case for retrieving users with a specific permission.
    """
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository
    
    def execute(self, permission_codename: str) -> List[UserDTO]:
        """
        Get all users with a specific permission.
        
        Args:
            permission_codename: The permission codename
            
        Returns:
            List of UserDTO objects
        """
        users = self.user_repository.get_users_with_permission(permission_codename)
        
        return [
            UserDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                name=user.get_full_name(),
                is_active=user.is_active,
            )
            for user in users
        ]
