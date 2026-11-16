---
name: new-admin
description: Register a model in the Django admin with N+1 protection and read-only fields for use-case-owned data.
---

# Create a model admin

Register the model the user names in the app's `infrastructure/admin.py`.

```python
from django.contrib import admin

from {app}.domain.models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["copy", "member", "due_on", "returned_on"]
    list_filter = ["returned_on"]
    list_select_related = ["copy__book", "member__user"]
    search_fields = ["copy__barcode", "member__user__username"]
    raw_id_fields = ["member", "copy"]
    readonly_fields = ["late_fee_cents", "created_at", "updated_at"]
```

## Rules

- If the project's admins use base classes from an admin theme, import `ModelAdmin` and inlines from there, as the existing admins do.
- `list_select_related` or `get_queryset()` with `select_related` to avoid N+1.
- `raw_id_fields` for relations to big tables.
- Fields that only use cases may set (fees, counters) are read-only, with a comment saying why.
- The AppConfig imports this module in `ready()`.

## After creating

- Add a changelist smoke test with a logged-in staff client.
- Run the project's format command (see `CLAUDE.md`).
