---
name: init
description: Set up a Django project for the django-ddd plugin. Writes the project CLAUDE.md, the hook config and permissions, using the commands and tools the project already has. Run once per project, or again after the layout changes.
disable-model-invocation: true
---

# Set up a project for django-ddd

The plugin ships skills, subagents and hooks. It assumes Django and DRF and nothing else. The other skills say "the project's test command" or "the project's task runner" and look the answer up in the project `CLAUDE.md`. This skill finds those answers and writes them down.

Never overwrite a file without showing the user the change first. Do not install anything. Do not stage or commit anything.

## 1. Read the project

Find these and show them to the user in one list before writing anything:

- `manage.py` and the directory that holds it.
- The apps root (`{apps_root}`): the directory whose children are Django apps.
- The base settings module (`{base_settings_path}`) and the root URLconf.
- The commands the project uses to test, format and lint (`{test_command}`, `{format_command}`, `{lint_command}`). Look in the Makefile, justfile, `pyproject.toml`, tox or nox config, CI config and README.
- The formatters that can format one file, and the executable that runs them.
- The task runner, the frontend library for partial page updates, and the logging library, if any.
- Existing `CLAUDE.md` and `.claude/settings.json`.

Ask the user when the apps root is not clear or there are several candidates. When the project has no command for something, write "none" and move on. Do not invent one.

Check that the apps root is on `sys.path`, so apps import as `<app>`. The layer guard matches imports by their first name, so with `apps.<app>` imports it finds nothing. If it is not on the path, tell the user and ask whether to add `sys.path.insert` to the base settings.

## 2. Hook config

Write `.claude/django-ddd.json` from `templates/django-ddd.json` next to this file.

- `apps_root`: the real apps root, relative to the project root.
- `format_commands`: for each file suffix, the commands that format one file. Each command is a list of arguments with `{file}` for the edited file. The hook runs them from the project root with no virtualenv active, so name the executable by its path. Leave it empty when the project has no formatter.

```json
{
  "apps_root": "src/apps",
  "format_commands": {
    ".py": [[".venv/bin/python", "-m", "black", "--quiet", "{file}"]]
  }
}
```

The plugin's hooks do nothing in a project without this file. With it, each edit is formatted and checked by the layer guard, and destructive shell commands are blocked.

## 3. CLAUDE.md

Fill the placeholders in `templates/CLAUDE.md` and write it as the project `CLAUDE.md`.

- Drop each line whose placeholder has no answer.
- Add one line for each tool found in step 1 that the skills need to know: the task runner and where tasks are registered, the fragment library and its request header, the logging library.
- Do not add other rules.
- If a `CLAUDE.md` exists, merge: keep the user's content, add the sections that are missing, and show a diff of anything that conflicts.

## 4. Permissions

Merge `templates/permissions.json` into `.claude/settings.json`. Keep every entry already there. Then add:

- allow: the project's test, format and lint commands, and `manage.py` with `check`, `makemigrations`, `showmigrations`.
- ask: `manage.py migrate`.
- deny: `Read` on settings files that hold secrets.

## 5. Layer check

Run the check from the project root and report what it finds:

`python3 "${CLAUDE_PLUGIN_ROOT}/hooks/ddd_layer_guard.py" --all`

Ask whether the user wants it in CI. If yes, copy `${CLAUDE_PLUGIN_ROOT}/hooks/ddd_layer_guard.py` unchanged to a path they pick, and show the command to run it. Do not edit their CI config.

## 6. Existing apps

List each app under the apps root and say whether it has the three layers.

- For an app with layers and no `CLAUDE.md`, offer to write one (at most 30 lines: what it owns, invariants, cross-app dependencies, gotchas).
- For an app without layers, do not move code. Say that it is outside the rules until it is restructured, and that the `django-ddd:new-app` skill shows the target shape.

## 7. Report

List the files written or changed, what was left as "none", and the layer violations found. Suggest adding the plugin to the project `.claude/settings.json` under `enabledPlugins`, so teammates get it too.
