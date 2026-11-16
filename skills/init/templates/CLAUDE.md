## Project Structure

The full rules and their reasons are in the `django-ddd:architecture` skill. Load it before deciding where new code belongs. The short version:

- Apps live in `{apps_root}/`. Each app is one bounded context with three layers: `domain/`, `application/`, `infrastructure/`.
- Imports point inward only: infrastructure imports application and domain, application imports domain, domain imports neither.
- A domain or application module never imports another app. Cross-app needs go through an ABC in `domain/interfaces.py` and a gateway in `infrastructure/gateways.py`.
- `domain/` holds models, repository managers, value objects, pure services, errors, interfaces and business constants.
- `application/use_cases/` holds one use case class per action, with one public `execute()` and keyword-only arguments.
- `infrastructure/` holds views, API views, serializers, forms, admin, tasks, commands, templates, gateways and the DI container.
- Queries are built on the QuerySet or repository manager in `domain/managers.py`. Never inline a filter in a use case, view, task or command.
- The current date or time comes into a use case as an argument (`today=`), never read inside.
- A refusal is a domain error with a stable `code`. The database enforces each invariant too, and the `IntegrityError` becomes the domain error in a narrow try block.
- Views, tasks and commands get use cases from the container in `infrastructure/di.py` and never build gateways themselves.
- API output goes through DRF `serializers.Serializer` subclasses with `to_representation()`. Request-scoped state arrives via serializer `context`.
- Shared helpers with no business meaning go in `corelib`.

## Wiring an app

- `{apps_root}` is on `sys.path`, so apps import as `<app>`, not `apps.<app>`.
- A new app is added to `LOCAL_APPS`, `MIGRATION_MODULES` and `TEMPLATES["DIRS"]` in `{base_settings_path}`. The `django-ddd:new-app` skill has the rest.

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
