/** URL создания задания с опциональной привязкой к главе и языку. */
export function teacherTaskCreatePath(options?: {
  chapterKey?: string | null
  language?: string | null
}): string {
  const params = new URLSearchParams()
  if (options?.chapterKey) params.set("chapter", options.chapterKey)
  if (options?.language) params.set("language", options.language)
  const query = params.toString()
  return query ? `/teacher/create-task?${query}` : "/teacher/create-task"
}
