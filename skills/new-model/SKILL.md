---
name: new-model
description: Add a Django model with its QuerySet and repository manager in the domain layer. Use when a feature needs a new table or entity.
---

# Create a new model with a repository manager

Create a model with the name the user gives.

## Model (`domain/models.py`)

- `gettext_lazy as _` for verbose names.
- `created_at` (`auto_now_add`) and `updated_at` (`auto_now`).
- `objects = models.Manager()` and `repository = {Model}Repository()`.
- `related_name` on every relation. A relation to another app uses the string name (`"catalog.Copy"`).
- `Meta` with `ordering`, `verbose_name`, `verbose_name_plural`, and `constraints` for every invariant the database can hold (unique, partial unique, check). Prefix constraint names with the app label.
- `__str__` and `get_admin_url()`.
- A docstring that says what one row means and any rule about its lifetime (closed, withdrawn, never deleted).
- Lengths and limits come from `domain/settings.py`.

## Repository (`domain/managers.py`)

The repository is a Django manager. There is no separate repository class or folder.

```python
if TYPE_CHECKING:
    from {app}.domain.models import {Model}


class {Model}QuerySet(models.QuerySet["{Model}"]):
    def still_open(self) -> "{Model}QuerySet":
        return self.filter(...)


class {Model}Repository(models.Manager["{Model}"]):
    def get_queryset(self) -> {Model}QuerySet:
        return {Model}QuerySet(self.model, using=self._db)

    def open_count_for_member(self, *, member_id: int) -> int:
        return self.get_queryset().still_open().filter(member_id=member_id).count()

    def close_if_open(self, *, loan_id: int, returned_on: date) -> bool:
        closed_rows = (
            self.get_queryset()
            .still_open()
            .filter(id=loan_id)
            .update(returned_on=returned_on)
        )

        return bool(closed_rows)
```

- Type both classes with the model name as a string. The model import stays under `TYPE_CHECKING`, because `models.py` imports this file.
- Chainable filters on the QuerySet, named in domain words.
- Business questions on the Repository, keyword-only, returning a bool, a count, one object or `None`, or `.values()` rows with plain keys.
- Writes that touch many rows or depend on a condition go on the Repository too: a bulk upsert, a conditional UPDATE, a delete of rows no longer present. Name them for what they do (`bulk_upsert`, `close_if_open`, `prune_missing`) and return what the use case needs to know, such as the number of rows changed. Dates and times come in as arguments.
- Creating or saving one object stays in the use case.
- A condition that several queries share is a `Q` builder written once. A `prefix` lets another model's query reuse it through a relation:

  ```python
  @staticmethod
  def lendable_condition(*, prefix: str = "") -> Q:
      return Q(**{f"{prefix}is_withdrawn": False}) & ~Q(
          **{f"{prefix}condition": CopyCondition.DAMAGED}
      )
  ```

  Used as `self.filter(CopyRepository.lendable_condition())` and as `Count("copies", filter=CopyRepository.lendable_condition(prefix="copies__"))`.

### When the file grows

When `managers.py` is too long to scan, turn it into a package:

```
domain/managers/
├── __init__.py      re-exports every QuerySet and Repository
├── loan.py
└── member.py
```

One module per model. `__init__.py` re-exports each class, so `from {app}.domain.managers import {Model}Repository` keeps working and no caller changes. Do not split by reads and writes.

## Admin

Register it in `infrastructure/admin.py` (see the `django-ddd:new-admin` skill).

## After creating

- `python manage.py makemigrations`
- Run the project's format command (see `CLAUDE.md`).
