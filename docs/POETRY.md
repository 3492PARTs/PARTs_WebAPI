# Poetry Setup and Usage Guide

## What is Poetry?

Poetry is a modern Python dependency management and packaging tool that provides:
- **Dependency Resolution**: Automatically resolves and locks dependencies
- **Virtual Environments**: Creates and manages isolated Python environments
- **Reproducible Builds**: Lock file ensures consistent installations across all environments
- **Easy Dependency Management**: Simple commands to add, update, and remove packages

## Installation

### Installing Poetry

**macOS / Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Alternative (via pip):**
```bash
pip install poetry
```

### Verify Installation
```bash
poetry --version
```

### Shell Completion (Optional)
Poetry supports tab completion for bash, zsh, and fish:

```bash
# Bash
poetry completions bash >> ~/.bash_completion

# Zsh
poetry completions zsh > ~/.zfunc/_poetry

# Fish
poetry completions fish > ~/.config/fish/completions/poetry.fish
```

## Project Configuration

This project is configured with Poetry using the following files:

### pyproject.toml
The main configuration file that defines:
- Project metadata (name, version, description, authors)
- Python version requirement (`^3.11`)
- All project dependencies
- Dependency groups (dev, wvnet, uat)
- Build system configuration

### poetry.lock
Auto-generated lock file that:
- Locks exact versions of all dependencies (including transitive ones)
- Ensures reproducible installations
- Should be committed to version control

### poetry.toml
Project-specific Poetry settings:
```toml
[virtualenvs]
create = true
in-project = true
```

This configuration creates the virtual environment inside the project directory (`.venv/`), making it easier to manage and discover.

## Getting Started with This Project

### 1. Clone the Repository
```bash
git clone https://github.com/3492PARTs/PARTs_WebAPI.git
cd PARTs_WebAPI
```

### 2. Install Dependencies

**Install only production dependencies:**
```bash
poetry install --no-dev
```

**Install with development dependencies (recommended for contributors):**
```bash
poetry install --with dev
```

**Install all optional dependency groups:**
```bash
poetry install --with dev,wvnet,uat
```

### 3. Activate the Virtual Environment

**Option 1: Use poetry run (recommended)**
```bash
poetry run python src/manage.py runserver
poetry run pytest
```

**Option 2: Activate the shell**
```bash
poetry shell
# Now you're in the virtual environment
python src/manage.py runserver
pytest
```

**Option 3: Direct shell activation**
```bash
# Unix/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

## Dependency Groups

This project defines several dependency groups for different use cases:

### Main Dependencies (Required)
These are the core dependencies required to run the application:

```toml
[tool.poetry.dependencies]
python = "^3.11"
django = "5.2.8"
djangorestframework = "3.16.1"
djangorestframework-simplejwt = "5.5.1"
django-cors-headers = "4.8.0"
django-filter = "25.1"
django-simple-history = "3.10.1"
django-webpush = "0.3.6"
cloudinary = "1.44.1"
gunicorn = "23.0.0"
python-dotenv = "1.1.1"
requests = "2.32.5"
pillow = "11.3.0"
# ... and other core dependencies
```

**Installation:**
```bash
poetry install
```

### Development Group (Optional)
Testing and development tools:

```toml
[tool.poetry.group.dev]
optional = true

[tool.poetry.group.dev.dependencies]
pipdeptree = "^2.23.4"          # Visualize dependency tree
pytest = "^8.0.0"                # Test framework
pytest-django = "^4.8.0"         # Django plugin for pytest
pytest-cov = "^6.0.0"            # Coverage reporting
pytest-mock = "^3.14.0"          # Enhanced mocking
freezegun = "^1.5.0"             # Time mocking for tests
factory-boy = "^3.3.0"           # Test data factories
requests-mock = "^1.12.0"        # HTTP request mocking
faker = "^33.0.0"                # Fake data generation
```

**Installation:**
```bash
poetry install --with dev
```

**Use for:**
- Running tests (`pytest`)
- Code coverage reports
- Development and debugging
- Test data generation

### WVNet Group (Optional)
Dependencies for WVNet deployment environment:

```toml
[tool.poetry.group.wvnet]
optional = true

