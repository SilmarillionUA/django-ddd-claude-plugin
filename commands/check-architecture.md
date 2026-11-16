---
description: Run the DDD layer check and fix each violation.
---

Run the layer check from the project root: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/ddd_layer_guard.py" --all`. For each violation, explain which layer rule it breaks and fix it: move the code to the right layer, or add an interface in `domain/interfaces.py` with a gateway in `infrastructure/gateways.py` and wire it in `infrastructure/di.py`. Run the layer check and the project's test command again until both pass.
