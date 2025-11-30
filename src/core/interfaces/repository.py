"""
Base repository interfaces following the Repository Pattern.

These interfaces define contracts for data access operations,
enabling dependency inversion and easier testing.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from django.db.models import QuerySet, Model


T = TypeVar('T', bound=Model)


class IRepository(ABC, Generic[T]):
    """
    Generic repository interface for basic CRUD operations.
    
    This interface abstracts database operations, allowing
    business logic to be independent of the ORM implementation.
    """
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Retrieve an entity by its ID.
        
        Args:
            id: The primary key of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> QuerySet[T]:
        """
        Retrieve all entities.
        
        Returns:
            QuerySet containing all entities
        """
        pass
    
    @abstractmethod
    def filter(self, **kwargs) -> QuerySet[T]:
        """
        Filter entities based on criteria.
        
        Args:
            **kwargs: Filter criteria
            
        Returns:
            QuerySet of filtered entities
        """
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """
        Create a new entity.
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            The created entity
        """
        pass
    
    @abstractmethod
    def update(self, id: int, **kwargs) -> T:
        """
        Update an existing entity.
        
        Args:
            id: The entity ID
            **kwargs: Attributes to update
            
        Returns:
            The updated entity
        """
        pass
    
    @abstractmethod
    def delete(self, id: int) -> None:
        """
        Delete an entity.
        
        Args:
            id: The entity ID
        """
        pass
    
    @abstractmethod
    def exists(self, **kwargs) -> bool:
        """
        Check if an entity exists matching the criteria.
        
        Args:
            **kwargs: Filter criteria
            
        Returns:
            True if exists, False otherwise
        """
        pass
