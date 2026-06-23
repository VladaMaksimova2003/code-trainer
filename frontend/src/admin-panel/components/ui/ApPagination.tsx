export default function ApPagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null

  const pages = []
  const start = Math.max(1, page - 2)
  const end = Math.min(totalPages, page + 2)
  for (let i = start; i <= end; i += 1) pages.push(i)

  return (
    <div className="ap-pagination">
      <button type="button" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
        ←
      </button>
      {pages.map((p) => (
        <button
          key={p}
          type="button"
          className={p === page ? "on" : ""}
          onClick={() => onPageChange(p)}
        >
          {p}
        </button>
      ))}
      <button type="button" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
        →
      </button>
    </div>
  )
}
