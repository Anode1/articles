import ItemRow from "./ItemRow.jsx";

function caret(sort, key) {
  if (sort.key !== key) return "";
  return sort.dir > 0 ? " ▲" : " ▼";
}

export default function ItemsTable({ rows, selected, sort, onSort, onToggle, onRemove }) {
  return (
    <>
      <div className="header">
        <span></span>
        <span data-sort="id" onClick={() => onSort("id")}>ID{caret(sort, "id")}</span>
        <span>Author</span>
        <span data-sort="name" onClick={() => onSort("name")}>Name{caret(sort, "name")}</span>
        <span>State</span>
        <span></span>
      </div>
      <div id="rows">
        {rows.length === 0
          ? <div className="empty">No items found.</div>
          : rows.map((it) => (
              <ItemRow key={it.id} item={it} checked={!!selected[it.id]}
                       onToggle={onToggle} onRemove={onRemove} />
            ))}
      </div>
    </>
  );
}
