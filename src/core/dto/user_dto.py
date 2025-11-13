"""
Data Transfer Objects (DTOs) for the user domain.

DTOs are used to transfer data between layers without exposing
internal domain models or database entities.
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class UserDTO:
    """
    Data transfer object for user information.
    
    This DTO contains all user data needed by the presentation layer
    without coupling to Django models.
    """
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    name: str
    is_active: bool
    phone: Optional[str] = None
    discord_user_id: Optional[str] = None
    phone_type_id: Optional[int] = None
    image_url: Optional[str] = None
    groups: Optional[List[dict]] = None
    permissions: Optional[List[dict]] = None
    links: Optional[List[dict]] = None


@dataclass
class CreateUserDTO:
    """
    Data transfer object for creating a new user.
    """
    username: str
    email: str
    password: str
    first_name: str
    last_name: str


@dataclass
class UpdateUserDTO:
    """
    Data transfer object for updating user information.
    """
    user_id: int
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    discord_user_id: Optional[str] = None
    phone_type_id: Optional[int] = None
    is_active: Optional[bool] = None
    groups: Optional[List[str]] = None


@dataclass
class UserAuthDTO:
    """
    Data transfer object for user authentication.
    """
    username: str
    password: str


@dataclass
class PhoneTypeDTO:
    """
    Data transfer object for phone type information.
    """
    id: int
    carrier: str
    phone_type: str


@dataclass
class GroupDTO:
    """
    Data transfer object for group information.
    """
    id: int
    name: str
    permissions: Optional[List[dict]] = None


@dataclass
class PermissionDTO:
    """
    Data transfer object for permission information.
    """
    id: int
    name: str
    codename: str
    content_type_id: Optional[int] = None


@dataclass
class LinkDTO:
    """
    Data transfer object for navigation link information.
    """
    id: int
    menu_name: str
    routerlink: str
    order: int
    permission: Optional[PermissionDTO] = None
