# Migration Guide: From Traditional Django to Clean Architecture

This guide helps you migrate existing Django REST Framework code to clean architecture.

## Table of Contents
1. [Understanding the Problem](#understanding-the-problem)
2. [Step-by-Step Migration](#step-by-step-migration)
3. [Common Patterns](#common-patterns)
4. [Checklist](#checklist)
5. [Examples](#examples)

## Understanding the Problem

### Current Architecture Issues

**Before (Traditional Django):**
```python
# views.py - Everything in one place
class UserProfile(APIView):
    def get(self, request):
        # Direct database access
        usr = User.objects.get(id=request.user.id)
        
        # Business logic mixed in
        permissions = Permission.objects.filter(group__user=usr).distinct()
        
        # More database queries
        user_links = Link.objects.filter(
            Q(permission__in=permissions) | Q(permission_id__isnull=True)
        ).order_by("order")
        
        # Data transformation
        usr = {
            "id": usr.id,
            "username": usr.username,
            "permissions": permissions,
            "links": user_links,
        }
        
        return Response(UserSerializer(usr).data)
```

**Problems:**
- ❌ Business logic in view (hard to test)
- ❌ Direct ORM usage (coupled to Django)
- ❌ No reusability (can't use this logic elsewhere)
- ❌ Hard to mock for testing
- ❌ Difficult to maintain as it grows

**After (Clean Architecture):**
```python
# views_clean.py - Thin HTTP handler
class UserProfileView(APIView):
    def get(self, request):
        # Resolve dependency
        repo = resolve(IUserRepository)
        
        # Execute use case
        use_case = GetUserUseCase(repo)
        user_dto = use_case.execute(request.user.id)
        
        # Return response
        return Response(UserSerializer(user_dto).data)

# use_cases/user_use_cases.py - Business logic
class GetUserUseCase:
    def __init__(self, repository: IUserRepository):
        self.repository = repository
    
    def execute(self, user_id: int) -> UserDTO:
        user = self.repository.get_by_id(user_id)
        permissions = self.repository.get_user_permissions(user_id)
        # ... business logic here
        return UserDTO(...)
```

**Benefits:**
- ✅ Business logic separate and testable
- ✅ Not coupled to Django
- ✅ Reusable in other contexts (CLI, background jobs, etc.)
- ✅ Easy to mock repositories for testing
- ✅ Follows SOLID principles

## Step-by-Step Migration

### Step 1: Identify What to Migrate

Start with a single Django app or feature. Good candidates:
- Self-contained features
- Features with complex business logic
- Features that need extensive testing

### Step 2: Create DTOs

Extract data structures from your models:

```python
# Before: Using Django model directly
def get_user(user_id):
    return User.objects.get(id=user_id)

# After: Use DTO
@dataclass
class UserDTO:
    id: int
    username: str
    email: str
    is_active: bool

def get_user(user_id) -> UserDTO:
    user = repository.get_by_id(user_id)
    return UserDTO(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active
    )
```

### Step 3: Define Repository Interface

Identify all database operations and create interface:

```python
# Look at your existing code
def get_active_users():
    return User.objects.filter(is_active=True)

def get_user_by_email(email):
    return User.objects.get(email=email)

# Create interface
class IUserRepository(ABC):
    @abstractmethod
    def get_active_users(self) -> QuerySet:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
```

### Step 4: Implement Repository

Move ORM code to repository:

```python
class DjangoUserRepository(IUserRepository):
    def get_active_users(self) -> QuerySet:
        return User.objects.filter(is_active=True)
    
    def get_by_email(self, email: str) -> Optional[User]:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
```

### Step 5: Extract Business Logic to Use Cases

Move logic from views/utils to use cases:

```python
# Before: In views.py or util.py
def save_user(data):
    u = User.objects.get(username=data["username"])
    u.first_name = data["first_name"]
    u.last_name = data["last_name"]
    u.email = data["email"].lower()
    u.save()
    
    # Update groups
    for d in data["groups"]:
        group = Group.objects.get(name=d["name"])
        u.groups.add(group)
    
    return u

# After: In use_cases/user_use_cases.py
class UpdateUserUseCase:
    def __init__(self, repository: IUserRepository):
        self.repository = repository
    
    def execute(self, dto: UpdateUserDTO) -> UserDTO:
        user = self.repository.get_by_id(dto.user_id)
        
        # Business logic
        if dto.email:
            user.email = dto.email.lower()
        if dto.first_name:
            user.first_name = dto.first_name
        
        user.save()
        
        # Update groups
        if dto.groups:
            self.repository.add_user_to_groups(dto.user_id, dto.groups)
        
        return UserDTO(...)
```

### Step 6: Refactor Views

Make views thin HTTP handlers:

```python
# Before: Fat view with business logic
class UserUpdateView(APIView):
    def post(self, request):
        try:
            if not has_access(request.user.id, ["admin"]):
                return ret_message("No access", True, "user/", request.user.id)
            
            # Business logic
            u = User.objects.get(username=request.data["username"])
            u.first_name = request.data["first_name"]
            u.email = request.data["email"].lower()
            u.save()
            
            # More business logic
            for group_data in request.data["groups"]:
                group = Group.objects.get(name=group_data["name"])
                u.groups.add(group)
            
            return Response(UserSerializer(u).data)
        except Exception as e:
            return ret_message("Error", True, "user/", request.user.id, e)

# After: Thin view delegating to use case
class UserUpdateView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            # Check access
            if not self.check_access(request):
                return ret_message("No access", True, "user/", request.user.id)
            
            # Create DTO
            dto = UpdateUserDTO(
                user_id=request.user.id,
                first_name=request.data.get("first_name"),
                email=request.data.get("email"),
                groups=request.data.get("groups", [])
            )
            
            # Execute use case
            repo = resolve(IUserRepository)
            use_case = UpdateUserUseCase(repo)
            result = use_case.execute(dto)
            
            # Return response
            return Response(UserSerializer(result).data)
        except Exception as e:
            return ret_message("Error", True, "user/", request.user.id, e)
```

### Step 7: Register Dependencies

Add to `core/di_container.py`:

```python
def register_dependencies():
    container = get_container()
    
    container.register_factory(
        IUserRepository,
        lambda: DjangoUserRepository()
    )
```

### Step 8: Update Tests

Write tests for use cases:

```python
# Before: Testing through HTTP
def test_update_user(client, user):
    client.force_authenticate(user=user)
    response = client.post('/api/user/update/', {
        'first_name': 'New Name'
    })
    assert response.status_code == 200

# After: Testing use case directly
def test_update_user_use_case():
    # Mock repository
    mock_repo = MagicMock(spec=IUserRepository)
    mock_user = User(id=1, first_name="Old")
    mock_repo.get_by_id.return_value = mock_user
    
    # Test use case
    use_case = UpdateUserUseCase(mock_repo)
    dto = UpdateUserDTO(user_id=1, first_name="New")
    result = use_case.execute(dto)
    
    assert result.first_name == "New"
    mock_repo.get_by_id.assert_called_once_with(1)
```

## Common Patterns

### Pattern 1: Simple CRUD

```python
# Repository
class IEntityRepository(IRepository):
    pass  # Inherits basic CRUD

# Use Cases
class GetEntityUseCase:
    def execute(self, id: int) -> EntityDTO:
        entity = self.repository.get_by_id(id)
        return EntityDTO(...)

# View
class EntityView(APIView):
    def get(self, request, id):
        repo = resolve(IEntityRepository)
        use_case = GetEntityUseCase(repo)
        dto = use_case.execute(id)
        return Response(serializer.data)
```

### Pattern 2: Complex Business Logic

```python
# Use Case with multiple steps
class ProcessScoutingDataUseCase:
    def __init__(
        self,
        scouting_repo: IScoutingRepository,
        team_repo: ITeamRepository,
        notification_service: INotificationService
    ):
        self.scouting_repo = scouting_repo
        self.team_repo = team_repo
        self.notification_service = notification_service
    
    def execute(self, dto: ScoutingDataDTO) -> ProcessResultDTO:
        # Step 1: Validate
        self._validate_data(dto)
        
        # Step 2: Save
        response = self.scouting_repo.create_field_response(**dto.dict())
        
        # Step 3: Update rankings
        self._update_rankings(dto.season_id)
        
        # Step 4: Notify team
        team = self.team_repo.get_by_id(dto.team_id)
        self.notification_service.notify(team, "New scouting data")
        
        return ProcessResultDTO(...)
```

### Pattern 3: Authorization

```python
# Base class for secured views
class SecureView(APIView):
    required_permissions = []
    
    def dispatch(self, request, *args, **kwargs):
        auth_service = resolve(IAuthorizationService)
        use_case = CheckUserAccessUseCase(auth_service)
        result = use_case.execute(request.user.id, self.required_permissions)
        
        if not result.has_access:
            return ret_message("No access", True, self.endpoint, request.user.id)
        
        return super().dispatch(request, *args, **kwargs)

# Usage
class AdminView(SecureView):
    required_permissions = ["admin"]
    
    def get(self, request):
        # User already authorized
        return Response(...)
```

## Checklist

Use this checklist when migrating a feature:

### Planning
- [ ] Identify the feature/app to migrate
- [ ] List all database operations
- [ ] List all business rules
- [ ] Identify external dependencies

### Implementation
- [ ] Create DTOs for data transfer
- [ ] Define repository interface
- [ ] Implement repository with Django ORM
- [ ] Create use cases with business logic
- [ ] Refactor views to be thin handlers
- [ ] Register dependencies in DI container
- [ ] Update URL routing (if needed)

### Testing
- [ ] Write unit tests for use cases
- [ ] Write integration tests for repositories
- [ ] Update existing view tests
- [ ] Verify no regressions

### Documentation
- [ ] Document new use cases
- [ ] Update API documentation
- [ ] Add migration notes

## Examples

### Example 1: Simple Model Migration

**Before:**
```python
# models.py
class PhoneType(models.Model):
    carrier = models.CharField(max_length=255)
    phone_type = models.CharField(max_length=255)

# util.py
def get_phone_types():
    return PhoneType.objects.all().order_by("carrier")

def delete_phone_type(phone_type_id):
    phone_type = PhoneType.objects.get(id=phone_type_id)
    if phone_type.user_set.exists():
        raise ValueError("Can't delete, users tied to this phone type.")
    phone_type.delete()

# views.py
class PhoneTypeView(APIView):
    def get(self, request):
        phone_types = get_phone_types()
        return Response(PhoneTypeSerializer(phone_types, many=True).data)
```

**After:**
```python
# core/dto/user_dto.py
@dataclass
class PhoneTypeDTO:
    id: int
    carrier: str
    phone_type: str

# core/interfaces/phone_type_repository.py
class IPhoneTypeRepository(IRepository):
    @abstractmethod
    def get_all_ordered(self) -> QuerySet:
        pass
    
    @abstractmethod
    def has_users(self, phone_type_id: int) -> bool:
        pass

# infrastructure/repositories/phone_type_repository.py
class DjangoPhoneTypeRepository(IPhoneTypeRepository):
    def get_all_ordered(self) -> QuerySet:
        return PhoneType.objects.all().order_by("carrier")
    
    def has_users(self, phone_type_id: int) -> bool:
        phone_type = self.get_by_id(phone_type_id)
        return phone_type.user_set.exists() if phone_type else False

# core/use_cases/phone_type_use_cases.py
class GetPhoneTypesUseCase:
    def __init__(self, repository: IPhoneTypeRepository):
        self.repository = repository
    
    def execute(self) -> List[PhoneTypeDTO]:
        phone_types = self.repository.get_all_ordered()
        return [PhoneTypeDTO(id=pt.id, carrier=pt.carrier, phone_type=pt.phone_type) 
                for pt in phone_types]

class DeletePhoneTypeUseCase:
    def __init__(self, repository: IPhoneTypeRepository):
        self.repository = repository
    
    def execute(self, phone_type_id: int) -> None:
        if self.repository.has_users(phone_type_id):
            raise ValueError("Can't delete, users tied to this phone type.")
        self.repository.delete(phone_type_id)

# user/views_clean.py
class PhoneTypeView(APIView):
    def get(self, request):
        repo = resolve(IPhoneTypeRepository)
        use_case = GetPhoneTypesUseCase(repo)
        dtos = use_case.execute()
        return Response(PhoneTypeSerializer(dtos, many=True).data)
    
    def delete(self, request, phone_type_id):
        try:
            repo = resolve(IPhoneTypeRepository)
            use_case = DeletePhoneTypeUseCase(repo)
            use_case.execute(phone_type_id)
            return ret_message("Phone type deleted", False, "user/phone-type/", request.user.id)
        except ValueError as e:
            return ret_message(str(e), True, "user/phone-type/", request.user.id)
```

## Tips

1. **Start Small**: Begin with one feature/app
2. **Test As You Go**: Write tests for each use case
3. **Keep Old Code**: Create `views_clean.py` alongside `views.py`
4. **Gradual Migration**: You can run both architectures side-by-side
5. **Document Decisions**: Keep notes on why you structure things certain ways
6. **Get Feedback**: Review with team before migrating more code

## Common Pitfalls

❌ **Don't** expose Django models in use case return values
✅ **Do** return DTOs

❌ **Don't** put business logic in repositories
✅ **Do** keep repositories focused on data access

❌ **Don't** make use cases depend on concrete implementations
✅ **Do** use interfaces and dependency injection

❌ **Don't** skip writing tests
✅ **Do** write unit tests for use cases with mocked repositories

## Next Steps

1. Pick your first app/feature to migrate
2. Follow the step-by-step guide above
3. Write tests
4. Get code review
5. Deploy and monitor
6. Move to next feature

For questions or help, see `CLEAN_ARCHITECTURE.md` and `CLEAN_ARCHITECTURE_TEMPLATE.py`.
