---
name: fragment-endpoint
description: Add an endpoint that returns a partial template for in-page updates. Use for search-as-you-type, inline actions and partial page refreshes, with whatever frontend library the project uses.
---

# Create a fragment endpoint

Add a partial-update interaction to the page or feature the user names. Use the frontend library the project already has (HTMX, Turbo, Unpoly or plain `fetch`) and copy the markup of an existing template.

## Rules

- One helper decides whether a request wants a fragment. Look for it in `corelib/http.py`. Add it when missing, with the header the project's library sends:

  ```python
  FRAGMENT_REQUEST_HEADER = "HX-Request"
  FRAGMENT_REQUEST_VALUE = "true"


  def is_fragment_request(request: HttpRequest) -> bool:
      return request.headers.get(FRAGMENT_REQUEST_HEADER) == FRAGMENT_REQUEST_VALUE
  ```

- A POST action answers a fragment request with the fresh fragment and a plain form post with a redirect:

  ```python
  def post(self, request, **kwargs):
      try:
          success_message = self.perform(**kwargs)
      except LendingError as exc:
          messages.error(request, LENDING_ERROR_MESSAGES[type(exc)])
      else:
          messages.success(request, success_message)

      if not is_fragment_request(request):
          return redirect("lending:my_loans")

      return render(
          request,
          LOAN_TABLE_TEMPLATE,
          {"my_loans": my_loans_report(request=request), "show_messages": True},
      )
  ```

- A fragment returned after an action renders its own messages. The full page already shows them in the layout, so pass a flag (`show_messages`) only from the action response.
- Fragment POSTs must send the CSRF token. Set it once in the base template, the way the project's library expects.
- Fragments live in `templates/{app}/partials/_name.html` and never extend a layout.
- A page and its fragment share one mixin that builds the context.
- Classes used only as JavaScript hooks get a `js-` prefix and are never styled.

## After creating

- Test both paths: with the fragment header and as a plain request.
- Run the project's format command (see `CLAUDE.md`).
