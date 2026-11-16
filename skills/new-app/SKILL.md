---
name: new-app
description: Scaffold a new bounded context as a Django app with domain, application and infrastructure layers, and wire it into settings. Use when the user asks for a new app or a new bounded context.
---

# Create a new Django app with DDD layers

Create a new app with the name the user gives under the apps root named in the project `CLAUDE.md` (`src/apps/` by default). Copy the style of an existing app when there is one.

## Directory structure

```
{apps_root}/{app_name}/
├── __init__.py
├── CLAUDE.md
├── conftest.py
├── domain/
│   ├── __init__.py
│   ├── models.py
│   ├── managers.py
│   ├── choices.py
│   ├── exceptions.py
│   ├── interfaces.py
│   ├── settings.py
│   ├── types.py
│   ├── services/__init__.py
│   └── tests/__init__.py
├── application/
│   ├── __init__.py
│   ├── use_cases/__init__.py
│   └── tests/__init__.py
└── infrastructure/
    ├── __init__.py
    ├── apps.py
    ├── admin.py
    ├── di.py
    ├── gateways.py
    ├── urls.py
    ├── views.py
    ├── tasks.py
    ├── migrations/__init__.py
    ├── templates/{app_name}/
    └── tests/__init__.py
```

## Wiring

**`{app_name}/__init__.py`:**
```python
import sys

from {app_name}.infrastructure import apps

# Django looks for <app>.apps. The config lives in infrastructure/.
sys.modules["{app_name}.apps"] = apps
```

**`{app_name}/infrastructure/apps.py`:**
```python
from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class {AppName}Config(AppConfig):
    name = "{app_name}"
    label = "{app_name}"
    verbose_name = _("{App Name}")

    def import_models(self) -> None:
        # Models live in domain/models.py. Setting models_module keeps
        # post_migrate signals (permissions, content types) firing.
        self.models = self.apps.all_models[self.label]
        self.models_module = import_module("{app_name}.domain.models")

    def ready(self) -> None:
        import_module("{app_name}.infrastructure.admin")
```

Django's command finder does not scan `infrastructure/management/`, so each command is registered by name:

```python
from django.core.management import get_commands

MANAGEMENT_COMMANDS = ("send_due_reminders",)
COMMANDS_PACKAGE = "{app_name}.infrastructure"

# at the end of ready():
commands = get_commands()
for command_name in MANAGEMENT_COMMANDS:
    commands[command_name] = COMMANDS_PACKAGE
```

## Settings

The apps root must be on `sys.path`, so the app imports as `{app_name}`, not `apps.{app_name}`. Find the base settings module, the Celery module and the root URLconf in the project `CLAUDE.md`.

1. Add `"{app_name}"` to `LOCAL_APPS` in the base settings module.
2. Add `"{app_name}": "{app_name}.infrastructure.migrations"` to `MIGRATION_MODULES`.
3. Add the path of `{app_name}/infrastructure/templates` to `TEMPLATES[0]["DIRS"]`, built the way the other entries are.
4. Add `"{app_name}.infrastructure"` to `autodiscover_tasks` in the project's Celery module if the app has tasks.
5. Include `{app_name}.infrastructure.urls` in the root URLconf if the app has views.

## After creating

- Write the app's `CLAUDE.md` (max 30 lines).
- Run `make format` and `make test`.
