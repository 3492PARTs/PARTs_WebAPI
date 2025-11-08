# Documentation Index

This directory contains comprehensive documentation for the PARTs WebAPI project.

## Setup and Configuration

- **[POETRY.md](POETRY.md)** - Complete guide to Poetry setup, dependency management, and usage
  - Installing Poetry
  - Managing dependencies and dependency groups
  - Working with virtual environments
  - Common commands and workflows
  - Project-specific configurations

## Project History and Changes

- **[REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)** - Django project structure reorganization
  - Migration to `src/` layout
  - Settings split (base, dev, prod, test)
  - Breaking changes and migration guide
  
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Django best practices refactoring
  - Code quality improvements
  - URL namespacing and explicit imports
  - Documentation additions
  - Metrics and benefits

## Quick Links to Other Documentation

### In Repository Root

- **[README.md](../README.md)** - Main project documentation
  - Project overview and setup
  - Development workflow
  - Testing instructions
  - Deployment guide

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
  - Development workflow
  - Code style and standards
  - Pull request process
  - Adding new features

- **[DJANGO_BEST_PRACTICES.md](../DJANGO_BEST_PRACTICES.md)** - Coding standards
  - Project structure guidelines
  - URL configuration patterns
  - Views and serializers best practices
  - Security guidelines

- **[TESTING.md](../TESTING.md)** - Testing strategy
  - Test organization
  - Coverage roadmap
  - Running tests
  - Writing new tests

### In Tests Directory

- **[tests/README.md](../tests/README.md)** - Test suite organization
  - Directory structure
  - Running specific tests
  - Test fixtures and patterns
  - Test organization principles

## Documentation Organization

### Repository Root (`/`)
Contains the primary documentation that developers need frequently:
- Main README with setup and usage
- Contributing guidelines
- Django best practices
- Testing strategy

### docs/ Directory (`/docs/`)
Contains supplementary documentation and historical records:
- Poetry setup guide
- Project reorganization history
- Refactoring summaries
- Architecture decision records (future)

### tests/ Directory (`/tests/`)
Contains test-specific documentation:
- Test organization guide
- Test fixture reference
- Testing patterns and examples

## Finding the Right Document

**I want to...**

- **Set up the project** → [README.md](../README.md)
- **Use Poetry** → [POETRY.md](POETRY.md)
- **Contribute code** → [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Follow coding standards** → [DJANGO_BEST_PRACTICES.md](../DJANGO_BEST_PRACTICES.md)
- **Write tests** → [TESTING.md](../TESTING.md) and [tests/README.md](../tests/README.md)
- **Understand project history** → [REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md) and [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
- **Run tests** → [tests/README.md](../tests/README.md)

## Documentation Standards

When adding new documentation:

1. **Choose the right location:**
   - Frequently needed docs → Repository root
   - Setup guides and references → `docs/`
   - Test-specific docs → `tests/`

2. **Update this index** when adding new documents

3. **Use clear, descriptive filenames** (e.g., `POETRY.md` not `dependencies.md`)

4. **Include:**
   - Clear title and purpose
   - Table of contents for long documents
   - Code examples where relevant
   - Links to related documentation

5. **Keep documentation up-to-date:**
   - Update docs when changing functionality
   - Mark outdated sections clearly
   - Remove obsolete documentation

## Contributing to Documentation

Documentation improvements are always welcome! When updating docs:

1. Follow the existing format and style
2. Use clear, concise language
3. Include examples for complex concepts
4. Test any code snippets you include
5. Update this index if adding new files
6. Submit a pull request with your changes

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contribution process.
