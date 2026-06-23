import { useEffect, useMemo, useRef, useState } from "react"
import { api } from "@/shared/api/client"
import { isConceptUsedForLanguage } from "@/features/task-solving/model/conceptUsage"

export type ScannedConceptItem = {
  id: string
  label: string
  detected: boolean
  reason?: string | null
}

export type ScannableConcept = {
  id: string
  technical_concept_ids?: string[]
}

export type ConceptScanResult = {
  usedMap: Record<string, boolean>
  reasons: Record<string, string>
  loading: boolean
}

type ScanResponse = {
  items: ScannedConceptItem[]
  detected_ids: string[]
}

export async function scanExpectedConcepts(params: {
  code: string
  language: string
  conceptIds: string[]
  signal?: AbortSignal
}): Promise<ScanResponse> {
  const res = await api.post<ScanResponse>(
    "/tasks/scan-expected-concepts",
    {
      code: params.code,
      language: params.language,
      concept_ids: params.conceptIds,
    },
    { signal: params.signal },
  )
  return res.data
}

function buildLocalScan(
  code: string,
  language: string,
  concepts: ScannableConcept[],
): Pick<ConceptScanResult, "usedMap" | "reasons"> {
  const usedMap: Record<string, boolean> = {}
  const reasons: Record<string, string> = {}
  for (const concept of concepts) {
    const conceptId = String(concept.id || "").trim()
    if (!conceptId) continue
    const detected = isConceptUsedForLanguage(
      conceptId,
      code,
      language,
      concept.technical_concept_ids,
    )
    usedMap[conceptId] = detected
    if (!detected) {
      reasons[conceptId] = "В коде не найдена конструкция (локальная проверка)"
    }
  }
  return { usedMap, reasons }
}

export function useExpectedConceptScan(
  code: string,
  language: string,
  concepts: ScannableConcept[],
  debounceMs = 350,
): ConceptScanResult {
  const [usedMap, setUsedMap] = useState<Record<string, boolean>>({})
  const [reasons, setReasons] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const requestIdRef = useRef(0)
  const conceptIds = useMemo(
    () => concepts.map((concept) => String(concept.id || "").trim()).filter(Boolean),
    [concepts],
  )
  const conceptKey = useMemo(() => conceptIds.join("|"), [conceptIds])

  useEffect(() => {
    if (conceptIds.length === 0) {
      setUsedMap({})
      setReasons({})
      setLoading(false)
      return
    }

    const requestId = ++requestIdRef.current
    const controller = new AbortController()
    const timer = window.setTimeout(async () => {
      setLoading(true)
      try {
        const result = await scanExpectedConcepts({
          code,
          language,
          conceptIds,
          signal: controller.signal,
        })
        if (requestId !== requestIdRef.current) return
        const nextUsed: Record<string, boolean> = {}
        const nextReasons: Record<string, string> = {}
        for (const item of result.items) {
          nextUsed[item.id] = item.detected
          if (!item.detected && item.reason) {
            nextReasons[item.id] = item.reason
          }
        }
        setUsedMap(nextUsed)
        setReasons(nextReasons)
      } catch (error) {
        if (controller.signal.aborted) return
        if (requestId !== requestIdRef.current) return
        const fallback = buildLocalScan(code, language, concepts)
        setUsedMap(fallback.usedMap)
        setReasons(fallback.reasons)
      } finally {
        if (requestId === requestIdRef.current) {
          setLoading(false)
        }
      }
    }, debounceMs)

    return () => {
      controller.abort()
      window.clearTimeout(timer)
    }
  }, [code, language, conceptKey, debounceMs, conceptIds, concepts])

  return { usedMap, reasons, loading }
}
