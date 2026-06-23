/** View-model types for curriculum UI (aligned with backend OpenAPI schemas). */

export type ProgressStatus = "passed" | "failed" | "not_started"

export type ActionType =
  | "translate"
  | "assemble"
  | "implement"
  | "debug"
  | "analyze"
  | "recognize"

export interface CollectionProgress {
  total_tasks: number
  passed_tasks: number
  progress_percent?: number
  catalog_tasks?: number
}

export interface NextTask {
  task_id: number
  title?: string | null
  slug?: string | null
  progress_status?: ProgressStatus | string | null
}

/** Карточка сборника на хабе языка (/learn/pascal). */
export interface Collection {
  collection_id: string
  title_ru: string
  description_ru?: string | null
  route_path: string
  order: number
  progress: CollectionProgress
  completed: boolean
  button_label: string
  next_task: NextTask | null
}

/** Язык целиком (агрегат + список сборников). */
export interface LanguageTrack {
  language: string
  language_label: string
  track_description_ru?: string | null
  progress: CollectionProgress
  collections: Collection[]
}

export interface ShowcaseTask {
  task_id: number
  title: string
  action: ActionType | string
  action_label: string
  action_skill_label: string
  action_description_ru: string
  difficulty: string
  progress_status?: ProgressStatus | string | null
  short_instruction: string
  subtopic_name_ru: string
  available_language_tracks?: string[]
  language_track_states?: Record<string, "solved" | "attempted" | "todo">
}

export interface ShowcaseSection {
  id?: string | null
  name_ru: string
  tasks: ShowcaseTask[]
  progress?: CollectionProgress | null
}

/** State, который страница задачи ждёт от curriculum-навигации. */
export interface CurriculumNavState {
  returnTo: string
  navigationMode: "curriculum"
  collectionId: string
  learningLanguage?: "python" | "pascal" | "cpp" | "csharp" | "java"
}
