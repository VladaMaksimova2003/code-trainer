/**
 * Lightweight task row from GET /tasks/overview or GET /tasks?light=true.
 */

export interface TaskOverviewItem {
  id: number
  slot_id?: string | null
  pedagogical_slot_id?: string | null
  concept_id?: string | null
  title: string
  language?: string | null
  target_language?: string | null
  course_key?: string | null
  chapter_key?: string | null
  available_language_tracks?: string[]
  language_track_states?: Record<string, "solved" | "attempted" | "todo">
  task_format?: string | null
  difficulty?: string | null
  type?: string | null
  task_type?: string | null
  constructions?: string[]
  attempted?: boolean
  solved?: boolean
  completed?: boolean
  submissions_count?: number
}

export interface TaskOverviewResponse {
  tasks: TaskOverviewItem[]
  total: number
  page: number
  page_size: number
}

export interface TaskOverviewFilters {
  course?: string
  chapter?: string
  targetLanguage?: string
  page?: number
  pageSize?: number
  search?: string
  type?: string
  difficulty?: string
  pattern?: string
  language?: string
  status?: string
  matchMode?: "all" | "any"
}
