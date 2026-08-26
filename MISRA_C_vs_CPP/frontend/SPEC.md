# The behavior both sides implement

One screen, modelled on the shape System A uses for every list page: fetch rows,
render a table, filter it, select rows, act on one.

1. On load, GET `items.json` and render every row.
2. Text filter matches name or author, case-insensitive, as you type.
3. Minimum-length filter, a number input, keeps rows whose name is at least
   that long. It combines with the text filter.
4. Count line reads `N items`, and `1 item` in the singular.
5. When nothing matches, the table body shows `No items found.` and the count
   reads `0 items`.
6. Each row: a select checkbox, the id, the author, the name, and a state
   badge whose class is `badge badge-<state>`.
7. A second line reads `N selected`, and is absent when none are.
8. Clicking the `name` or `id` header sorts by that column and toggles
   direction; the active header carries ` ▲` or ` ▼`.
9. Each row has a Delete button that removes that row from the list.
10. Deleting or filtering never loses a selection of a row that is still
    present.

The DOM the checks read: `#count`, `#selected`, `#rows`, `.item-row` with
`data-id`, `.badge`, `.item-name`, `.item-author`, and the header carets.
Both sides render the same structure and the same class names, so one set of
checks grades both.
