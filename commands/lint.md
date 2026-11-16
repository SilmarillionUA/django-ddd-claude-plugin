---
description: Run the project's lint command and the DDD layer check.
---

Run the project's lint command named in `CLAUDE.md`, then the layer check from the project root: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/ddd_layer_guard.py" --all`. Report each issue with file and line, and suggest a fix.
