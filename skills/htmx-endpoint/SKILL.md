---
name: htmx-endpoint
description: Add an HTMX fragment endpoint or POST action that returns a partial template. Use for search-as-you-type, inline actions and partial page updates.
---

# Create an HTMX endpoint

Add an HTMX interaction to the page or feature the user names.

## Rules

- Detect HTMX with `corelib.http.is_htmx(request)`. Add the helper when the project lacks it:

  ```python
  HTMX_REQUEST_HEADER = "HX-Request"
  HTMX_REQUEST_VALUE = "true"


  def is_htmx(request: HttpRequest) -> bool:
      return request.headers.get(HTMX_REQUEST_HEADER) == HTMX_REQUEST_VALUE
  ```

- A POST action answers HTMX with the fresh fragment and a plain form post with a redirect:

  ```python
  def post(self, request, **kwargs):
      try:
          success_message = self.perform(**kwargs)
      except LendingError as exc:
          messages.error(request, LENDING_ERROR_MESSAGES[type(exc)])
      else:
          messages.success(request, success_message)

      if not is_htmx(request):
          return redirect("lending:my_loans")

      return render(
          request,
          LOAN_TABLE_TEMPLATE,
          {"my_loans": my_loans_report(request=request), "show_messages": True},
      )
  ```
- A fragment returned after an action renders its own messages. The full page already shows them in the layout, so pass a flag (`show_messages`) only from the action response.
- CSRF comes from `hx-headers` on `<body>` in the base template: `<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>`. Add it when missing.
- Fragments live in `templates/{app}/partials/_name.html` and never extend a layout.

## Trigger

```html
<button class="btn btn-sm btn-outline-primary"
        hx-post="{% url 'lending:return_loan' loan_id=row.loan_id %}"
        hx-target="#loan-table">
  <i class="fas fa-fw fa-rotate-left"></i> {% translate "Return" %}
</button>
```

- `hx-trigger="input changed delay:300ms"` for search boxes.
- `fa-fw` on every Font Awesome icon.
- `js-` prefixed classes for JavaScript hooks, never styled.

## After creating

- Test with `HTTP_HX_REQUEST="true"` in the test client.
- `make format`
