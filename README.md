# django-ddd

A Claude Code plugin that teaches Claude to build Django projects as bounded contexts with domain, application and infrastructure layers, and stops it when an import breaks the layering.

It assumes Django and Django REST Framework. For everything else (test runner, formatter, task queue, frontend library) it uses what the project already has.

## The architecture

Each Django app is one bounded context with three layers. Imports point inward only.

```
infrastructure  ->  application  ->  domain
```

| Layer | Holds |
|---|---|
| `domain/` | Models, repository managers, value objects, pure services, errors, interfaces, business constants |
| `application/` | One use case class per action, with a single `execute()` |
| `infrastructure/` | Views, API, admin, forms, tasks, commands, templates, gateways, the DI container |

An app never imports another app outside its gateways. Queries are built on repository managers, not in views or use cases. The clock is passed into use cases as an argument. The ORM is accepted as the persistence layer, so Django models are the entities.

The full rules and the reasons for them are in [skills/architecture/SKILL.md](skills/architecture/SKILL.md).

## Install

```
/plugin marketplace add SilmarillionUA/django-ddd-claude-plugin
/plugin install django-ddd@django-ddd-claude-plugin
```

Then, inside your Django project:

```
/django-ddd:init
```

`init` reads the project and writes three things:

- `CLAUDE.md` with the rules and your project's own test, format and lint commands.
- `.claude/django-ddd.json`, which turns the hooks on for this project.
- Permission entries in `.claude/settings.json`.

It shows each change before writing. It installs nothing and moves no code.

## What you get

Skills:

| Skill | Use |
|---|---|
| `architecture` | The rules and their reasons |
| `ddd-feature` | Build a feature through all layers, in order |
| `new-app` | Scaffold a bounded context and wire it into settings |
| `new-model` | A model with its QuerySet and repository manager |
| `new-service` | A pure domain service |
| `new-usecase` | A use case with DI wiring and tests |
| `new-gateway` | A domain interface and its gateway |
| `new-view` | A class-based view that calls a use case |
| `fragment-endpoint` | An endpoint that returns a partial template |
| `new-form` | A form that checks input shape only |
| `new-task` | A background task that delegates to a use case |
| `new-admin` | A model admin |
| `init` | Set up a project |

Subagents: `ddd-reviewer` reviews a change against the rules. `test-writer` writes tests in the layer that owns the code.

Commands: `/django-ddd:check-architecture`, `/django-ddd:lint`, `/django-ddd:format`, `/django-ddd:review`.

Hooks, active only in a project that has `.claude/django-ddd.json`:

- After each edit, the layer guard checks the file's imports. A violation is sent back to Claude to fix.
- After each edit, the file is formatted with the commands you configured.
- Before each shell command, destructive ones are blocked (dropping a database, force-push, `git reset --hard`).

## What is enforced

Only import direction is enforced by a script: `domain/` and `application/` may not import outward or from another app. The other rules are instructions and review. Claude follows them from `CLAUDE.md` and the skills, and `ddd-reviewer` checks them by reading the code.

## Configuration

`.claude/django-ddd.json`:

```json
{
  "apps_root": "src/apps",
  "format_commands": {
    ".py": [[".venv/bin/python", "-m", "black", "--quiet", "{file}"]]
  }
}
```

- `apps_root`: the directory whose children are your apps, relative to the project root. It must be on `sys.path`, so apps import as `lending`, not `apps.lending`.
- `format_commands`: commands to run on an edited file, by file suffix. `{file}` stands for the file. Leave it empty for no formatting.

To run the layer check in CI, copy `hooks/ddd_layer_guard.py` into your repository and run it from the project root with `--all`.

## Requirements

- Claude Code with plugin support.
- `python3` on `PATH`, for the hooks.
- `git`, for the reviewer.
