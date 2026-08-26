export default function ItemRow({ item, checked, onToggle, onRemove }) {
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
