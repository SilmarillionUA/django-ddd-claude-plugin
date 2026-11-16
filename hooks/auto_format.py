#!/usr/bin/env python3
"""
Formats the file Claude just edited, so diffs never carry style noise.

PostToolUse hook for Edit and Write. The commands come from
`format_commands` in .claude/django-ddd.json, keyed by file suffix. Each
command is a list of arguments, and `{file}` stands for the edited file.
The plugin names no formatter itself, so a project with no commands set
gets no formatting.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from project_config import load_config, project_root

FORMAT_COMMANDS_KEY = "format_commands"
FILE_PLACEHOLDER = "{file}"


def commands_for(path: Path, *, config: dict) -> list[list[str]]:
    suffix_commands = config.get(FORMAT_COMMANDS_KEY, {}).get(path.suffix, [])

    return [
        [part.replace(FILE_PLACEHOLDER, str(path)) for part in command]
        for command in suffix_commands
    ]


def main() -> int:
    root = project_root()
    config = load_config(root=root)
    if config is None:
        return 0

    tool_call = json.load(sys.stdin)
    file_path = tool_call.get("tool_input", {}).get("file_path", "")
    if not file_path or not Path(file_path).is_file():
        return 0

    for command in commands_for(Path(file_path), config=config):
        # Output is dropped on purpose: a formatter that is missing or
        # fails must never stop Claude's edit.
        try:
            subprocess.run(command, cwd=root, capture_output=True, check=False)
        except FileNotFoundError:
            continue

    return 0


if __name__ == "__main__":
    sys.exit(main())
