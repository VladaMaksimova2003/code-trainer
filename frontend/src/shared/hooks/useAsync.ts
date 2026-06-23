import { useCallback, useEffect, useState } from "react"

interface UseAsyncOptions {
  immediate?: boolean
}

export function useAsync<T>(
  asyncFn: (...args: unknown[]) => Promise<T>,
  deps: unknown[] = [],
  { immediate = true }: UseAsyncOptions = {},
) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<unknown>(null)
  const [loading, setLoading] = useState(Boolean(immediate))

  const execute = useCallback(async (...args: unknown[]) => {
    setLoading(true)
    setError(null)
    try {
      const result = await asyncFn(...args)
      setData(result)
      return result
    } catch (err) {
      setError(err)
      throw err
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    if (immediate) {
      execute()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [execute, immediate])

  return { data, error, loading, execute, setData }
}
