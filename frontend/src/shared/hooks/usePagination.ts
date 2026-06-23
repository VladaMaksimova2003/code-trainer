import { useMemo, useState } from "react"

export function usePagination<T>(items: T[] | null | undefined, pageSize = 15) {
  const [page, setPage] = useState(1)

  const totalPages = Math.max(1, Math.ceil((items?.length || 0) / pageSize))

  const safePage = Math.min(page, totalPages)

  const slice = useMemo(() => {
    const start = (safePage - 1) * pageSize
    return (items || []).slice(start, start + pageSize)
  }, [items, safePage, pageSize])

  const resetPage = () => setPage(1)

  return {
    page: safePage,
    setPage,
    totalPages,
    pageItems: slice,
    resetPage,
    pageSize,
  }
}