[tool.poetry.group.wvnet.dependencies]
gunicorn = "23.0.0"              # WSGI HTTP server
uwsgi = "2.0.30"                 # Application server
mysqlclient = "2.2.7"            # MySQL database adapter
```

**Installation:**
```bash
poetry install --with wvnet
```

**Use for:**
- WVNet production deployments
- MySQL database connections
- uWSGI application server setup

### UAT Group (Optional)
Dependencies for User Acceptance Testing (staging) environment:

```toml
[tool.poetry.group.uat]
optional = true

[tool.poetry.group.uat.dependencies]
gunicorn = "23.0.0"              # WSGI HTTP server
uwsgi = "2.0.30"                 # Application server
psycopg2-binary = "*"            # PostgreSQL database adapter
```

**Installation:**
```bash
poetry install --with uat
```

**Use for:**
- UAT/staging deployments
- PostgreSQL database connections
- Pre-production testing

## Common Poetry Commands

### Managing Dependencies

**Add a new dependency:**
```bash
# Add to main dependencies
poetry add django-extensions

# Add to dev group
poetry add --group dev black

# Add with version constraint
poetry add "django>=4.0,<5.0"
```

**Remove a dependency:**
```bash
poetry remove package-name
```

**Update dependencies:**
```bash
# Update all dependencies
poetry update

# Update specific package
poetry update django

# Update packages in a group
poetry update --with dev
```

**Show installed packages:**
```bash
poetry show

# Show as a tree
poetry show --tree

# Show only dev dependencies
poetry show --only dev
```

**Check for outdated packages:**
```bash
poetry show --outdated
```

### Running Commands

**Run a command in the virtual environment:**
```bash
poetry run python src/manage.py migrate
poetry run pytest
poetry run python src/manage.py runserver
```

**Activate shell:**
```bash
poetry shell
```

**Exit shell:**
```bash
exit
```

### Environment Management

**Show environment info:**
```bash
poetry env info
```

**List environments:**
```bash
poetry env list
```

**Remove environment:**
```bash
poetry env remove python3.11
```

**Use a specific Python version:**
```bash
poetry env use python3.11
poetry env use python3.12
```

### Lock File Management

**Update lock file without installing:**
```bash
poetry lock --no-update
```

**Update lock file and upgrade dependencies:**
```bash
poetry lock
```

**Install from lock file exactly:**
```bash
poetry install --sync
```

## Working with Requirements.txt

If you need a `requirements.txt` file (for deployment platforms that don't support Poetry):

**Export all dependencies:**
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

**Export with dev dependencies:**
```bash
poetry export -f requirements.txt --output requirements.txt --with dev --without-hashes
```

**Export specific groups:**
```bash
poetry export -f requirements.txt --output requirements.txt --with dev,wvnet --without-hashes
```

## Project-Specific Workflows

### Development Setup
```bash
# 1. Install with dev dependencies
poetry install --with dev

# 2. Set up environment
cp .env.example .env
# Edit .env with your settings

# 3. Run migrations
poetry run python src/manage.py migrate

# 4. Run tests
poetry run pytest

# 5. Start development server
poetry run python src/manage.py runserver
```

### Running Tests
```bash
# All tests with coverage
poetry run pytest

# Without coverage (faster)
poetry run pytest --no-cov

# Specific test file
poetry run pytest tests/user/test_user_comprehensive.py

# Verbose output
poetry run pytest -v
```

### WVNet Deployment
```bash
# Install with WVNet dependencies
poetry install --without dev --with wvnet

# Start with gunicorn
cd src
poetry run gunicorn parts_webapi.wsgi:application --bind 0.0.0.0:8000
```

### UAT Deployment
```bash
# Install with UAT dependencies
poetry install --without dev --with uat

# Run migrations
poetry run python src/manage.py migrate --settings=parts_webapi.settings.production

