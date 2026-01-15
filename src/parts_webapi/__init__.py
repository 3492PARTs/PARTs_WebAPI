"""
Django app initialization.

This module initializes the dependency injection container
for clean architecture on application startup.
"""


def setup_clean_architecture():
    """
    Initialize clean architecture dependencies.
    
    This function is called during Django startup to register
    all dependencies in the DI container.
    """
    try:
        from core.di_container import register_dependencies
        register_dependencies()
    except ImportError:
        # Clean architecture not yet fully set up
        pass


# Initialize clean architecture on app startup
setup_clean_architecture()
