import { api } from "@/shared/api"

import type { CatalogDto, CatalogTaskDto, CatalogTaskListItem } from "@/shared/types/catalog"



export const listCatalogTasks = async (params: Record<string, unknown> = {}): Promise<CatalogTaskListItem[]> => {

  const res = await api.get("/catalogs/tasks", { params })

  return res.data as CatalogTaskListItem[]

}



export const getCatalogTask = async (taskId: number | string): Promise<CatalogTaskListItem> => {
  const res = await api.get(`/catalogs/tasks/${taskId}`)
  return res.data as CatalogTaskListItem
}



export const createCatalogTask = async (payload: Record<string, unknown>): Promise<CatalogTaskListItem> => {

  const res = await api.post("/catalogs/tasks", payload)

  return res.data as CatalogTaskListItem

}



export const deleteCatalogTask = async (taskId: number | string): Promise<TaskRetireResultDto> => {
  const res = await api.delete(`/catalogs/tasks/${taskId}`)
  return res.data as TaskRetireResultDto
}

export type TaskRetireResultDto = {
  action: "deleted" | "archived" | "active"
  task_id: number
  submissions_count: number
}

export const archiveCatalogTask = async (taskId: number | string): Promise<void> => {
  await api.put(`/catalogs/tasks/${taskId}/workflow`, { status: "archived" })
}

export const deleteCurriculumChapter = async (
  chapterKey: string,
  language?: string,
): Promise<void> => {
  await api.delete(`/catalogs/chapters/${encodeURIComponent(chapterKey)}`, {
    params: language ? { language } : undefined,
  })
}



export const listMyCatalogs = async (): Promise<CatalogDto[]> => {

  const res = await api.get("/catalogs/mine")

  return res.data as CatalogDto[]

}



export const createCatalog = async (payload: Record<string, unknown>): Promise<CatalogDto> => {

  const res = await api.post("/catalogs", payload)

  return res.data as CatalogDto

}



export const getCatalog = async (catalogId: number | string): Promise<CatalogDto> => {

  const res = await api.get(`/catalogs/${catalogId}`)

  return res.data as CatalogDto

}



export const deleteCatalog = async (catalogId: number | string): Promise<void> => {

  await api.delete(`/catalogs/${catalogId}`)

}



export const getTasksByCatalog = async (catalogId: number | string): Promise<CatalogTaskDto[]> => {

  const res = await api.get(`/catalogs/${catalogId}/tasks`)

  return res.data as CatalogTaskDto[]

}



export const createTaskInCatalog = async (

  catalogId: number | string,

  payload: Record<string, unknown>,

): Promise<CatalogTaskDto> => {

  const res = await api.post(`/catalogs/${catalogId}/tasks`, payload)

  return res.data as CatalogTaskDto

}



export const assignTaskToCatalog = async (catalogId: number | string, taskId: number | string): Promise<void> => {

  await api.post(`/catalogs/${catalogId}/assignments`, { task_id: taskId })

}

export const assignTaskToChapter = async (
  taskId: number | string,
  payload: { language: string; chapter_key: string },
): Promise<{ task_id: number; language: string; chapter_key: string; chapter_title: string }> => {
  const res = await api.post(`/catalogs/tasks/${taskId}/chapter-placement`, payload)
  return res.data as { task_id: number; language: string; chapter_key: string; chapter_title: string }
}



export const removeTaskFromCatalog = async (catalogId: number | string, taskId: number | string): Promise<void> => {

  await api.delete(`/catalogs/${catalogId}/tasks/${taskId}`)

}



export const updateChapterTaskOrder = async (
  chapterKey: string,
  taskIds: number[],
): Promise<{ chapter_key: string; task_ids: number[] }> => {
  const res = await api.put("/catalogs/tasks/chapter-order", {
    chapter_key: chapterKey,
    task_ids: taskIds,
  })
  return res.data as { chapter_key: string; task_ids: number[] }
}

