---
name: init
description: Set up a Django project for the django-ddd plugin. Writes the project CLAUDE.md, the hook config, permissions and the make targets the other skills call. Run once per project, or again after the layout changes.
disable-model-invocation: true
---

# Set up a project for django-ddd

The plugin ships skills, subagents and hooks. It cannot ship the project rules, permissions or make targets, so this skill writes them. Templates are in `templates/` next to this file.

Never overwrite a file without showing the user the change first. Do not stage or commit anything.

## 1. Read the project

Find these and show them to the user in one list before writing anything:

- `manage.py` and the source root that holds it (`{source_root}`).
- The apps root (`{apps_root}`): the directory whose children are Django apps. Default `src/apps`.
- The base settings module (`{base_settings_path}`), the Celery module (`{celery_module_path}`) and the root URLconf.
- The Django version, as `major.minor` (`{django_target_version}`).
- Which of these the project uses: DRF, Celery, HTMX, Unfold, structlog, Bootstrap, pytest-django, isort, black, flake8, djade.
- Existing `CLAUDE.md`, `.claude/settings.json`, `Makefile`.

Ask the user when the apps root is not clear or there are several candidates.

Check that the apps root is on `sys.path`, so apps import as `<app>`. The layer guard matches imports by their first name, so with `apps.<app>` imports it finds nothing. If it is not on the path, tell the user and ask whether to add `sys.path.insert` to the base settings.

## 2. Hook config

Write `.claude/django-ddd.json` from `templates/django-ddd.json` with the real `apps_root` (relative to the project root) and `django_target_version`.

The plugin's hooks do nothing in a project without this file. With it, each edit is formatted and checked by the layer guard, and destructive shell commands are blocked.

## 3. CLAUDE.md

Fill the placeholders in `templates/CLAUDE.md` and write it as the project `CLAUDE.md`.

- Drop each line about a tool the project does not use. Do not add rules the template does not have.
- If a `CLAUDE.md` exists, merge: keep the user's content, add the sections that are missing, and show a diff of anything that conflicts.

## 4. Permissions

Merge `templates/permissions.json` into `.claude/settings.json`. Keep every entry already there. Add `manage.py` entries with the real path:

- allow: `check`, `makemigrations`, `showmigrations`.
- ask: `migrate`.
- deny: `Read` on local and production settings files that hold secrets.

## 5. Layer check for make and CI

Copy the plugin's `hooks/ddd_layer_guard.py` to `scripts/ddd_layer_guard.py`. It is at `${CLAUDE_SKILL_DIR}/../../hooks/ddd_layer_guard.py`. Copy it unchanged, so a later plugin update can replace it.

Run `python scripts/ddd_layer_guard.py --all` from the project root and report what it finds.

## 6. Make targets

The other skills call `make test`, `make format`, `make lint` and `make architecture`. Add the missing ones from `templates/Makefile.mk`, with the placeholders filled. Leave existing targets alone, and tell the user when one has the same name but does something else. Skip lines for formatters the project does not have.

## 7. Existing apps

List each app under the apps root and say whether it has the three layers.

- For an app with layers and no `CLAUDE.md`, offer to write one (at most 30 lines: what it owns, invariants, cross-app dependencies, gotchas).
- For an app without layers, do not move code. Say that it is outside the rules until it is restructured, and that the `django-ddd:new-app` skill shows the target shape.

## 8. Report

List the files written or changed and the layer violations found. Suggest adding the plugin to the project `.claude/settings.json` under `enabledPlugins`, so teammates get it too.
