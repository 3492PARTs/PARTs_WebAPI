# Clean Architecture Implementation

This document describes the clean architecture patterns implemented in the PARTs WebAPI project.

## Overview

The project has been refactored to follow clean architecture principles, with clear separation between:
- **API Layer** (Views)
- **Service Layer** (Business Logic)
- **Repository Layer** (Data Access)
- **Domain Layer** (Models)

## Architecture Layers

### 1. Domain Layer (Models)
Located in: `<app>/models.py`

Contains Django ORM models that represent the core business entities. These are the heart of the application and should have minimal dependencies.

**Example:**
```python
# user/models.py
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    # ... other fields
```

### 2. Repository Layer
Located in: `<app>/repositories/`

Repositories encapsulate all database access logic. They provide a clean interface for querying and manipulating data, isolating the service layer from Django ORM details.

**Responsibilities:**
- Execute database queries
- Handle ORM-specific logic
- Return model instances or QuerySets
- No business logic

**Example:**
```python
# user/repositories/user_repository.py
class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> User:
        """Get a user by ID."""
        return User.objects.get(id=user_id)
    
    @staticmethod
    def filter_users(active: Optional[bool] = None) -> QuerySet[User]:
        """Filter users by criteria."""
        queryset = User.objects.all()
        if active is not None:
            queryset = queryset.filter(is_active=active)
        return queryset
```

### 3. Service Layer
Located in: `<app>/services/`

Services contain the business logic of the application. They coordinate between repositories and implement business rules.

**Responsibilities:**
- Implement business logic
- Coordinate multiple repositories
- Handle complex operations
- Validate business rules
- Transform data for presentation
- No direct database access

**Example:**
```python
# user/services/user_service.py
class UserService:
    def __init__(self, user_repo=None, permission_repo=None):
        self.user_repo = user_repo or UserRepository()
        self.permission_repo = permission_repo or PermissionRepository()
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user information."""
        user = self.user_repo.get_by_id(user_id)
        permissions = self.permission_repo.get_user_permissions(user)
        
        return {
            "id": user.id,
            "username": user.username,
            "permissions": permissions,
            # ... build complete user info
        }
```

### 4. API Layer (Views)
Located in: `<app>/views.py`

Views handle HTTP requests and responses. They delegate business logic to services and focus on request/response handling.

**Responsibilities:**
- Handle HTTP requests
- Validate request data
- Call appropriate services
- Format responses
- Handle authentication/authorization
- No business logic
- No direct database access

**Example:**
```python
# user/views.py (future refactored version)
class UserView(APIView):
    def __init__(self):
        self.user_service = UserService()
    
    def get(self, request, user_id):
        """Get user information."""
        try:
            user_info = self.user_service.get_user_info(user_id)
            serializer = UserSerializer(user_info)
            return Response(serializer.data)
        except Exception as e:
            return ret_message("Error getting user", True, "user/", request.user.id, e)
```

## Dependency Flow

The dependency flow follows the Dependency Inversion Principle:

```
Views (API Layer)
  ↓ depends on
Services (Business Logic)
  ↓ depends on
Repositories (Data Access)
  ↓ depends on
Models (Domain)
```

**Key Rules:**
- Inner layers don't depend on outer layers
- Dependencies point inward
- Services don't know about Views
- Repositories don't know about Services

## Implementation Status

### Completed Modules

#### User Module
- ✅ `UserRepository`: User data access
- ✅ `PermissionRepository`: Permission, Group, Link data access
- ✅ `UserService`: User management business logic
- ✅ `PermissionService`: Permission and group management
- ✅ `AuthService`: Authentication logic (placeholder)

#### General Module
- ✅ `AuthorizationService`: Authorization and access control

### Backward Compatibility

All legacy functions in `user/util.py` and `general/security.py` have been updated to delegate to the new service layer. This ensures:
- No breaking changes to existing code
- Gradual migration path
- All tests continue to pass

**Example:**
```python
# user/util.py (backward compatibility wrapper)
def get_user(user_id: int) -> dict[str, Any]:
    """
    DEPRECATED: Use UserService.get_user_info() instead.
    Maintained for backward compatibility.
    """
    service = UserService()
    return service.get_user_info(user_id)
```