export const updateCollectionChapterOrder = async (
  chapterKeys: string[],
): Promise<{ chapter_keys: string[] }> => {
  const res = await api.put("/catalogs/tasks/collection-chapter-order", {
    chapter_keys: chapterKeys,
  })
  return res.data as { chapter_keys: string[] }
}

export type CurriculumChapterDto = {
  language: string
  chapter_key: string
  title: string
  description: string
  sort_order: number
  is_custom: boolean
  task_count: number
  registry_title?: string | null
  updated_at?: string | null
}

export const listCurriculumChapters = async (
  language?: string,
): Promise<CurriculumChapterDto[]> => {
  const res = await api.get("/catalogs/chapters", {
    params: language ? { language } : undefined,
  })
  return res.data as CurriculumChapterDto[]
}

export const createCurriculumChapter = async (payload: {
  language: string
  title: string
  description?: string
}): Promise<CurriculumChapterDto> => {
  const res = await api.post("/catalogs/chapters", payload)
  return res.data as CurriculumChapterDto
}

export const updateCurriculumChapter = async (
  chapterKey: string,
  payload: {
    language?: string
    title: string
    description?: string
  },
): Promise<CurriculumChapterDto> => {
  const res = await api.put(`/catalogs/chapters/${encodeURIComponent(chapterKey)}`, payload)
  return res.data as CurriculumChapterDto
}

export type CollectionMetaDto = {
  language: string
  title: string
  description: string
  registry_title?: string | null
  updated_at?: string | null
}

export const listCollectionMeta = async (): Promise<CollectionMetaDto[]> => {
  const res = await api.get("/catalogs/collections")
  return res.data as CollectionMetaDto[]
}

export const updateCollectionMeta = async (
  language: string,
  payload: { title: string; description?: string },
): Promise<CollectionMetaDto> => {
  const res = await api.put(`/catalogs/collections/${encodeURIComponent(language)}`, payload)
  return res.data as CollectionMetaDto
}

export type PlatformCourseMetaDto = {
  title: string
  description: string
  registry_title?: string | null
  updated_at?: string | null
  author_user_id?: number | null
  author_name?: string | null
}

export const getPlatformCourseMeta = async (): Promise<PlatformCourseMetaDto> => {
  const res = await api.get("/catalogs/platform-course")
  return res.data as PlatformCourseMetaDto
}

export const updatePlatformCourseMeta = async (payload: {
  title: string
  description?: string
}): Promise<PlatformCourseMetaDto> => {
  const res = await api.put("/catalogs/platform-course", payload)
  return res.data as PlatformCourseMetaDto
}

export type TeacherCourseDto = {
  id: number
  title: string
  description: string
  is_default: boolean
  task_count: number
  created_at: string
  updated_at?: string | null
}

export const listTeacherCourses = async (): Promise<TeacherCourseDto[]> => {
  const res = await api.get("/catalogs/courses")
  return res.data as TeacherCourseDto[]
}

export const createTeacherCourse = async (payload: {
  title: string
  description?: string
}): Promise<TeacherCourseDto> => {
  const res = await api.post("/catalogs/courses", payload)
  return res.data as TeacherCourseDto
}

export const updateTeacherCourse = async (
  courseId: number,
  payload: { title: string; description?: string },
): Promise<TeacherCourseDto> => {
  const res = await api.put(`/catalogs/courses/${courseId}`, payload)
  return res.data as TeacherCourseDto
}

export const listCatalogCourses = async (catalogId: number): Promise<TeacherCourseDto[]> => {
  const res = await api.get(`/catalogs/${catalogId}/courses`)
  return res.data as TeacherCourseDto[]
}

export const addCourseToCatalog = async (catalogId: number, courseId: number): Promise<void> => {
  await api.post(`/catalogs/${catalogId}/courses`, { course_id: courseId })
}

export const removeCourseFromCatalog = async (catalogId: number, courseId: number): Promise<void> => {
  await api.delete(`/catalogs/${catalogId}/courses/${courseId}`)
}

