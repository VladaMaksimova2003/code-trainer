import type { CodeBlockRange } from "@/domain/codeBlockRanges"
import type { CodeSegment } from "@/features/task-editor/domain/codeSegment"
import type { IoValue, IoValueKind } from "@/features/task-editor/domain/ioValue"
import type { AnalysisStatus, DifficultyLevel, PatternType, TaskType } from "@/features/task-editor/domain/enums"

export interface IoSchema {
  inputFormat: IoValueKind
  outputFormat: IoValueKind
}

export interface ConceptCard {
  id: string
  name_ru?: string
  description_ru?: string
  descriptions_by_language?: Record<string, string>
  examples_by_language?: Record<string, Array<{ title?: string; code?: string }>>
  pascal_template?: string
}

export interface Pattern {
  id: string
  type: PatternType | string
  label: string
  confidence: number
  sourceConstruct?: string
  approved?: boolean
  card?: ConceptCard
}

export interface CodeSnippet {
  code: string
  language: string
}

export interface TestCase {
  id: string
  name?: string
  input: IoValue
  expectedOutput: IoValue
  description?: string
}

export interface AnalysisResult {
  patterns: Pattern[]
  rawConstructs: string[]
  status: AnalysisStatus
  error?: string
}

export interface TaskDraft {
  id?: string
  title: string
  description: string
  /** Доп. поле при выборе типа (контент задания) */
  content?: string
  /** Ситуация / контекст программы */
  programSituation?: string
  type: TaskType
  difficulty: DifficultyLevel
  languages: string[]
  selectedPatterns: Pattern[]
  /** Display TC card ids per programming language (tc_display_registry.json). */
  selectedPatternsByLanguage?: Record<string, string[]>
  code: CodeSnippet
  segments?: CodeSegment[]
  /** Character ranges (start inclusive, end exclusive) marked as blocks in code.code */
  blockRanges?: CodeBlockRange[]
  selectedSegmentId?: string | null
  analysis: AnalysisResult | null
  testCases: TestCase[]
  ioSchema: IoSchema
  flow?: { flow: unknown[]; nodes: unknown[]; edges: unknown[] }
  /** Per-language block-reorder payloads (showcase / curriculum tasks). */
  languageVariants?: Record<
    string,
    {
      original_code?: string
      blocks?: string[]
      template?: string | null
      correct_order?: number[]
    }
  >
  /** Teacher block markings preserved while switching languages in the editor. */
  languageBlockEditorState?: Record<
    string,
    {
      code: string
      blockRanges: CodeBlockRange[]
    }
  >
  /** Показывать эталонный код студенту (составление схемы по коду). */
  flowchartExposeReferenceCode?: boolean
  /** Задача «Исправить» — отдельные эталон и код с ошибкой для ученика. */
  isDebugTask?: boolean
  catalogId?: number | null
  version: number
  updatedAt: string
}

export interface CreateTaskPayload {
  title: string
  description: string
  content?: string
  programSituation?: string
  type: TaskType
  patterns: string[]
  code: string
  testCases: TestCase[]
  difficulty: DifficultyLevel
  languages: string[]
  ioSchema: IoSchema
  flow?: { flow: unknown[]; nodes: unknown[]; edges: unknown[] }
}
