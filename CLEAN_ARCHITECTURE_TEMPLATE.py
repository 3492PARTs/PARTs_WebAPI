"""
Template for Creating Clean Architecture Components

This file provides templates and examples for quickly creating
clean architecture components for new features or refactoring existing ones.
"""

# ============================================================================
# STEP 1: Define DTOs (Data Transfer Objects)
# Location: core/dto/your_module_dto.py
# ============================================================================

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class YourEntityDTO:
    """
    Data transfer object for YourEntity.
    
    Use dataclasses for simple, immutable data structures.
    Include only the data needed by the presentation layer.
    """
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True


@dataclass
class CreateYourEntityDTO:
    """DTO for creating a new entity."""
    name: str
    description: Optional[str] = None


@dataclass
class UpdateYourEntityDTO:
    """DTO for updating an entity."""
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================================
# STEP 2: Define Repository Interface
# Location: core/interfaces/your_module_repository.py
# ============================================================================

from abc import ABC, abstractmethod
from typing import Optional, List
from django.db.models import QuerySet

from core.interfaces.repository import IRepository


class IYourEntityRepository(IRepository):
    """
    Interface for YourEntity data access operations.
    
    Define only the operations your business logic needs.
    Don't expose Django ORM specifics in the interface.
    """
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Any]:
        """
        Retrieve an entity by name.
        
        Args:
            name: The name to search for
            
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_active_entities(self) -> QuerySet:
        """
        Get all active entities.
        
        Returns:
            QuerySet of active entities
        """
        pass
    
    @abstractmethod
    def search(self, query: str) -> QuerySet:
        """
        Search entities by query string.
        
        Args:
            query: Search query
            
        Returns:
            QuerySet of matching entities
        """
        pass


# ============================================================================
# STEP 3: Implement Repository
# Location: infrastructure/repositories/your_module_repository.py
# ============================================================================

from typing import Optional
from django.db.models import QuerySet, Q
from django.core.exceptions import ObjectDoesNotExist

from your_app.models import YourEntity
from core.interfaces.your_module_repository import IYourEntityRepository


class DjangoYourEntityRepository(IYourEntityRepository):
    """
    Django ORM implementation of IYourEntityRepository.
    
    This is where all the Django-specific code lives.
    """
    
    def get_by_id(self, id: int) -> Optional[YourEntity]:
        """Retrieve an entity by ID."""
        try:
            return YourEntity.objects.get(id=id)
        except YourEntity.DoesNotExist:
            return None
    
    def get_by_name(self, name: str) -> Optional[YourEntity]:
        """Retrieve an entity by name."""
        try:
            return YourEntity.objects.get(name=name)
        except YourEntity.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet[YourEntity]:
        """Retrieve all entities."""
        return YourEntity.objects.all().order_by('name')
    
    def filter(self, **kwargs) -> QuerySet[YourEntity]:
        """Filter entities based on criteria."""
        return YourEntity.objects.filter(**kwargs)
    
    def create(self, **kwargs) -> YourEntity:
        """Create a new entity."""
        return YourEntity.objects.create(**kwargs)
    
    def update(self, id: int, **kwargs) -> YourEntity:
        """Update an existing entity."""
        entity = self.get_by_id(id)
        if not entity:
            raise ObjectDoesNotExist(f"Entity with id {id} not found")
        
        for key, value in kwargs.items():
            setattr(entity, key, value)
        entity.save()
        return entity
    
    def delete(self, id: int) -> None:
        """Delete an entity."""
        entity = self.get_by_id(id)
        if entity:
            entity.delete()
    
    def exists(self, **kwargs) -> bool:
        """Check if an entity exists matching the criteria."""
        return YourEntity.objects.filter(**kwargs).exists()
    
    def get_active_entities(self) -> QuerySet[YourEntity]:
        """Get all active entities."""
        return YourEntity.objects.filter(is_active=True).order_by('name')
    
    def search(self, query: str) -> QuerySet[YourEntity]:
        """Search entities by query string."""
        return YourEntity.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('name')


# ============================================================================
# STEP 4: Create Use Cases
# Location: core/use_cases/your_module_use_cases.py
# ============================================================================

from typing import List
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from core.dto.your_module_dto import YourEntityDTO, CreateYourEntityDTO, UpdateYourEntityDTO
from core.interfaces.your_module_repository import IYourEntityRepository


class GetYourEntityUseCase:
    """
    Use case for retrieving an entity.
    
    Keep use cases focused on a single responsibility.
    """
    
    def __init__(self, repository: IYourEntityRepository):
        """
        Initialize with dependencies.
        
        Args:
            repository: Repository for data access
        """
        self.repository = repository
    
    def execute(self, entity_id: int) -> YourEntityDTO:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            YourEntityDTO
            
        Raises:
            ObjectDoesNotExist: If entity not found
        """
        entity = self.repository.get_by_id(entity_id)
        if not entity:
            raise ObjectDoesNotExist(f"Entity with id {entity_id} not found")
        
        # Convert to DTO
        return YourEntityDTO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
        )