# Start with gunicorn
cd src
poetry run gunicorn parts_webapi.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Virtual Environment Not Found
```bash
# Recreate the virtual environment
poetry env remove python3.11
poetry install --with dev
```

### Dependency Conflicts
```bash
# Clear cache and reinstall
poetry cache clear pypi --all
poetry install --with dev
```

### Lock File Out of Sync
```bash
# Regenerate lock file
poetry lock --no-update
poetry install --with dev
```

### Poetry Command Not Found
```bash
# Add Poetry to PATH (after installation)
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall
curl -sSL https://install.python-poetry.org | python3 -
```

### Slow Dependency Resolution
```bash
# Use newer installer (faster)
poetry config installer.modern-installation true
```

## Configuration Options

### Global Configuration

**List current config:**
```bash
poetry config --list
```

**Set PyPI credentials:**
```bash
poetry config pypi-token.pypi <your-token>
```

**Configure virtualenv location:**
```bash
# Create in project directory (already configured for this project)
poetry config virtualenvs.in-project true

# Create in global cache
poetry config virtualenvs.in-project false
```

### Project Configuration

The project uses `poetry.toml` for project-specific settings:
```toml
[virtualenvs]
create = true
in-project = true
```

This ensures consistent virtual environment location across all developers.

## Best Practices

### For Contributors
1. **Always use Poetry** for dependency management
2. **Commit poetry.lock** to ensure reproducible builds
3. **Use dependency groups** appropriately (dev, wvnet, uat)
4. **Run tests** before committing: `poetry run pytest`
5. **Keep dependencies updated** regularly
6. **Use specific version constraints** when adding critical dependencies

### Adding New Dependencies
```bash
# 1. Add the dependency
poetry add package-name

# 2. Test that it works
poetry run pytest

# 3. Commit both pyproject.toml and poetry.lock
git add pyproject.toml poetry.lock
git commit -m "Add package-name dependency"
```

### Updating Dependencies
```bash
# 1. Update dependencies
poetry update

# 2. Run tests to ensure nothing broke
poetry run pytest

# 3. Commit the updated lock file
git add poetry.lock
git commit -m "Update dependencies"
```

## Comparison with pip/virtualenv

| Feature | Poetry | pip + virtualenv |
|---------|--------|------------------|
| Dependency Resolution | ✅ Automatic | ❌ Manual |
| Lock File | ✅ Yes (poetry.lock) | ⚠️ Manual (requirements.txt) |
| Virtual Environment | ✅ Automatic | ❌ Manual creation |
| Dependency Groups | ✅ Built-in | ❌ Multiple requirement files |
| Add/Remove Packages | ✅ `poetry add/remove` | ⚠️ `pip install` + manual requirements update |
| Version Constraints | ✅ Flexible syntax | ⚠️ Less flexible |
| Build System | ✅ Integrated | ❌ Separate tools |

## Additional Resources

- **Official Documentation**: https://python-poetry.org/docs/
- **PyPI Package Index**: https://pypi.org/
- **Dependency Groups**: https://python-poetry.org/docs/managing-dependencies/#dependency-groups
- **Version Constraints**: https://python-poetry.org/docs/dependency-specification/
- **Commands Reference**: https://python-poetry.org/docs/cli/

## Quick Reference

```bash
# Setup
poetry install                           # Install dependencies
poetry install --with dev                # Install with dev group
poetry install --with dev,wvnet,uat      # Install all groups

# Add/Remove
poetry add package-name                  # Add dependency
poetry add --group dev package-name      # Add to dev group
poetry remove package-name               # Remove dependency

# Update
poetry update                            # Update all
poetry update package-name               # Update specific package

# Run
poetry run <command>                     # Run command
poetry shell                             # Activate shell

# Info
poetry show                              # List packages
poetry show --tree                       # Show as tree
poetry show --outdated                   # Check for updates
poetry env info                          # Environment info

# Export
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Questions or Issues?

For questions about Poetry usage in this project:
1. Check this documentation
2. See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
3. Review the [official Poetry documentation](https://python-poetry.org/docs/)
4. Open an issue on GitHub for project-specific questions
