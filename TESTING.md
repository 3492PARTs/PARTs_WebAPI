# Testing Strategy and Coverage Roadmap

## Current Status

✅ **52% Test Coverage Achieved** (up from 21% baseline)

- **300+ tests** implemented across all major modules
- **Comprehensive test infrastructure** in place
- **CI/CD pipeline** configured and running
- **All critical paths** have basic test coverage

## Test Infrastructure

### What's Complete

1. **Test Configuration**
   - `pytest.ini` configured for Django testing
   - `.coveragerc` with proper exclusions
   - `api/test_settings.py` for isolated test environment
   - `tests/conftest.py` with reusable fixtures

2. **Test Organization**
   - `tests/` directory organized by Django app following pytest best practices
   - Each app has its own subdirectory: `tests/<app_name>/`
   - Test files use pattern: `test_<component>_<type>.py`
   - Comprehensive fixtures in root `tests/conftest.py`
   - Directory structure:
     ```
     tests/
     ├── conftest.py              # Shared fixtures
     ├── admin/                   # Admin app tests
     ├── alerts/                  # Alerts app tests
     ├── attendance/              # Attendance app tests
     ├── form/                    # Form app tests
     ├── general/                 # General utilities tests
     ├── public/                  # Public API tests
     ├── scouting/                # Scouting app tests
     ├── sponsoring/              # Sponsoring app tests
     ├── tba/                     # TBA integration tests
     ├── user/                    # User app tests
     ├── project/                 # Project-level tests (URLs, apps, etc.)
     └── misc/                    # Coverage and meta tests
     ```

3. **CI/CD**
   - GitHub Actions workflow (`test-and-coverage.yml`)
   - Automated testing on Python 3.11-3.12
   - Coverage reporting to Codecov
   - Runs on all PRs and main branch pushes

## Coverage by Module

### ✅ Fully Tested (100% Coverage)

- `general/security.py` - Security and access control utilities
- `general/cloudinary.py` - Image upload and management
- `general/send_message.py` - Email, Discord, and webpush notifications
- `general/util.py` - Date/time utilities
- `api/test_settings.py` - Test configuration

### 🟡 Well Tested (>70% Coverage)

- `sponsoring/serializers.py` - 100%
- `user/serializers.py` - 93%
- `user/models.py` - 67%
- `sponsoring/models.py` - 92%
- `scouting/models.py` - 90%
- `form/models.py` - 89%
- `alerts/models.py` - 89%
- `attendance/models.py` - 86%

### 🔶 Partially Tested (30-70% Coverage)

- `admin/views.py` - 30%
- `user/views.py` - 28%
- `sponsoring/views.py` - 45%
- `sponsoring/util.py` - 23%
- `scouting/views.py` - 42%
- `scouting/util.py` - 25%
- `tba/views.py` - 34%
- `form/views.py` - 27%

### 🔴 Needs More Tests (<30% Coverage)

- `form/util.py` - 7% (874 statements, very large file)
- `scouting/admin/util.py` - 10% (334 statements)
- `scouting/admin/views.py` - 35%
- `scouting/field/util.py` - 15%
- `scouting/pit/util.py` - 16%
- `scouting/strategizing/util.py` - 16%
- `scouting/strategizing/views.py` - 35%
- `tba/util.py` - 16%
- `user/util.py` - 21%
- `alerts/util.py` - 18%
- `alerts/util_alert_definitions.py` - 14%
- `attendance/util.py` - 15%

## Roadmap to 100% Coverage

### Phase 1: High-Value Modules (Target: 70% total)

Focus on business-critical code with highest impact:

1. **User Authentication & Authorization**
   - Complete `user/views.py` tests (all 18 view classes)
   - Full `user/util.py` coverage (18 utility functions)
   - Test all JWT token flows
   - Test password reset and email confirmation

2. **API Security**
   - Comprehensive permission tests
   - Access control edge cases
   - Authentication failure scenarios

3. **Core Business Logic**
   - `form/util.py` - Form builder and response handling
   - `scouting/admin/util.py` - Schedule and event initialization
   - `tba/util.py` - TBA API integration

### Phase 2: Feature Completeness (Target: 85% total)

Complete testing for all user-facing features:

1. **Scouting System**
   - Field scouting views and utils
   - Pit scouting views and utils
   - Strategizing views and utils
   - Portal functionality

2. **Attendance Tracking**
   - Meeting management
   - Attendance approval workflows
   - Reporting functions

