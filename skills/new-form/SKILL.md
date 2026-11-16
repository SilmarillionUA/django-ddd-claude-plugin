---
name: new-form
description: Add a Django form that checks input shape only and leaves domain rules to the use case.
---

# Create a form

Create a form with the name the user gives in the app's `infrastructure/forms.py`.

## Rules

- A form checks the shape of input only: required, length, type, range.
- Domain rules (valid ISBN, already taken, limits) are decided by the use case. The view catches the domain error and calls `form.add_error()`:

  ```python
  # One dict maps each domain error class to (field_name, message).
  try:
      book_obj = CatalogContainer.get_add_book_use_case().execute(
          raw_isbn=cleaned_data.get("isbn"),
          title=cleaned_data.get("title"),
      )
  except tuple(ADD_BOOK_ERRORS) as exc:
      field_name, message = ADD_BOOK_ERRORS[type(exc)]
      form.add_error(field_name, message)
      return self.form_invalid(form)
  ```
- Prefer `forms.Form` feeding a use case over a `ModelForm` that saves directly.
- Bootstrap widget classes: `form-control`, `form-select`, `form-check-input`.
- `gettext_lazy` labels. Limits from `domain/settings.py`.

## After creating

- `make format`
