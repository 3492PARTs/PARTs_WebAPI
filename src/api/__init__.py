"""
Compatibility module for backward compatibility with old 'api' module name.

This module redirects imports from the old 'api' module to the new 'parts_webapi' module.
This allows existing server configurations that reference 'api.settings' or 'api.wsgi'
to continue working without modification.
"""
