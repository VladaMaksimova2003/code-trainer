interface PaginationProps {
  page: number
  pageCount: number
  onChange: (page: number) => void
}

export default function Pagination({ page, pageCount, onChange }: PaginationProps) {
  const pages: number[] = []
  const max = Math.min(pageCount, 5)
  for (let i = 1; i <= max; i += 1) pages.push(i)

  return (
    <div className="pagination">
      <button type="button" onClick={() => onChange(Math.max(1, page - 1))} disabled={page === 1}>
        ‹
      </button>
      {pages.map((p) => (
        <button
          key={p}
          type="button"
          className={p === page ? "on" : ""}
          onClick={() => onChange(p)}
        >
          {p}
        </button>
      ))}
      {pageCount > 5 ? <span className="mut3" style={{ padding: "0 8px" }}>…</span> : null}
      <button
        type="button"
        onClick={() => onChange(Math.min(pageCount, page + 1))}
        disabled={page === pageCount}
      >
        ›
      </button>
    </div>
  )
}
