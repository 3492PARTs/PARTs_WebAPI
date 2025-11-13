# Clean Architecture Implementation Guide

This document explains the clean architecture refactoring of the PARTs WebAPI Django REST Framework application.

## Overview

Clean Architecture is an architectural pattern that separates concerns into distinct layers, making the codebase:
- **Independent of frameworks**: Business logic doesn't depend on Django or DRF
- **Testable**: Use cases can be tested without UI, database, or external dependencies
- **Independent of UI**: The business logic doesn't know about REST APIs
- **Independent of database**: Business logic doesn't depend on Django ORM
- **Independent of external agencies**: Business logic doesn't know about external services

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│                  (views_clean.py, APIs)                  │
│         Thin HTTP handlers, authentication, etc.         │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│          (use_cases/, DTOs for data transfer)           │
│      Business logic, orchestration, validation          │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    Domain Layer                          │
│              (domain/, interfaces/)                      │
│      Entities, business rules, repository interfaces    │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                     │
│         (infrastructure/repositories/)                   │
│    Database access, external services, ORM details      │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/
├── core/                           # Core business logic and interfaces
│   ├── domain/                     # Domain entities and business rules
│   │   └── __init__.py
│   ├── use_cases/                  # Application business logic
│   │   ├── __init__.py
│   │   └── user_use_cases.py       # User-related use cases
│   ├── interfaces/                 # Repository interfaces (contracts)
│   │   ├── __init__.py
│   │   ├── repository.py           # Base repository interface
│   │   └── user_repository.py      # User repository interface
│   ├── dto/                        # Data Transfer Objects
│   │   ├── __init__.py
│   │   └── user_dto.py            # User DTOs
│   ├── di_container.py            # Dependency injection container
│   └── __init__.py
│
├── infrastructure/                 # External dependencies implementation
│   ├── repositories/              # Repository implementations
│   │   ├── __init__.py
│   │   └── user_repository.py     # Django ORM user repository
│   └── __init__.py
│
├── user/                          # User app (Django app)
│   ├── models.py                  # Django models (entities)
│   ├── views.py                   # Original views (legacy)
│   ├── views_clean.py             # Refactored clean architecture views
│   ├── serializers.py             # DRF serializers
│   ├── urls.py                    # URL routing
│   └── ...
│
└── [other Django apps...]
```

## Key Concepts

### 1. **Use Cases** (Application Layer)

Use cases contain the business logic and orchestrate operations. They:
- Are independent of frameworks (Django, DRF)
- Take DTOs as input and return DTOs as output
- Use repository interfaces (not concrete implementations)
- Can be easily tested with mocked repositories

**Example:**
```python
class GetUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def execute(self, user_id: int) -> UserDTO:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ObjectDoesNotExist(f"User with id {user_id} not found")
        
        # Business logic here
        return UserDTO(...)
```

### 2. **Repository Interfaces** (Domain Layer)

Interfaces define contracts for data access without specifying implementation:
- Define what operations are needed (get, create, update, delete)
- Don't depend on any ORM or database
- Enable dependency inversion

**Example:**
```python
class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
```

### 3. **Repository Implementations** (Infrastructure Layer)

Concrete implementations of repository interfaces:
- Handle Django ORM operations
- Implement the repository interface
- Can be swapped without affecting business logic

**Example:**
```python
class DjangoUserRepository(IUserRepository):
    def get_by_id(self, id: int) -> Optional[User]:
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None
```

### 4. **DTOs (Data Transfer Objects)**

Objects for transferring data between layers:
- Decouple business logic from Django models
- Simple dataclasses with no behavior
- Can be easily serialized/deserialized

**Example:**
```python
@dataclass
class UserDTO:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
```

### 5. **Views (Presentation Layer)**

Thin HTTP handlers that:
- Handle HTTP request/response
- Resolve dependencies from DI container
- Call use cases
- Serialize responses
- Don't contain business logic

**Example:**
```python
class UserProfileView(APIView):
    def get(self, request, format=None):
        # Resolve dependencies
        user_repo = resolve(IUserRepository)
        
        # Execute use case
        use_case = GetUserUseCase(user_repo)
        user_dto = use_case.execute(request.user.id)
        
        # Serialize and return
        serializer = UserSerializer(user_dto)
        return Response(serializer.data)
```

### 6. **Dependency Injection Container**

Manages dependencies and their lifetimes:
- Registers interfaces with implementations
- Resolves dependencies at runtime
- Supports singleton and transient lifetimes

**Example:**
```python
# Registration (in app startup)
container.register_factory(
    IUserRepository,
    lambda: DjangoUserRepository()
)

