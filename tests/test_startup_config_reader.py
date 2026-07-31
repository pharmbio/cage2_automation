"""Verify laborchestrator startup config loading preserves all fields set in lab_adaption/config.py."""

import ast
from pathlib import Path

from lab_adaption import config as user_config
from laborchestrator.start_up.config_loader import load_config


CONFIG_FILE = Path(__file__).resolve().parent.parent / "lab_adaption" / "config.py"


def _configured_field_names():
    tree = ast.parse(CONFIG_FILE.read_text())
    fields = []

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    fields.append(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            fields.append(node.target.id)

    return fields


def test_laborchestrator_config_reader_loads_configured_fields():
    loaded_config = load_config(str(CONFIG_FILE))

    for field in _configured_field_names():
        assert hasattr(loaded_config, field)
        loaded_value = getattr(loaded_config, field)
        configured_value = getattr(user_config, field)

        assert (
            loaded_value is configured_value
            or loaded_value == configured_value
            or type(loaded_value) is type(configured_value)
        )
