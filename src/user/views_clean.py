"""
Refactored user views following Clean Architecture principles.

Views are now thin HTTP handlers that delegate to use cases.
Business logic has been extracted into use cases, and data access
is abstracted behind repository interfaces.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from core.di_container import resolve
from core.interfaces.user_repository import IUserRepository
from core.use_cases.user_use_cases import (
    GetUserUseCase,
    GetUsersUseCase,
    CreateUserUseCase,
    UpdateUserUseCase,
    CheckUserAccessUseCase,
    GetUsersInGroupUseCase,
    GetUsersWithPermissionUseCase,
)
from core.dto.user_dto import CreateUserDTO, UpdateUserDTO
from user.serializers import (
    UserSerializer,
    UserCreationSerializer,
    RetMessageSerializer,
)
from general.security import ret_message


app_url = "user/"


class UserProfileView(APIView):
    """
    API endpoint for user profile operations.
    
    Handles retrieving and updating user profiles using clean architecture.
    """
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "profile/"
    
    def get(self, request, format=None):
        """
        Get the authenticated user's profile.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response with user data or error
        """
        try:
            # Resolve dependencies
            user_repo = resolve(IUserRepository)
            
            # Execute use case
            use_case = GetUserUseCase(user_repo)
            user_dto = use_case.execute(request.user.id)
            
            # Serialize and return
            serializer = UserSerializer({
                "id": user_dto.id,
                "username": user_dto.username,
                "email": user_dto.email,
                "name": user_dto.name,
                "first_name": user_dto.first_name,
                "last_name": user_dto.last_name,
                "is_active": user_dto.is_active,
                "phone": user_dto.phone,
                "discord_user_id": user_dto.discord_user_id,
                "phone_type_id": user_dto.phone_type_id,
                "groups": user_dto.groups,
                "permissions": user_dto.permissions,
                "image": user_dto.image_url,
                "links": user_dto.links,
            })
            
            return Response(serializer.data)
        
        except ObjectDoesNotExist:
            return ret_message(
                "User not found.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )
        except Exception as e:
            return ret_message(
                "An error occurred while retrieving user profile.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    
    Handles new user sign-ups using clean architecture.
    """
    
    endpoint = "register/"
    
    def post(self, request):
        """
        Register a new user.
        
        Args:
            request: The HTTP request with user data
            
        Returns:
            Response with success/error message
        """
        try:
            # Validate input
            serializer = UserCreationSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    -1,
                    error_message=serializer.errors,
                )
            
            # Check passwords match
            if serializer.validated_data.get("password1") != serializer.validated_data.get("password2"):
                return ret_message(
                    "Passwords don't match.",
                    True,
                    app_url + self.endpoint,
                    -1,
                )
            
            # Create DTO
            create_dto = CreateUserDTO(
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password1"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
            )
            
            # Resolve dependencies and execute use case
            user_repo = resolve(IUserRepository)
            use_case = CreateUserUseCase(user_repo)
            user_dto = use_case.execute(create_dto)
            
            # TODO: Send confirmation email (would be another use case)
            
            return ret_message(
                "User created successfully. Please check your email for activation.",
                False,
                app_url + self.endpoint,
                user_dto.id,
            )
        
        except ValidationError as e:
            return ret_message(
                str(e),
                True,
                app_url + self.endpoint,
                -1,
            )
        except ValueError as e:
            return ret_message(
                str(e),
                True,
                app_url + self.endpoint,
                -1,
            )
        except Exception as e:
            return ret_message(
                "An error occurred during registration.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )


class UserListView(APIView):
    """
    API endpoint for listing users.
    
    Requires authentication and appropriate permissions.
    """
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "list/"
    
    def get(self, request, format=None):
        """
        Get a list of users filtered by parameters.
        
        Query params:
            - active: Filter by active status (1 for active, 0 for inactive, omit for all)
            - exclude_admin: Exclude admin users (true/false)
            
        Returns:
            Response with list of users or error
        """
        try:
            # Check access
            user_repo = resolve(IUserRepository)
            access_use_case = CheckUserAccessUseCase(user_repo)
            if not access_use_case.execute(request.user.id, ["admin", "user_view"]):
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
            
            # Parse query params
            active_param = request.query_params.get('active', None)
            is_active = None if active_param is None else active_param == '1'
            exclude_admin = request.query_params.get('exclude_admin', 'false').lower() == 'true'
            
            # Execute use case
            use_case = GetUsersUseCase(user_repo)
            users_dtos = use_case.execute(is_active, exclude_admin)
            
            # Serialize and return
            serializer = UserSerializer([
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": user.name,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                    "phone": user.phone,
                    "discord_user_id": user.discord_user_id,
                    "phone_type_id": user.phone_type_id,
                }
                for user in users_dtos
            ], many=True)
            
            return Response(serializer.data)
        
        except Exception as e:
            return ret_message(
                "An error occurred while retrieving users.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class UsersByGroupView(APIView):
    """
    API endpoint for getting users in a specific group.
    """
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "by-group/"
    
    def get(self, request, group_name: str, format=None):
        """
        Get all users in a specific group.
        
        Args:
            request: The HTTP request
            group_name: Name of the group
            
        Returns:
            Response with list of users or error
        """
        try:
            # Check access
            user_repo = resolve(IUserRepository)
            access_use_case = CheckUserAccessUseCase(user_repo)
            if not access_use_case.execute(request.user.id, ["admin", "user_view"]):
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
            
            # Execute use case
            use_case = GetUsersInGroupUseCase(user_repo)
            users_dtos = use_case.execute(group_name)
            
            # Serialize and return
            serializer = UserSerializer([
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": user.name,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": user.is_active,
                }
                for user in users_dtos
            ], many=True)
            
            return Response(serializer.data)
        
        except Exception as e:
            return ret_message(
                "An error occurred while retrieving users by group.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )
