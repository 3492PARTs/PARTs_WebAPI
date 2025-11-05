import importlib
import sys
from unittest.mock import patch

def test_manage_main_calls_execute(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "api.settings")
    module_name = "manage"
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    import manage
    with patch("django.core.management.execute_from_command_line") as mock_exec:
        manage.main()
        mock_exec.assert_called_once()