class ListYourEntitiesUseCase:
    """Use case for listing entities."""
    
    def __init__(self, repository: IYourEntityRepository):
        self.repository = repository
    
    def execute(self, active_only: bool = False) -> List[YourEntityDTO]:
        """
        List entities.
        
        Args:
            active_only: Whether to return only active entities
            
        Returns:
            List of YourEntityDTO
        """
        if active_only:
            entities = self.repository.get_active_entities()
        else:
            entities = self.repository.get_all()
        
        return [
            YourEntityDTO(
                id=entity.id,
                name=entity.name,
                description=entity.description,
                is_active=entity.is_active,
            )
            for entity in entities
        ]


class CreateYourEntityUseCase:
    """Use case for creating an entity."""
    
    def __init__(self, repository: IYourEntityRepository):
        self.repository = repository
    
    def execute(self, dto: CreateYourEntityDTO) -> YourEntityDTO:
        """
        Create a new entity.
        
        Args:
            dto: Data for creating the entity
            
        Returns:
            Created YourEntityDTO
            
        Raises:
            ValidationError: If validation fails
        """
        # Business rule: Name must be unique
        if self.repository.get_by_name(dto.name):
            raise ValidationError(f"Entity with name '{dto.name}' already exists")
        
        # Business rule: Name must not be empty
        if not dto.name or not dto.name.strip():
            raise ValidationError("Name cannot be empty")
        
        # Create entity
        entity = self.repository.create(
            name=dto.name,
            description=dto.description,
        )
        
        return YourEntityDTO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
        )


class UpdateYourEntityUseCase:
    """Use case for updating an entity."""
    
    def __init__(self, repository: IYourEntityRepository):
        self.repository = repository
    
    def execute(self, dto: UpdateYourEntityDTO) -> YourEntityDTO:
        """
        Update an entity.
        
        Args:
            dto: Data for updating the entity
            
        Returns:
            Updated YourEntityDTO
            
        Raises:
            ObjectDoesNotExist: If entity not found
            ValidationError: If validation fails
        """
        entity = self.repository.get_by_id(dto.id)
        if not entity:
            raise ObjectDoesNotExist(f"Entity with id {dto.id} not found")
        
        # Business rule: Name must be unique (if changing)
        if dto.name and dto.name != entity.name:
            if self.repository.get_by_name(dto.name):
                raise ValidationError(f"Entity with name '{dto.name}' already exists")
        
        # Update fields
        update_data = {}
        if dto.name is not None:
            update_data['name'] = dto.name
        if dto.description is not None:
            update_data['description'] = dto.description
        if dto.is_active is not None:
            update_data['is_active'] = dto.is_active
        
        entity = self.repository.update(dto.id, **update_data)
        
        return YourEntityDTO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
        )


class DeleteYourEntityUseCase:
    """Use case for deleting an entity."""
    
    def __init__(self, repository: IYourEntityRepository):
        self.repository = repository
    
    def execute(self, entity_id: int) -> None:
        """
        Delete an entity.
        
        Args:
            entity_id: The entity ID
            
        Raises:
            ObjectDoesNotExist: If entity not found
        """
        entity = self.repository.get_by_id(entity_id)
        if not entity:
            raise ObjectDoesNotExist(f"Entity with id {entity_id} not found")
        
        # Business rule: Check if entity can be deleted
        # (e.g., check for dependencies)
        
        self.repository.delete(entity_id)


class SearchYourEntitiesUseCase:
    """Use case for searching entities."""
    
    def __init__(self, repository: IYourEntityRepository):
        self.repository = repository
    
    def execute(self, query: str) -> List[YourEntityDTO]:
        """
        Search entities by query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching YourEntityDTO
        """
        entities = self.repository.search(query)
        
        return [
            YourEntityDTO(
                id=entity.id,
                name=entity.name,
                description=entity.description,
                is_active=entity.is_active,
            )
            for entity in entities
        ]


# ============================================================================
# STEP 5: Create Views
# Location: your_app/views_clean.py
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from core.di_container import resolve
from core.interfaces.your_module_repository import IYourEntityRepository
from core.use_cases.your_module_use_cases import (
    GetYourEntityUseCase,
    ListYourEntitiesUseCase,
    CreateYourEntityUseCase,
    UpdateYourEntityUseCase,
    DeleteYourEntityUseCase,
    SearchYourEntitiesUseCase,
)
from core.dto.your_module_dto import CreateYourEntityDTO, UpdateYourEntityDTO
from your_app.serializers import YourEntitySerializer
from general.security import ret_message


app_url = "your_app/"


