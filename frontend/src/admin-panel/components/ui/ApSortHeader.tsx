export type SortDir = "asc" | "desc"

type ApSortHeaderProps<K extends string> = {
  label: string
  column: K
  sortKey: K
  sortDir: SortDir
  onSort: (column: K) => void
}

export function ApSortHeader<K extends string>({
  label,
  column,
  sortKey,
  sortDir,
  onSort,
}: ApSortHeaderProps<K>) {
  const active = sortKey === column
  return (
    <button
      type="button"
      className={`ap-table-sort-btn${active ? " is-active" : ""}`}
      onClick={() => onSort(column)}
      aria-sort={active ? (sortDir === "asc" ? "ascending" : "descending") : "none"}
    >
      {label}
      <span className="ap-table-sort-icon" aria-hidden="true">
        {active ? (sortDir === "asc" ? "▲" : "▼") : "↕"}
      </span>
    </button>
  )
}
