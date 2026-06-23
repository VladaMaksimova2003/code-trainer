import { useCallback, useEffect, useState } from "react"
import { getErrorMessage } from "@/shared/utils/errors"

export function useAsyncResource(loadFn, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const reload = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await loadFn()
      setData(result)
      return result
    } catch (err) {
      setError(getErrorMessage(err))
      throw err
    } finally {
      setLoading(false)
    }
  }, deps)

  useEffect(() => {
    reload().catch(() => {})
  }, [reload])

  return { data, loading, error, reload, setData }
}
