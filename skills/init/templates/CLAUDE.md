## Project Structure

- Apps live in `{apps_root}/`. Each app is one bounded context with three layers: `domain/`, `application/`, `infrastructure/`.
- Imports point inward only: infrastructure imports application and domain, application imports domain, domain imports neither.
- A domain or application module never imports another app. Cross-app needs go through an ABC in `domain/interfaces.py` and a gateway in `infrastructure/gateways.py`. A foreign key by string name (`"other_app.Model"`) is fine.
- Models, managers, interfaces, choices, exceptions, value objects and business constants live in `domain/`.
- ORM query building belongs on the model's QuerySet or repository manager in `domain/managers.py`. Never inline a filter in a use case, view, task or command. Compose the existing helpers instead of repeating a condition.
- Each model has `objects = models.Manager()` and `repository = <Model>Repository()`.
- A rule that several queries need is written once, as a `Q` builder on the repository.
- Use cases live in `application/use_cases/`, one action per file. Use cases and domain services are classes with one public `execute()` and small private helpers.
- Use cases take keyword-only arguments. Dependencies come in through `__init__`. The current date or time comes in as an argument (`today=`), never read inside.
- Use cases return a model or a frozen dataclass read model. Anything that depends on today is computed there, not in templates or serializers.
- Domain errors subclass the app's base error and carry a stable `code`. The API returns the code; web views map the class to a translated message.
- Checks run before writes, and the database enforces the invariant too (unique index, check constraint, conditional UPDATE). Turn the resulting `IntegrityError` into the domain error, in a narrow try block.
- Domain services in `domain/services/` are pure: no ORM, no clock. Configuration is a frozen dataclass.
- Business numbers live in `domain/settings.py` with a comment on why.
- Views, admin, forms, serializers, API views, tasks, commands, templates, gateways and the DI container live in `infrastructure/`.
- Each app has a DI container in `infrastructure/di.py` (`<App>Container`) with `@staticmethod` factories. Views, tasks and commands get use cases from it and never build gateways themselves.
- API output goes through DRF `serializers.Serializer` subclasses with `to_representation()`. Request-scoped state arrives via serializer `context`.
- Shared helpers with no business meaning go in `corelib`.
- An outside API is split in two. The client in `corelib/external/` owns HTTP (session, timeout, retries) and returns the API's shapes. The gateway in `infrastructure/gateways.py` takes the client in `__init__` and maps those shapes to domain types. Gateways never make HTTP calls themselves.

## Wiring an app

- `{apps_root}` is on `sys.path`, so apps import as `<app>`, not `apps.<app>`.
- `<app>/__init__.py` aliases `sys.modules["<app>.apps"]` to `infrastructure/apps.py`.
- The AppConfig overrides `import_models()` to load `domain/models.py` and set `models_module`, and imports `infrastructure.admin` in `ready()`.
- Add the app to `LOCAL_APPS`, `MIGRATION_MODULES` and `TEMPLATES["DIRS"]` in `{base_settings_path}`.
- Management commands are registered by name in `ready()`.

## Commands

- Test: `{test_command}`
- Format: `{format_command}`
- Lint: `{lint_command}`
- Layer check: `/django-ddd:check-architecture`

## Testing

- Tests go in `<layer>/tests/` inside each app.
- Test data comes from the project's factories or fixtures. Add one next to the others when it is missing.
- Use case tests pass stub classes that subclass the domain interface. Patch only at the infrastructure edge (HTTP calls, task queueing).

## Instructions

- Absolute imports from the app name (`from <app>.domain.models import <Model>`), never relative.
- Top-level imports only, except `TYPE_CHECKING` blocks and `import_module` in `AppConfig`.
- No magic numbers or strings. Name them at module level.
- Narrow try/except blocks, one failure mode each. Never hide errors.
- Prefer `filter().first()` over try/except `DoesNotExist`, and `dict.get()` over square brackets unless a missing key should raise.
- Named arguments for calls with two or more arguments that could be swapped.
- Comments explain why, never what. Docstrings on classes and functions whose contract is not obvious.
- No inline CSS. `js-` prefix for classes used by JavaScript, never targeted by CSS.
- User-facing text lives in templates with `{% translate %}`, or in `gettext` for messages.
- `select_related` and `prefetch_related` wherever a list touches a relation.

## Per-app CLAUDE.md

Each app has a `CLAUDE.md` of at most 30 lines: what the context owns, invariants the code does not show, cross-app dependencies, gotchas. Do not list files or restate this file. Update it when the rules change.

## Claude Code setup

- The `django-ddd` plugin provides the skills, subagents and hooks below. `.claude/django-ddd.json` turns its hooks on for this project.
- Hooks run on every edit: the file is formatted when format commands are set, then the layer guard rejects imports that point outward. Fix the import it reports; do not work around the guard.
- Destructive shell commands are blocked. Ask the user instead of retrying.
- For a feature that spans layers, follow the `django-ddd:ddd-feature` skill. Single pieces have their own skills (`django-ddd:new-usecase`, `django-ddd:new-gateway`, and so on).
- Before handing work back, run the lint and test commands above and the layer check, then ask the `django-ddd:ddd-reviewer` subagent for a review.
