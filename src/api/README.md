# Backward Compatibility Module

This directory contains a backward compatibility shim for the old `api` module name.

## Purpose

During the project reorganization, the main Django project package was renamed from `api` to `parts_webapi` to better reflect the project name and follow Django naming conventions. However, existing production server configurations may still reference the old module name.

This compatibility layer ensures that both old and new module references work correctly.

## What This Does

The modules in this directory redirect imports from the old `api` namespace to the new `parts_webapi` namespace:

- **`api.settings`** → redirects to `parts_webapi.settings.production`
- **`api.wsgi`** → redirects to `parts_webapi.wsgi`
- **`api.asgi`** → redirects to `parts_webapi.asgi`

## Server Configuration

If your production server is configured with:
```
DJANGO_SETTINGS_MODULE=api.settings
```
or references:
```
api.wsgi:application
```

These will continue to work without any changes to your server configuration.

## Migration Path

While this compatibility layer allows old configurations to work, we recommend updating your server configuration to use the new module names:

**Old:**
```bash
DJANGO_SETTINGS_MODULE=api.settings
WSGIScriptAlias / /path/to/api/wsgi.py
```

**New (recommended):**
```bash
DJANGO_SETTINGS_MODULE=parts_webapi.settings.production
WSGIScriptAlias / /path/to/parts_webapi/wsgi.py
```

## Future

This compatibility layer can be removed once all production servers have been updated to use the new `parts_webapi` module name. Until then, it ensures a smooth transition without downtime.
