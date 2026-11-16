"""
Finds the project a hook runs in and reads its django-ddd config.

The init skill writes the config file. A project without it has not
opted in, so every hook does nothing there.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_DIR_VARIABLE = "CLAUDE_PROJECT_DIR"
CONFIG_PATH = Path(".claude") / "django-ddd.json"


def project_root() -> Path:
    return Path(os.environ.get(PROJECT_DIR_VARIABLE) or Path.cwd()).resolve()


def load_config(*, root: Path) -> dict | None:
    config_file = root / CONFIG_PATH
    if not config_file.is_file():
        return None

    return json.loads(config_file.read_text())
