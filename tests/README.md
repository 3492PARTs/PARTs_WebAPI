# Test Organization

This directory contains all unit and integration tests for the PARTs WebAPI project, organized following Django pytest best practices.

## Directory Structure

Tests are organized by Django app to mirror the `src/` directory structure:

```
tests/
├── conftest.py              # Shared fixtures available to all tests
├── README.md                # This file
│
├── admin/                   # Admin app tests
│   └── test_admin_comprehensive.py
│
├── alerts/                  # Alerts app tests
│   ├── test_alerts_comprehensive.py
│   └── test_alerts_util_definitions.py
│
├── attendance/              # Attendance app tests
│   ├── test_attendance_comprehensive.py
│   └── test_attendance_integration.py
│
├── form/                    # Form builder app tests
│   ├── test_form_integration.py
│   ├── test_form_util_comprehensive.py
│   └── test_form_views_comprehensive.py
│
├── general/                 # General utilities tests
│   ├── test_general_cloudinary.py
│   ├── test_general_security.py
│   ├── test_general_send_message.py
│   └── test_general_util.py
│
├── public/                  # Public API tests
│   ├── test_public_api_status.py
│   └── test_public_comprehensive.py
│
├── scouting/                # Scouting system tests
│   ├── test_scouting_admin_comprehensive.py
│   ├── test_scouting_field_comprehensive.py
│   ├── test_scouting_pit_comprehensive.py
│   ├── test_scouting_portal_comprehensive.py
│   ├── test_scouting_simple.py
│   ├── test_scouting_util_extended.py
│   ├── test_scouting_views_extended.py
│   └── test_strategizing_comprehensive.py
│
├── sponsoring/              # Sponsoring app tests
│   └── test_sponsoring_comprehensive.py
│
├── tba/                     # The Blue Alliance integration tests
│   ├── test_tba_integration.py
│   ├── test_tba_util_comprehensive.py
│   ├── test_tba_util_extended.py
│   └── test_tba_views_comprehensive.py
│
├── user/                    # User app tests
│   ├── test_user_auth_comprehensive.py
│   ├── test_user_comprehensive.py
│   ├── test_user_integration.py
│   ├── test_user_util_extended.py
│   ├── test_user_views_extended.py
│   └── test_coverage_additional.py
│
├── project/                 # Project-level tests (URLs, apps config, etc.)
│   ├── test_api_urls.py
│   ├── test_apps_comprehensive.py
│   ├── test_bulk_modules.py
│   └── test_manage_py.py
│
└── misc/                    # Cross-cutting coverage tests
    └── test_coverage_misc.py
```

**Note**: Each app directory now also contains a `test_coverage_additional.py` file with additional coverage tests that were extracted from the misc folder.

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests for a specific app
```bash
pytest tests/user/
pytest tests/scouting/
```

### Run a specific test file
```bash
pytest tests/user/test_user_comprehensive.py
```

### Run a specific test class
```bash
pytest tests/user/test_user_comprehensive.py::TestUserViews
```

### Run a specific test method
```bash
pytest tests/user/test_user_comprehensive.py::TestUserViews::test_user_profile_get
```

### Run with coverage
```bash
pytest --cov=src --cov-report=term-missing
```

### Run tests matching a pattern
```bash
pytest -k "test_user"
```

## Writing New Tests

When adding tests for a new feature:

1. **Place test files in the appropriate app directory** under `tests/<app_name>/`
2. **Follow naming conventions**:
   - Test files: `test_<component>_<type>.py`
   - Test classes: `Test<ComponentName>`
   - Test methods: `test_<what>_<when>_<expected>`

3. **Use shared fixtures** from `conftest.py`:
   - `api_client` - DRF API client
   - `test_user` - Standard test user
   - `admin_user` - Admin user
   - `authenticated_api_client` - Pre-authenticated API client

4. **Example test structure**:
```python
import pytest
from unittest.mock import patch

@pytest.mark.django_db
class TestMyFeature:
    """Tests for my feature."""

    def test_success_case(self, api_client, test_user):
        """Test the happy path."""
        api_client.force_authenticate(user=test_user)
        response = api_client.get('/api/endpoint/')
        assert response.status_code == 200

    def test_error_case(self, api_client):
        """Test error handling."""
        response = api_client.get('/api/endpoint/')
        assert response.status_code == 401
```

## Test Organization Principles

This test suite follows Django pytest best practices:

1. **Mirror app structure**: Tests are organized to match the `src/` directory
2. **One app per directory**: Each Django app has its own test subdirectory
3. **Shared fixtures**: Common test setup lives in `conftest.py`
4. **Clear naming**: Test files clearly indicate what they test
5. **No __init__.py files**: Test directories don't have `__init__.py` to avoid namespace conflicts with app modules

## More Information

See [TESTING.md](../TESTING.md) in the repository root for:
- Coverage roadmap
- Testing best practices
- CI/CD configuration
- Tools and resources
