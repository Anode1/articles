import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./app.css";
function ItemRow({ item, checked, onToggle, onRemove }) {
  return (
    <div className="item-row" data-id={item.id}>
      <input type="checkbox" className="select" checked={checked}
             onChange={() => onToggle(item.id)} />
      <span>{item.id}</span>
      <span className="item-author">{item.author}</span>
      <span className="item-name">{item.name}</span>
      <span className={`badge badge-${item.state}`}>{item.state}</span>
      <button className="delete" onClick={() => onRemove(item.id)}>Delete</button>
    </div>
  );
}

function caret(sort, key) {
  if (sort.key !== key) return "";
  return sort.dir > 0 ? " ▲" : " ▼";
}

function ItemsTable({ rows, selected, sort, onSort, onToggle, onRemove }) {
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

function App() {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState({});
  const [filterText, setFilterText] = useState("");
  const [minLen, setMinLen] = useState(0);
  const [sort, setSort] = useState({ key: "id", dir: 1 });

  useEffect(() => {
    fetch("items.json")
      .then((r) => r.json())
      .then(setItems);
  }, []);

  const rows = useMemo(() => {
    const q = filterText.toLowerCase();
    return items
      .filter((it) => {
        if (q && !it.name.toLowerCase().includes(q)
               && !it.author.toLowerCase().includes(q)) return false;
        return it.name.length >= minLen;
      })
      .sort((a, b) => {
        const x = a[sort.key], y = b[sort.key];
        return (x < y ? -1 : x > y ? 1 : 0) * sort.dir;
      });
  }, [items, filterText, minLen, sort]);

  const selectedCount = rows.filter((it) => selected[it.id]).length;

  function toggle(id) {
    setSelected((prev) => {
      const next = { ...prev };
      if (next[id]) delete next[id]; else next[id] = true;
      return next;
    });
  }

  function remove(id) {
    setItems((prev) => prev.filter((it) => String(it.id) !== String(id)));
    setSelected((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  }

  function sortBy(key) {
    setSort((prev) =>
      prev.key === key ? { key, dir: -prev.dir } : { key, dir: 1 });
  }

  return (
    <>
      <h1>Items</h1>
      <div className="controls">
        <input id="filter" type="text" placeholder="filter"
               value={filterText} onChange={(e) => setFilterText(e.target.value)} />
        <input id="minLen" type="number" min="0" placeholder="min length"
               value={minLen || ""}
               onChange={(e) => setMinLen(parseInt(e.target.value, 10) || 0)} />
      </div>
      <div id="count">{rows.length} {rows.length === 1 ? "item" : "items"}</div>
      <div id="selected">{selectedCount ? `${selectedCount} selected` : ""}</div>
      <ItemsTable rows={rows} selected={selected} sort={sort}
                  onSort={sortBy} onToggle={toggle} onRemove={remove} />
    </>
  );
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);