## Dependency Injection

Services use constructor injection for dependencies, enabling:
- Easy testing with mocks
- Flexibility to swap implementations
- Better separation of concerns

**Example:**
```python
# Testing with dependency injection
def test_get_user_info():
    mock_user_repo = Mock()
    mock_permission_repo = Mock()
    
    service = UserService(
        user_repo=mock_user_repo,
        permission_repo=mock_permission_repo
    )
    
    # Test the service with mocked dependencies
    result = service.get_user_info(1)
```

## Benefits of This Architecture

### 1. Testability
- Services can be tested independently with mocked repositories
- Repositories can be tested with in-memory databases
- Views can be tested with mocked services

### 2. Maintainability
- Business logic is centralized in services
- Data access is isolated in repositories
- Changes to one layer don't affect others

### 3. Reusability
- Services can be used from multiple views
- Repositories can be shared across services
- Business logic isn't duplicated

### 4. Flexibility
- Easy to swap database implementations
- Business rules can change without affecting data access
- Can add new presentation layers (GraphQL, gRPC) easily

### 5. SOLID Principles
- **Single Responsibility**: Each layer has one reason to change
- **Open/Closed**: Easy to extend without modifying existing code
- **Liskov Substitution**: Repositories and services are substitutable
- **Interface Segregation**: Clean, focused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Migration Guide

### For New Features

When adding new features, follow this pattern:

1. **Add models** if needed in `<app>/models.py`
2. **Create repository methods** in `<app>/repositories/`
3. **Implement business logic** in `<app>/services/`
4. **Add view endpoints** in `<app>/views.py`

### For Existing Code

When refactoring existing code:

1. **Create repository** for data access
2. **Create service** for business logic
3. **Update view** to use service
4. **Keep old functions** as deprecated wrappers initially
5. **Update all callers** to use new services
6. **Remove deprecated wrappers** when safe

## Code Examples

### Complete Flow Example

```python
# 1. Repository (Data Access)
class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> User:
        return User.objects.get(id=user_id)

# 2. Service (Business Logic)
class UserService:
    def __init__(self, user_repo=None):
        self.user_repo = user_repo or UserRepository()
    
    def activate_user(self, user_id: int) -> User:
        """Activate a user and send notification."""
        user = self.user_repo.get_by_id(user_id)
        user.is_active = True
        user.save()
        
        # Business logic: send notification
        send_activation_email(user)
        
        return user

# 3. View (API Layer)
class ActivateUserView(APIView):
    def __init__(self):
        self.user_service = UserService()
    
    def post(self, request, user_id):
        """Activate a user."""
        try:
            user = self.user_service.activate_user(user_id)
            return Response({"message": "User activated"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
```

## Testing Strategy

### Repository Tests
Test data access logic with real database:
```python
@pytest.mark.django_db
def test_user_repository_get_by_id():
    user = User.objects.create(username="test")
    repo = UserRepository()
    result = repo.get_by_id(user.id)
    assert result == user
```

### Service Tests
Test business logic with mocked repositories:
```python
def test_user_service_activate_user():
    mock_repo = Mock()
    mock_user = Mock(is_active=False)
    mock_repo.get_by_id.return_value = mock_user
    
    service = UserService(user_repo=mock_repo)
    result = service.activate_user(1)
    
    assert mock_user.is_active is True
```

### View Tests
Test HTTP handling with mocked services:
```python
@pytest.mark.django_db
def test_activate_user_view():
    with patch('user.views.UserService') as MockService:
        mock_service = MockService.return_value
        mock_service.activate_user.return_value = Mock()
        
        response = client.post('/api/users/1/activate/')
        assert response.status_code == 200
```

## Future Improvements

1. **Extend to Other Modules**: Apply this pattern to scouting, form, attendance, etc.
2. **Add Use Cases**: For complex business operations, create dedicated use case classes
3. **Domain Events**: Implement event-driven architecture for cross-module communication
4. **DTOs**: Add Data Transfer Objects to decouple API from domain models
5. **Specification Pattern**: For complex queries, implement specification pattern in repositories

## Resources

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/tags/domain%20driven%20design.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
