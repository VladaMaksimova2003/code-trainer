import { useQuery } from "@tanstack/react-query"
import { useEffect, useMemo } from "react"
import { getServerLanguages } from "@/shared/api"
import {
  setLanguagesCache,
  getLanguagesCache,
  getDefaultLanguageId,
  getExecutableLanguageIds,
  getTaskAuthoringLanguageIds,
  getLanguageLabel,
  getMonacoLanguage,
  getAllLanguageIds,
} from "@/shared/config/languages"
import type { LanguageItem } from "@/shared/types/language"

export function useLanguages() {
  const query = useQuery({
    queryKey: ["languages"],
    queryFn: getServerLanguages,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })

  useEffect(() => {
    if (query.data) {
      setLanguagesCache(query.data)
    }
  }, [query.data])

  const languages = (
    Array.isArray(query.data) ? query.data : getLanguagesCache()
  ) as LanguageItem[]

  return useMemo(
    () => ({
      languages,
      isLoading: query.isLoading,
      isError: query.isError,
      error: query.error,
      executableIds: getExecutableLanguageIds(),
      authoringIds: getTaskAuthoringLanguageIds(),
      allIds: getAllLanguageIds(),
      defaultId: getDefaultLanguageId(),
      getLabel: getLanguageLabel,
      getMonacoLanguage,
    }),
    [languages, query.isLoading, query.isError, query.error],
  )
}