3. **Alerts System**
   - Alert staging and sending
   - Channel-specific delivery (email, Discord, webpush)
   - User alert retrieval and dismissal

4. **Forms System**
   - Question builder
   - Form responses
   - Answer validation

### Phase 3: Edge Cases & Error Handling (Target: 95% total)

Test error conditions and edge cases:

1. **Error Scenarios**
   - Invalid input validation
   - Database constraint violations
   - API timeout handling
   - Permission denied flows

2. **Edge Cases**
   - Empty result sets
   - Null/None value handling
   - Boundary conditions
   - Race conditions

### Phase 4: Final Coverage (Target: 100%)

1. **Integration Tests**
   - End-to-end workflows
   - Multi-step processes
   - Cross-module interactions

2. **Performance Edge Cases**
   - Large data sets
   - Pagination edge cases
   - Query optimization verification

## Testing Best Practices

### Writing Tests

```python
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestMyFeature:
    """Tests for my feature."""

    def test_success_case(self, api_client, test_user):
        """Test the happy path."""
        api_client.force_authenticate(user=test_user)
        response = api_client.get('/api/endpoint/')
        assert response.status_code == 200

    def test_permission_denied(self, api_client, test_user):
        """Test without permissions."""
        with patch('myapp.views.has_access', return_value=False):
            api_client.force_authenticate(user=test_user)
            response = api_client.get('/api/endpoint/')
            assert response.status_code == 403

    def test_with_mocked_dependency(self):
        """Test with mocked external dependency."""
        with patch('myapp.util.external_api_call') as mock_call:
            mock_call.return_value = {"data": "test"}
            result = my_function()
            assert result is not None
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests for a specific app
poetry run pytest tests/user/
poetry run pytest tests/scouting/

# Run specific test file
poetry run pytest tests/user/test_user_comprehensive.py

# Run with coverage
poetry run pytest --cov=.

# Run fast (no coverage)
poetry run pytest --no-cov -x

# Run specific test class or method
poetry run pytest tests/user/test_user_comprehensive.py::TestUserViews
poetry run pytest tests/user/test_user_comprehensive.py::TestUserViews::test_user_profile_get

# Run tests matching a pattern
poetry run pytest -k "test_user"

# Verbose output
poetry run pytest -v

# Show print statements
poetry run pytest -s
```

### Coverage Analysis

```bash
# Generate HTML coverage report
poetry run pytest --cov=. --cov-report=html
open htmlcov/index.html

# Show missing lines
poetry run pytest --cov=. --cov-report=term-missing

# Coverage for specific app or module
poetry run pytest --cov=user --cov-report=term-missing tests/user/

# Coverage for specific component
poetry run pytest --cov=user.views --cov-report=term-missing tests/user/test_user_views_extended.py
```

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach recommended)
2. **Place tests in the correct app directory** under `tests/<app_name>/`
3. **Test both success and failure cases**
4. **Mock external dependencies** (API calls, email, etc.)
5. **Use fixtures** from `conftest.py` for common setup
6. **Follow naming conventions**: 
   - Test files: `test_<component>_<type>.py` (e.g., `test_views_comprehensive.py`)
   - Test classes: `Test<ComponentName>` (e.g., `TestUserViews`)
   - Test methods: `test_<what>_<when>_<expected>` (e.g., `test_create_user_with_valid_data_succeeds`)
7. **Document complex test scenarios** with clear docstrings
8. **Run tests locally** before pushing
9. **Maintain or improve coverage** - never decrease it

### Test File Organization

Follow this structure when adding new tests:

```
tests/
├── <app_name>/
│   ├── test_models.py         # Model tests
│   ├── test_views.py          # View tests
│   ├── test_utils.py          # Utility function tests
│   ├── test_serializers.py    # Serializer tests
│   └── test_integration.py    # Integration tests
└── conftest.py                # Shared fixtures
```

**Note**: Test directories should NOT have `__init__.py` files to avoid namespace conflicts with Django app modules.

## Tools and Resources

- **pytest**: Test framework
- **pytest-django**: Django-specific test utilities
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Enhanced mocking
- **freezegun**: Time mocking
- **factory-boy**: Test data factories
- **requests-mock**: HTTP mocking

## Questions?

For testing questions or help reaching 100% coverage:
- Check existing tests in `tests/` for examples
- Review this document for patterns
- Reach out to team maintainers
