import { httpClient } from "@/features/task-editor/infrastructure/api/httpClient"

export type DetectedExpectedConcept = {
  id: string
  label: string
}

export type DetectExpectedConceptsResult = {
  byLanguage: Record<string, DetectedExpectedConcept[]>
  suggestedIds: string[]
}

export async function detectExpectedConcepts(
  samples: Array<{ language: string; code: string }>,
): Promise<DetectExpectedConceptsResult> {
  const res = await httpClient.post<{
    by_language: Record<string, DetectedExpectedConcept[]>
    suggested_ids: string[]
  }>("/tasks/detect-expected-concepts", { samples })

  return {
    byLanguage: res.data.by_language ?? {},
    suggestedIds: res.data.suggested_ids ?? [],
  }
}
