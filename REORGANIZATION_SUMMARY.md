# Django Project Reorganization - Summary

## Overview
This document summarizes the reorganization of the PARTs WebAPI Django project to follow current Django best practices and improve maintainability.

## Changes Made

### 1. New Project Structure

The project has been reorganized with a `src/` layout that isolates application code from the repository root:

```
PARTs_WebAPI/
├── src/                          # NEW: Application code root
│   ├── parts_webapi/            # NEW: Django project package (renamed from 'api')
│   │   ├── settings/            # NEW: Split settings directory
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Common settings
│   │   │   ├── development.py   # Development-specific settings
│   │   │   ├── production.py    # Production-specific settings
│   │   │   └── test.py          # Test settings
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── manage.py                # NEW: Moved from root
│   ├── admin/                   # All Django apps moved to src/
│   ├── alerts/
│   ├── attendance/
│   ├── form/
│   ├── general/
│   ├── public/
│   ├── scouting/
│   ├── sponsoring/
│   ├── tba/
│   └── user/
├── tests/                       # Test suite (unchanged location)
├── templates/                   # Django templates (unchanged)
├── .env.example                 # NEW: Environment variables template
├── requirements.txt             # NEW: Pip requirements file
├── pyproject.toml              # Poetry configuration (updated)
├── pytest.ini                  # Updated for new structure
├── .github/workflows/ci.yml    # NEW: CI workflow
└── README.md                   # Completely rewritten
```

### 2. Settings Reorganization

**Old:** Single `api/settings.py` with inline environment checks
**New:** Split settings in `src/parts_webapi/settings/`:

- `base.py` - Common settings for all environments
- `development.py` - Development-specific (DEBUG=True, console emails, local CORS)
- `production.py` - Production-specific (DEBUG=False, security headers, production CORS)
- `test.py` - Test-specific (in-memory DB, disabled migrations, simplified auth)

**Key improvements:**
- Graceful handling of missing JWT keys (falls back to HS256 for development)
- Sensible defaults for all environment variables
- Clear separation of concerns

### 3. Environment Configuration

**New file:** `.env.example` provides a template for all required environment variables:
- SECRET_KEY
- DEBUG
- ENVIRONMENT
- Database configuration (DB_ENGINE, DB_NAME, etc.)
- Email settings
- API keys (Cloudinary, TBA, Discord)
- WebPush configuration

**Usage:**
```bash
cp .env.example .env
# Edit .env with your values
```

### 4. Django Settings Module

The default settings module is now `parts_webapi.settings.development`.

**To use different settings:**
```bash
# Option 1: Environment variable
export DJANGO_SETTINGS_MODULE=parts_webapi.settings.production

# Option 2: Command line
python src/manage.py runserver --settings=parts_webapi.settings.production

# Option 3: In .env file
DJANGO_SETTINGS_MODULE=parts_webapi.settings.production
```

### 5. Running the Application

**Old way:**
```bash
python manage.py runserver
```

**New way:**
```bash
cd src
python manage.py runserver
```

Or from repository root with Poetry:
```bash
poetry run python src/manage.py runserver
```

### 6. Testing

**Updated `pytest.ini`:**
- `DJANGO_SETTINGS_MODULE = parts_webapi.settings.test`
- `pythonpath = src` (allows imports to work correctly)
- Coverage now tracks `src/` instead of `.`

**Running tests:**
```bash
# From repository root
poetry run pytest

# Or with PYTHONPATH
PYTHONPATH=src pytest
```

**Test results:** 342 tests passed, 45.6% coverage

### 7. CI/CD

**New file:** `.github/workflows/ci.yml`

Features:
- Tests on Python 3.11 and 3.12
- Uses Poetry for dependency management
- Caches dependencies
- Reports coverage to Codecov
- Placeholder for linting

### 8. Dependencies

**New file:** `requirements.txt` - Extracted from Poetry dependencies for pip users

Core dependencies:
- Django 5.2.7
- djangorestframework 3.16.1
- djangorestframework-simplejwt 5.5.1
- python-dotenv 1.1.1
- And all other existing dependencies

### 9. Documentation

**Completely rewritten README.md** with:
- Updated project structure documentation
- Clear installation instructions
- Environment setup guide
- Settings module usage
- Testing instructions
- Deployment guidelines
- Manual testing steps for reviewers

## Breaking Changes

### For Developers

1. **manage.py location:** Now in `src/` directory
   - Old: `python manage.py <command>`
   - New: `python src/manage.py <command>` (from root) or `python manage.py <command>` (from src/)

2. **Settings module name:** Changed from `api.settings` to `parts_webapi.settings.development`
   - Update any deployment scripts or environment variables

3. **Import paths:** All unchanged - apps still use their original names
   - Example: `from user.models import User` still works

### For Deployment

1. Update `DJANGO_SETTINGS_MODULE` environment variable:
   - Old: `api.settings`
   - New: `parts_webapi.settings.production`

2. Update WSGI/ASGI application path:
   - Old: `api.wsgi:application`
   - New: `parts_webapi.wsgi:application`

3. Working directory should be `src/` or set `PYTHONPATH=src`

## Backward Compatibility

- All app import paths remain unchanged
- Database schema unchanged
- API endpoints unchanged
- Existing migrations work as-is
- All 342 existing tests pass

## Migration Steps for Team Members

1. **Pull the changes:**
   ```bash
   git checkout copilot/reorganize-django-project-structure
   git pull
   ```

2. **Reinstall dependencies:**
   ```bash
   poetry install --with dev
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

4. **Run migrations (if needed):**
   ```bash
   cd src
   python manage.py migrate
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```

6. **Run tests:**
   ```bash
   cd ..  # back to root
   poetry run pytest
   ```

## Benefits of New Structure

1. **Clearer separation:** Application code in `src/`, configuration at root
2. **Environment management:** Easy to switch between dev/staging/prod settings
3. **Better security:** Defaults prevent accidental production deployment with DEBUG=True
4. **Improved DX:** Clear documentation and setup instructions
5. **Modern practices:** Follows current Django community standards
6. **Easier testing:** Test settings isolated from application settings
7. **CI/CD ready:** Automated testing workflow included

## Files Modified/Added/Removed

### Added:
- `src/` directory with all application code
- `src/parts_webapi/settings/` with split settings files
- `.env.example`
- `requirements.txt`
- `.github/workflows/ci.yml`

### Modified:
- `README.md` (completely rewritten)
- `pytest.ini` (updated for new structure)
- All apps moved to `src/` (but code unchanged)

### Removed:
- `api/` directory (renamed to `parts_webapi`)
- `manage.py` from root (moved to `src/`)
- Old app directories from root (moved to `src/`)

## Notes

- The project uses Poetry for dependency management (unchanged)
- pyproject.toml remains at repository root (package-mode = false)
- All existing functionality preserved
- No data loss or migration required