# Resolution (in views)
user_repo = resolve(IUserRepository)
```

## Migration Strategy

### Phase 1: Create Core Structure ✅
- [x] Create core/domain/, core/use_cases/, core/interfaces/, core/dto/
- [x] Create infrastructure/repositories/
- [x] Implement base repository interface
- [x] Create dependency injection container

### Phase 2: Refactor User Module (Example)
- [x] Create user repository interface
- [x] Implement Django user repository
- [x] Create user DTOs
- [x] Create user use cases
- [x] Create refactored views (views_clean.py)
- [ ] Update URL routing
- [ ] Write tests for use cases
- [ ] Write tests for repository

### Phase 3: Refactor Other Modules
- [ ] Apply same pattern to scouting module
- [ ] Apply same pattern to attendance module
- [ ] Apply same pattern to alerts module
- [ ] Apply same pattern to form module
- [ ] Apply same pattern to other modules

### Phase 4: Complete Migration
- [ ] Remove old views (views.py)
- [ ] Update all URL routes
- [ ] Update all tests
- [ ] Update documentation

## How to Use Clean Architecture

### Creating a New Feature

1. **Define the DTO** (if needed):
   ```python
   # core/dto/my_feature_dto.py
   @dataclass
   class MyFeatureDTO:
       id: int
       name: str
   ```

2. **Define the Repository Interface** (if needed):
   ```python
   # core/interfaces/my_feature_repository.py
   class IMyFeatureRepository(IRepository):
       @abstractmethod
       def get_by_name(self, name: str) -> Optional[MyFeature]:
           pass
   ```

3. **Implement the Repository**:
   ```python
   # infrastructure/repositories/my_feature_repository.py
   class DjangoMyFeatureRepository(IMyFeatureRepository):
       def get_by_name(self, name: str) -> Optional[MyFeature]:
           # Django ORM code here
   ```

4. **Create Use Cases**:
   ```python
   # core/use_cases/my_feature_use_cases.py
   class GetMyFeatureUseCase:
       def __init__(self, repo: IMyFeatureRepository):
           self.repo = repo
       
       def execute(self, feature_id: int) -> MyFeatureDTO:
           # Business logic here
   ```

5. **Register Dependencies**:
   ```python
   # core/di_container.py - in register_dependencies()
   container.register_factory(
       IMyFeatureRepository,
       lambda: DjangoMyFeatureRepository()
   )
   ```

6. **Create View**:
   ```python
   # myapp/views_clean.py
   class MyFeatureView(APIView):
       def get(self, request):
           repo = resolve(IMyFeatureRepository)
           use_case = GetMyFeatureUseCase(repo)
           result = use_case.execute(feature_id)
           return Response(...)
   ```

### Testing

Clean architecture makes testing much easier:

**Testing Use Cases:**
```python
def test_get_user_use_case():
    # Mock the repository
    mock_repo = MagicMock(spec=IUserRepository)
    mock_repo.get_by_id.return_value = User(...)
    
    # Test the use case
    use_case = GetUserUseCase(mock_repo)
    result = use_case.execute(1)
    
    assert result.username == "expected"
    mock_repo.get_by_id.assert_called_once_with(1)
```

**Testing Repositories:**
```python
@pytest.mark.django_db
def test_user_repository_get_by_id():
    # Create test data
    user = User.objects.create(username="test")
    
    # Test repository
    repo = DjangoUserRepository()
    result = repo.get_by_id(user.id)
    
    assert result.username == "test"
```

## Benefits

1. **Testability**: Business logic can be tested without Django test client
2. **Flexibility**: Easy to swap implementations (e.g., change database)
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Easy to add new features following the same pattern
5. **Independence**: Business logic doesn't depend on frameworks

## Best Practices

1. **Keep views thin**: Views should only handle HTTP and delegate to use cases
2. **Use DTOs**: Don't pass Django models between layers
3. **Dependency Inversion**: Depend on interfaces, not concrete implementations
4. **Single Responsibility**: Each use case should do one thing
5. **Don't mix layers**: Business logic stays in use cases, not views or models
6. **Test use cases**: Write unit tests for use cases with mocked repositories

## Comparison: Old vs New

### Old Architecture (views.py)
```python
class UserProfile(APIView):
    def get(self, request):
        # Direct database access
        usr = User.objects.get(id=request.user.id)
        permissions = get_user_permissions(request.user.id)
        user_links = Link.objects.filter(...)
        
        # Business logic mixed with view
        usr = {
            "id": usr.id,
            "username": usr.username,
            # ... more fields
        }
        
        return Response(UserSerializer(usr).data)
```

### New Architecture (views_clean.py)
```python
class UserProfileView(APIView):
    def get(self, request):
        # Resolve dependencies
        user_repo = resolve(IUserRepository)
        
        # Delegate to use case
        use_case = GetUserUseCase(user_repo)
        user_dto = use_case.execute(request.user.id)
        
        # Serialize and return
        return Response(UserSerializer(user_dto).data)
```

## Next Steps

1. Initialize DI container in Django app startup
2. Create tests for user use cases and repository
3. Update URL routing to use clean architecture views
4. Apply pattern to remaining modules
5. Gradually deprecate old views

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)
