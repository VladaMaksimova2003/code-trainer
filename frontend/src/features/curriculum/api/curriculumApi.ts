import { api } from "@/shared/api"
import type {
  CurriculumCollectionNavigationDto,
  CurriculumCollectionsDto,
  CurriculumNextDto,
  CurriculumShowcaseNextDto,
  CurriculumShowcaseStudentDto,
} from "@/shared/types/curriculum"
import type { LanguageTrack } from "@/features/curriculum/types"
import { isPlatformCurriculumChapter } from "@/features/curriculum/learnTracksUi"
import { sectionsOf } from "@/features/curriculum/components/SubtopicSection"

const LANGUAGE = "pascal"

export async function fetchShowcaseStudent(
  language: string,
  routeSuffix: string,
): Promise<CurriculumShowcaseStudentDto> {
  const res = await api.get(`/curriculum/${language}/showcase/${routeSuffix}/student`)
  return res.data as CurriculumShowcaseStudentDto
}

export async function fetchShowcaseNext(
  language: string,
  routeSuffix: string,
): Promise<CurriculumShowcaseNextDto> {
  const res = await api.get(`/curriculum/${language}/showcase/${routeSuffix}/next`)
  return res.data as CurriculumShowcaseNextDto
}

export async function fetchPascalShowcaseStudent(routeSuffix: string): Promise<CurriculumShowcaseStudentDto> {
  return fetchShowcaseStudent("pascal", routeSuffix)
}

export async function fetchPascalShowcaseNext(routeSuffix: string): Promise<CurriculumShowcaseNextDto> {
  return fetchShowcaseNext("pascal", routeSuffix)
}

/** GET /curriculum/collections → конкретный язык. */
export async function getLanguageTrack(language: string): Promise<LanguageTrack | null> {
  const data = await fetchCurriculumCollections(language, { light: true })
  const block = data.languages?.find((l) => l.language === language)
  if (!block) return null

  return {
    language: block.language,
    language_label: block.language_label ?? block.language,
    track_description_ru: block.track_description_ru ?? null,
    progress: {
      total_tasks: block.progress?.total_tasks ?? 0,
      passed_tasks: block.progress?.passed_tasks ?? 0,
      progress_percent: block.progress?.progress_percent,
      catalog_tasks: block.progress?.catalog_tasks,
    },
    collections: (block.collections ?? [])
      .filter(isPlatformCurriculumChapter)
      .map((c, index) => ({
      collection_id: c.collection_id,
      title_ru: c.title_ru,
      description_ru: c.description_ru,
      route_path: c.route_path,
      order: index + 1,
      progress: {
        total_tasks: c.progress?.total_tasks ?? 0,
        passed_tasks: c.progress?.passed_tasks ?? 0,
        progress_percent: c.progress?.progress_percent,
        catalog_tasks: c.progress?.catalog_tasks,
      },
      completed: Boolean(c.completed),
      button_label: c.button_label ?? "Продолжить",
      next_task: c.next_task?.task_id
        ? {
            task_id: c.next_task.task_id,
            title: c.next_task.title,
            slug: c.next_task.slug,
            progress_status: c.next_task.progress_status,
          }
        : null,
    })),
  }
}

/** GET /curriculum/{language}/showcase/{slug}/student */
export async function getShowcase(language: string, slug: string): Promise<CurriculumShowcaseStudentDto> {
  return fetchShowcaseStudent(language, slug)
}

/** GET /curriculum/{language}/showcase/{slug}/next */
export async function getShowcaseNext(language: string, slug: string): Promise<CurriculumShowcaseNextDto> {
  return fetchShowcaseNext(language, slug)
}

export { sectionsOf }

export function showcaseSlugFromRoute(routePath: string): string | null {
  const trimmed = String(routePath || "").replace(/\/+$/, "")
  const parts = trimmed.split("/").filter(Boolean)
  return parts.length >= 3 ? parts[2] : null
}

/** Resolve next task for a chapter (uses cached next_task or /showcase/.../next). */
export async function resolveCollectionNextTaskId(
  language: string,
  chapter: { route_path?: string; next_task?: { task_id?: number } | null },
): Promise<number | null> {
  const existing = chapter.next_task?.task_id
  if (existing) return existing
  const slug = showcaseSlugFromRoute(String(chapter.route_path || ""))
  if (!slug) return null
  const payload = await fetchShowcaseNext(language, slug)
  return payload?.next_task?.task_id ?? null
}

export async function fetchPascalConditionsShowcaseStudent(): Promise<CurriculumShowcaseStudentDto> {
  return fetchPascalShowcaseStudent("conditions")
}

export async function fetchPascalConditionsShowcaseNext(): Promise<CurriculumShowcaseNextDto> {
  return fetchPascalShowcaseNext("conditions")
}

export async function fetchPascalLoopsShowcaseStudent(): Promise<CurriculumShowcaseStudentDto> {
  return fetchPascalShowcaseStudent("loops")
}

export async function fetchCurriculumCollections(
  language?: string,
  options?: { light?: boolean },
): Promise<CurriculumCollectionsDto> {
  const params: Record<string, string | boolean> = {}
  if (language) params.language = language
  if (options?.light) params.light = true
  const res = await api.get("/curriculum/collections", { params })
  return res.data as CurriculumCollectionsDto
}

export async function fetchCurriculumNext(): Promise<CurriculumNextDto> {
  const res = await api.get("/curriculum/next")
  return res.data as CurriculumNextDto
}

export async function fetchCurriculumCollectionNavigation(
  collectionId: number | string,
  taskId: number | string,
): Promise<CurriculumCollectionNavigationDto> {
  const res = await api.get(`/curriculum/collections/${collectionId}/navigation`, {
    params: { task_id: taskId },
  })
  return res.data as CurriculumCollectionNavigationDto
}

export async function fetchPascalLoopsShowcaseNext(): Promise<CurriculumShowcaseNextDto> {
  return fetchPascalShowcaseNext("loops")
}

export async function fetchAllPascalTaskIds(): Promise<{ task_ids: number[] }> {
  const res = await api.get("/curriculum/pascal/showcase/all-task-ids")
  return res.data as { task_ids: number[] }
}

export async function fetchAllPythonTaskIds(): Promise<{ task_ids: number[] }> {
  const res = await api.get("/curriculum/python/showcase/all-task-ids")
  return res.data as { task_ids: number[] }
}

export async function fetchAllCppTaskIds(): Promise<{ task_ids: number[] }> {
  const res = await api.get("/curriculum/cpp/showcase/all-task-ids")
  return res.data as { task_ids: number[] }
}

export async function fetchAllJavaTaskIds(): Promise<{ task_ids: number[] }> {
  const res = await api.get("/curriculum/java/showcase/all-task-ids")
  return res.data as { task_ids: number[] }
}

export async function fetchAllCsharpTaskIds(): Promise<{ task_ids: number[] }> {
  const res = await api.get("/curriculum/csharp/showcase/all-task-ids")
  return res.data as { task_ids: number[] }
}

