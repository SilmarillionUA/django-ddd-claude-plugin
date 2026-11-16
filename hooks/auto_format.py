#!/usr/bin/env python3
"""
Formats the file Claude just edited, so diffs never carry style noise.

PostToolUse hook for Edit and Write. Python files go through isort and
black, templates through djade. It formats one file, not the tree, so
it stays fast. A formatter that is not installed is skipped.
"""

import json
import subprocess
import sys
from pathlib import Path

from project_config import load_config, project_root

VENV_PYTHON = Path(".venv") / "bin" / "python"
DJANGO_TARGET_VERSION_KEY = "django_target_version"
DEFAULT_DJANGO_TARGET_VERSION = "5.2"


def python_executable(*, root: Path) -> str:
    venv_python = root / VENV_PYTHON
    return str(venv_python) if venv_python.exists() else sys.executable


def commands_for(path: Path, *, root: Path, config: dict) -> list[list[str]]:
    python = python_executable(root=root)

    if path.suffix == ".py" and "migrations" not in path.parts:
        return [
            [python, "-m", "isort", "--settings-path", str(root), str(path)],
            [python, "-m", "black", "--quiet", str(path)],
        ]

    if path.suffix == ".html":
        target_version = config.get(
            DJANGO_TARGET_VERSION_KEY, DEFAULT_DJANGO_TARGET_VERSION
        )
        return [
            [
                python,
                "-m",
                "djade",
                "--target-version",
                target_version,
                str(path),
            ],
        ]

    return []


def main() -> int:
    root = project_root()
    config = load_config(root=root)
    if config is None:
        return 0

    tool_call = json.load(sys.stdin)
    file_path = tool_call.get("tool_input", {}).get("file_path", "")
    if not file_path or not Path(file_path).is_file():
        return 0

    for command in commands_for(Path(file_path), root=root, config=config):
        # Output is dropped on purpose: a formatter that is missing or
        # fails must never stop Claude's edit.
        subprocess.run(command, cwd=root, capture_output=True, check=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
