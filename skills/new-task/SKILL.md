---
name: new-task
description: Add a background or scheduled task that delegates to a use case through the DI container. Use for background or periodic work, with whatever task runner the project uses.
---

# Create a background task

Create a task with the name the user gives in the app's `infrastructure/tasks.py`.

Use the task runner the project already has (see the project `CLAUDE.md`). Copy the decorator, retry settings and logging of an existing task. If the project has no task runner, write a management command that calls the same use case, and say so.

```python
import logging
from typing import Any

from django.utils import timezone

from {app}.infrastructure.di import {App}Container

logger = logging.getLogger(__name__)


def do_thing(*, thing_id: int) -> dict[str, Any]:
    logger.info("do_thing.started thing_id=%s", thing_id)

    use_case = {App}Container.get_do_thing_use_case()
    result = use_case.execute(thing_id=thing_id, today=timezone.localdate())

    logger.info("do_thing.completed thing_id=%s", thing_id)
    return {"thing_id": thing_id, "result": result}
```

## Rules

- The task is a thin shell: read arguments, call one use case from the container, log, return a dict.
- The task reads the clock and passes it to the use case.
- Retry only the specific errors worth retrying, never every exception.
- Pass ids, not model instances.
- Queue tasks from views with `transaction.on_commit`, so the worker never reads a row that is not there yet.
- Register the task and any schedule the way the project's runner needs.

## After creating

- Add a test in `infrastructure/tests/test_tasks.py` that calls the task directly.
- Run the project's format command (see `CLAUDE.md`).
