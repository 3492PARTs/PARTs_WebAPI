"""
Dependency Injection Container for Clean Architecture.

This module provides a simple dependency injection mechanism
to manage and resolve dependencies across the application.
"""
from typing import Dict, Any, Callable, Type, TypeVar

T = TypeVar('T')


class Container:
    """
    Simple dependency injection container.
    
    Manages the registration and resolution of dependencies,
    supporting singleton and transient lifetimes.
    """
    
    def __init__(self):
        """Initialize the container with empty registrations."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._transients: Dict[str, Callable[[], Any]] = {}
    
    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """
        Register a singleton instance.
        
        Args:
            interface: The interface/abstract class type
            instance: The concrete implementation instance
        """
        key = self._get_key(interface)
        self._singletons[key] = instance
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function for singleton creation.
        
        The factory will be called once and the result cached.
        
        Args:
            interface: The interface/abstract class type
            factory: Function that creates the implementation
        """
        key = self._get_key(interface)
        self._factories[key] = factory
    
    def register_transient(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a transient (new instance per resolve).
        
        Args:
            interface: The interface/abstract class type
            factory: Function that creates the implementation
        """
        key = self._get_key(interface)
        self._transients[key] = factory
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a dependency by its interface.
        
        Args:
            interface: The interface to resolve
            
        Returns:
            The resolved instance
            
        Raises:
            KeyError: If the interface is not registered
        """
        key = self._get_key(interface)
        
        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]
        
        # Check factories (create and cache)
        if key in self._factories:
            instance = self._factories[key]()
            self._singletons[key] = instance
            return instance
        
        # Check transients (create new every time)
        if key in self._transients:
            return self._transients[key]()
        
        raise KeyError(f"No registration found for {interface}")
    
    def _get_key(self, interface: Type) -> str:
        """
        Get a string key for the interface.
        
        Args:
            interface: The interface type
            
        Returns:
            String representation of the interface
        """
        return f"{interface.__module__}.{interface.__name__}"


# Global container instance
_container = Container()


def get_container() -> Container:
    """
    Get the global dependency injection container.
    
    Returns:
        The global Container instance
    """
    return _container


def register_dependencies() -> None:
    """
    Register all application dependencies.
    
    This function should be called during application startup
    to configure the dependency injection container.
    """
    from core.interfaces.user_repository import IUserRepository
    from infrastructure.repositories.user_repository import DjangoUserRepository
    
    # Register repositories
    container = get_container()
    container.register_factory(
        IUserRepository,
        lambda: DjangoUserRepository()
    )


def resolve(interface: Type[T]) -> T:
    """
    Resolve a dependency from the global container.
    
    Args:
        interface: The interface to resolve
        
    Returns:
        The resolved instance
    """
    return get_container().resolve(interface)
