export default function FilterInput({ value, onChange }) {
  return (
    <input id="filter" type="text" placeholder="filter"
           value={value} onChange={onChange} />
  );
}
