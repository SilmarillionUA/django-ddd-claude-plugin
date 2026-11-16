---
name: architecture
description: The DDD layer rules for a Django project that uses this plugin. Says what lives in each layer, which way imports point, how a request flows and why. Use when deciding where code belongs, reviewing a change against the architecture, or explaining the structure.
---

# Architecture

This is the one full statement of the rules. The project `CLAUDE.md` holds a short copy. The other skills show how to build each piece.

## Why

Plain Django apps put models, views, forms and business rules side by side. As an app grows, rules end up in views, the same queryset is rebuilt in several places, and apps reach into each other's models. Testing one rule then needs the whole stack.

Each Django app here is one bounded context with three layers. A rule lives in one place and is tested at the layer that owns it.

The ORM is accepted as the persistence layer. Django models are the entities, and an app's own models are not hidden behind interfaces. Mapping them to separate entity classes would double the code for little gain.

The cost is more files per feature and some extra wiring, because Django looks for models, admin and commands in its default paths.

## Layers

```
infrastructure  ->  application  ->  domain
```

Imports point inward only. Infrastructure may import application and domain. Application may import domain. Domain imports neither.

| Layer | Holds | Must not |
|---|---|---|
| `domain/` | Models, QuerySets and repository managers, value objects, pure services, errors, interfaces, choices, business constants | Import the other layers or another app. Read the clock in a service. |
| `application/` | Use cases, one action per file, and the read models they return | Import infrastructure or another app. Build queries. Read the clock. Do HTTP, email or task queueing directly. |
| `infrastructure/` | Views, API views, serializers, forms, admin, tasks, commands, templates, gateways, the DI container | Hold business rules. Build queries. |

Helpers with no business meaning go in `corelib`, which every layer may import.

## How a request flows

1. A view, API view, task or command reads its input and the clock.
2. It asks the app's container in `infrastructure/di.py` for a use case. The container builds the gateways and services the use case needs.
3. It calls `execute()` with keyword arguments, including `today=`.
4. The use case asks `Model.repository` for data, runs domain services, calls interfaces, and writes.
5. It returns a model or a frozen dataclass. A refusal is raised as a domain error.
6. The caller turns the result into a response. A web view maps the error class to a translated message. An API view returns the error's `code`.

## Rules and their reasons

**Queries live on the model's QuerySet or repository manager** in `domain/managers.py`. No filter is written inline in a use case, view, task or command. A condition that several queries share is one `Q` builder. This way a rule such as "which copies can be lent" has one definition, and changing it changes every query.

**Each model has two managers:** `objects = models.Manager()` for Django and the admin, and `repository = <Model>Repository()` for business questions.

**A use case is a class with one public `execute()`** and keyword-only arguments. Dependencies come in through `__init__`, typed as domain interfaces or services. This makes it testable with stub classes and no patching.

**The clock is passed in.** Use cases and domain services take `today=` or a datetime. Only infrastructure calls `timezone.now()`. Tests then pick any date without freezing time.

**Anything that depends on today is computed in the use case** and returned in a read model, not worked out in a template or serializer.

**Domain services are pure:** no ORM, no clock, no network. Their settings are a frozen dataclass whose defaults come from `domain/settings.py`.

**Business numbers live in `domain/settings.py`** with a comment on why each has its value.

**A refusal is a domain error** that subclasses the app's base error and carries a stable `code`. Nothing parses exception text.

**The database holds every invariant it can.** The use case checks first, to give a clear error. A unique index, check constraint or conditional UPDATE settles the race the check cannot. The `IntegrityError` is turned into the domain error in a try block around that one write.

**An app never imports another app outside its gateways.** The app states what it needs as an ABC in `domain/interfaces.py`, in its own words. A gateway in `infrastructure/gateways.py` implements it. A foreign key by string name (`"other_app.Model"`) is fine. Splitting an app out later then touches one gateway and one container method.

**An outside API is split in two.** A client in `corelib/external/` owns HTTP and returns the API's own shapes. The gateway takes the client in `__init__` and maps those shapes to domain types.

**Views, tasks and commands never build gateways or use cases themselves.** They get them from the container.

**Each app has a `CLAUDE.md`** of at most 30 lines: what the context owns, invariants the code does not show, cross-app dependencies and gotchas.

## Tests

Tests sit in `<layer>/tests/` inside each app, next to the code that owns the rule.

- Domain: services and value objects with no database, repository methods against the test database.
- Application: the use case built by hand with stub subclasses of each interface and a fixed `today`.
- Infrastructure: views, API, tasks and gateways. Patch only at the outside edge.

## What is checked

The layer guard hook checks import direction and cross-app imports in `domain/` and `application/` after every edit. Everything else here is checked by reading, which is the `django-ddd:ddd-reviewer` subagent's job.

## Review checklist

1. **Layer placement.** ORM filters outside `domain/managers.py`. Business rules in views, serializers, forms, tasks or templates. HTTP, email, task queueing or `timezone.now()` inside `domain/` or `application/`.
2. **Use cases.** One public `execute()`, keyword-only arguments, dependencies through `__init__` typed as interfaces, the date passed in, a model or a frozen dataclass returned.
3. **Invariants.** Every rule the database can hold is a constraint. Checks that race have a constraint or a conditional UPDATE behind them, and the `IntegrityError` becomes a domain error in a narrow try block.
4. **Rules written once.** A condition repeated across queries instead of a shared `Q` builder or QuerySet method.
5. **Errors.** Refusals are domain errors with a stable `code`. The API returns the code. Views map the class to a message.
6. **Cross-app.** Another app's models imported outside `infrastructure/gateways.py`. Interfaces that speak ORM or HTTP types instead of domain types.
7. **Wiring.** New use cases are built in `infrastructure/di.py`, and callers get them from the container. New apps are in `LOCAL_APPS`, `MIGRATION_MODULES` and `TEMPLATES["DIRS"]`.
8. **Tests.** Each new rule has a test in the layer that owns it. Use case tests stub interfaces instead of patching.
9. **Docs.** An app's `CLAUDE.md` reflects any new invariant or cross-app dependency.

## Building each piece

| Need | Skill |
|---|---|
| A feature across layers | `django-ddd:ddd-feature` |
| A new bounded context | `django-ddd:new-app` |
| A table and its queries | `django-ddd:new-model` |
| A pure calculation | `django-ddd:new-service` |
| A user or scheduled action | `django-ddd:new-usecase` |
| Another app, an outside API, a side effect | `django-ddd:new-gateway` |
| A page | `django-ddd:new-view` |
| A partial page update | `django-ddd:fragment-endpoint` |
| Input validation | `django-ddd:new-form` |
| Background work | `django-ddd:new-task` |
| Staff tools | `django-ddd:new-admin` |