class YourEntityDetailView(APIView):
    """
    API endpoint for retrieving a single entity.
    
    GET /api/your-entity/{id}/
    """
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "detail/"
    
    def get(self, request, entity_id: int, format=None):
        """Get an entity by ID."""
        try:
            # Resolve repository
            repo = resolve(IYourEntityRepository)
            
            # Execute use case
            use_case = GetYourEntityUseCase(repo)
            dto = use_case.execute(entity_id)
            
            # Serialize and return
            serializer = YourEntitySerializer({
                "id": dto.id,
                "name": dto.name,
                "description": dto.description,
                "is_active": dto.is_active,
            })
            
            return Response(serializer.data)
        
        except ObjectDoesNotExist as e:
            return ret_message(
                str(e),
                True,
                app_url + self.endpoint,
                request.user.id,
            )
        except Exception as e:
            return ret_message(
                "An error occurred while retrieving the entity.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class YourEntityListView(APIView):
    """
    API endpoint for listing entities.
    
    GET /api/your-entity/
    """
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "list/"
    
    def get(self, request, format=None):
        """List entities with optional filtering."""
        try:
            # Parse query params
            active_only = request.query_params.get('active', 'false').lower() == 'true'
            
            # Resolve repository
            repo = resolve(IYourEntityRepository)
            
            # Execute use case
            use_case = ListYourEntitiesUseCase(repo)
            dtos = use_case.execute(active_only)
            
            # Serialize and return
            serializer = YourEntitySerializer([
                {
                    "id": dto.id,
                    "name": dto.name,
                    "description": dto.description,
                    "is_active": dto.is_active,
                }
                for dto in dtos
            ], many=True)
            
            return Response(serializer.data)
        
        except Exception as e:
            return ret_message(
                "An error occurred while listing entities.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )
    
    def post(self, request, format=None):
        """Create a new entity."""
        try:
            # Validate input (can use DRF serializer)
            # For simplicity, using request.data directly
            
            # Create DTO
            dto = CreateYourEntityDTO(
                name=request.data.get('name'),
                description=request.data.get('description'),
            )
            
            # Resolve repository
            repo = resolve(IYourEntityRepository)
            
            # Execute use case
            use_case = CreateYourEntityUseCase(repo)
            result_dto = use_case.execute(dto)
            
            # Serialize and return
            serializer = YourEntitySerializer({
                "id": result_dto.id,
                "name": result_dto.name,
                "description": result_dto.description,
                "is_active": result_dto.is_active,
            })
            
            return Response(serializer.data, status=201)
        
        except ValidationError as e:
            return ret_message(
                str(e),
                True,
                app_url + self.endpoint,
                request.user.id,
            )
        except Exception as e:
            return ret_message(
                "An error occurred while creating the entity.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


# ============================================================================
# STEP 6: Register Dependencies
# Location: core/di_container.py (add to register_dependencies())
# ============================================================================

# In core/di_container.py, add to register_dependencies():
"""
from core.interfaces.your_module_repository import IYourEntityRepository
from infrastructure.repositories.your_module_repository import DjangoYourEntityRepository

container.register_factory(
    IYourEntityRepository,
    lambda: DjangoYourEntityRepository()
)
"""


# ============================================================================
# STEP 7: Update URLs
# Location: your_app/urls.py
# ============================================================================

# from django.urls import path
# from your_app.views_clean import YourEntityDetailView, YourEntityListView
#
# urlpatterns = [
#     path('your-entity/', YourEntityListView.as_view(), name='your-entity-list'),
#     path('your-entity/<int:entity_id>/', YourEntityDetailView.as_view(), name='your-entity-detail'),
# ]


# ============================================================================
# STEP 8: Write Tests
# Location: tests/your_app/test_your_entity_use_cases.py
# ============================================================================

"""
import pytest
from unittest.mock import MagicMock
from django.core.exceptions import ObjectDoesNotExist

from core.use_cases.your_module_use_cases import GetYourEntityUseCase
from core.dto.your_module_dto import YourEntityDTO
from your_app.models import YourEntity


def test_get_your_entity_use_case():
    # Arrange
    mock_repo = MagicMock()
    mock_entity = YourEntity(
        id=1,
        name="Test Entity",
        description="Test Description",
        is_active=True
    )
    mock_repo.get_by_id.return_value = mock_entity
    
    use_case = GetYourEntityUseCase(mock_repo)
    
    # Act
    result = use_case.execute(1)
    
    # Assert
    assert isinstance(result, YourEntityDTO)
    assert result.id == 1
    assert result.name == "Test Entity"
    mock_repo.get_by_id.assert_called_once_with(1)


def test_get_your_entity_use_case_not_found():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    
    use_case = GetYourEntityUseCase(mock_repo)
    
    # Act & Assert
    with pytest.raises(ObjectDoesNotExist):
        use_case.execute(999)
"""
