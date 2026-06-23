/**
 * Shared task DTO shapes for GET /tasks/:id and list endpoints.
 * GET /tasks/:id — OpenAPI `PublicTaskDetailResponse`; helper types for UI narrowing.
 */

import type { ApiSchema } from "./openapi"

export type TaskDto = ApiSchema["PublicTaskDetailResponse"]

export type TaskDifficulty = "easy" | "medium" | "hard" | string

/** Public task type id from API (`type` / `task_type`). */
export type TaskType =
  | "blocks"
  | "diagram"
  | "task_flowchart_to_code"
  | "block_reorder"
  | "code_assembly"
  | "task_build_from_blocks"
  | "algorithm"
  | "translation"
  | "task_translate_snippet"
  | "task_translate_full_program"
  | string

export type FlowchartMode =
  | "code_to_flowchart"
  | "flowchart_to_code"
  | "flowchart_to_blocks"
  | string

export type CurriculumAction = "analyze" | "solve" | "build" | string

export interface CurriculumMeta {
  action?: CurriculumAction
  flowchart_mode?: FlowchartMode
  collection_key?: string
  collection_title?: string
  slot_id?: string
  chapter_slug?: string
  expected_output?: string
  primary_action?: string
  [key: string]: unknown
}

export interface CodeExampleMap {
  [language: string]: string
}

export interface TaskTestCase {
  inputs?: string
  input?: string
  output?: string
  expected?: string
  expected_output?: string
}

export interface TaskBlock {
  text?: string
  label?: string
  [key: string]: unknown
}

export interface LanguageVariant {
  language?: string
  blocks?: TaskBlock[]
  template?: string | null
  [key: string]: unknown
}

/** Block assembly / block reorder task fields from GET /tasks/:id. */
export interface BlockAssemblyTaskFields {
  blocks?: TaskBlock[]
  template?: string | null
  language_variants?: LanguageVariant[]
  language?: string
}

/** Analyze-task fields (curriculum.action === "analyze"). */
export interface AnalyzeTaskFields {
  curriculum?: CurriculumMeta & { expected_output?: string }
  expected_output?: string
  test_cases?: TaskTestCase[]
  code_examples?: CodeExampleMap
}

/** Narrowing helpers — primary task shape comes from OpenAPI. */
export type PublicTaskDetail = TaskDto
