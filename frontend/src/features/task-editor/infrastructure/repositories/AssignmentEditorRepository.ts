import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { DifficultyLevel } from "@/features/task-editor/domain/enums"
import {
  getAssignmentEditorMode,
  inferIsDebugTaskFromTaskPayload,
  isTranslationAssignmentType,
} from "@/features/task-editor/domain/assignmentRules"
import { toAssignmentTypeId } from "@/shared/types/taskLabels"
import { IoValueKind, normalizeIoValue } from "@/features/task-editor/domain/ioValue"
import { httpClient } from "@/features/task-editor/infrastructure/api/httpClient"
import { getDefaultLanguageId } from "@/shared/config/languages"
import { buildInitialLanguageBlockEditorState, buildLanguageBlockEditorStateFromCodes } from "@/features/task-editor/domain/languageBlockEditorState"
import { inferBlockRangesFromAuthorPayload } from "@/features/task-editor/domain/inferBlockRangesFromAuthor"
import { mapConceptIdsToPatterns } from "@/features/task-editor/domain/expectedConceptPatterns"

function mapTestCases(raw: unknown): TaskDraft["testCases"] {
  const items = Array.isArray(raw) ? raw : []
  return items.map((tc, i) => ({
    id: `tc-${i}`,
    name: String(tc.name ?? `Тест ${i + 1}`),
    input: normalizeIoValue(tc.input ?? tc.inputs ?? ""),
    expectedOutput: normalizeIoValue(tc.expected_output ?? tc.output ?? ""),
    description: tc.description ? String(tc.description) : undefined,
  }))
}

function mapFlowPayload(raw: Record<string, unknown> | null | undefined): TaskDraft["flow"] {
  const diagram = raw?.diagram
  if (diagram && typeof diagram === "object") {
    const payload = diagram as { flow?: unknown[]; nodes?: unknown[]; edges?: unknown[] }
    return {
      flow: Array.isArray(payload.flow) ? payload.flow : [],
      nodes: Array.isArray(payload.nodes) ? payload.nodes : [],
      edges: Array.isArray(payload.edges) ? payload.edges : [],
    }
  }
  const flowSpec = raw?.flow_spec
  if (flowSpec && typeof flowSpec === "object") {
    const payload = flowSpec as { flow?: unknown[]; nodes?: unknown[]; edges?: unknown[] }
    if (Array.isArray(payload.nodes) && payload.nodes.length > 0) {
      return {
        flow: Array.isArray(payload.flow) ? payload.flow : [],
        nodes: payload.nodes,
        edges: Array.isArray(payload.edges) ? payload.edges : [],
      }
    }
  }
  return { flow: [], nodes: [], edges: [] }
}

export { inferBlockRangesFromAuthorPayload } from "@/features/task-editor/domain/inferBlockRangesFromAuthor"

export class AssignmentEditorRepository {
  async loadForEdit(taskId: number): Promise<TaskDraft> {
    const taskRes = await httpClient.get<Record<string, unknown>>(`/tasks/${taskId}`)
    const task = taskRes.data
    const isDebugTask = inferIsDebugTaskFromTaskPayload(task)
    const rawType = String(task.type || task.task_type || "translation")
    const assignmentType = toAssignmentTypeId(rawType) as TaskDraft["type"]

    if (getAssignmentEditorMode(assignmentType) === "flowchart") {
      const authorRes = await httpClient.get<Record<string, unknown>>(
        `/tasks/flowchart/${taskId}/author`,
      )
      const author = authorRes.data
      const testCases = mapTestCases(author.test_cases)
      const patterns = Array.isArray(author.patterns)
        ? author.patterns.map((id) => ({
            id: String(id),
            type: String(id),
            label: String(id),
            confidence: 1,
            approved: true,
          }))
        : []
      const lang = String(author.language || getDefaultLanguageId())
      const referenceCode = String(author.reference_code ?? "")

      return {
        id: String(taskId),
        title: String(author.title ?? task.title ?? ""),
        description: String(author.description ?? task.description ?? ""),
        type: assignmentType,
        difficulty: (String(author.difficulty || task.difficulty || "easy") as DifficultyLevel),
        languages: [lang],
        selectedPatterns: patterns,
        code: { code: referenceCode, language: lang },
        flowchartExposeReferenceCode: Boolean(author.expose_reference_code),
        analysis: null,
        testCases,
        ioSchema: {
          inputFormat: IoValueKind.SCALAR,
          outputFormat: IoValueKind.SCALAR,
        },
        flow: mapFlowPayload(author),
        isDebugTask,
        version: 1,
        updatedAt: new Date().toISOString(),
      }
    }

    if (isTranslationAssignmentType(assignmentType)) {
      try {
        const authorRes = await httpClient.get<Record<string, unknown>>(
          `/tasks/translation/${taskId}/author`,
        )
        const author = authorRes.data
        const lang = String(author.source_language || author.language || getDefaultLanguageId())
        const sourceCode = String(author.source_code ?? "")
        const testCases = mapTestCases(author.test_cases)
        const patternsByLanguage =
          (author.patterns_by_language as Record<string, string[]>) ?? {}
        const patternIds = Array.isArray(author.patterns)
          ? author.patterns.map((id) => String(id))
          : patternsByLanguage[lang] ?? []
        if (Object.keys(patternsByLanguage).length === 0 && patternIds.length > 0) {
          patternsByLanguage[lang] = patternIds
        }
        const patterns = patternIds.map((id) => ({
          id: String(id),
          type: String(id),
          label: String(id),
          confidence: 1,
          approved: true,
        }))
        const languageCodes = (author.language_codes as Record<string, string>) ?? {}
        const languageBlockEditorState = buildLanguageBlockEditorStateFromCodes(
          Object.keys(languageCodes).length > 0
            ? languageCodes
            : { [lang]: sourceCode },
          lang,
        )

        return {
          id: String(taskId),
          title: String(author.title ?? task.title ?? ""),
          description: String(author.description ?? task.description ?? ""),
          type: assignmentType,
          difficulty: (String(author.difficulty || task.difficulty || "easy") as DifficultyLevel),
          languages: [lang],
          selectedPatternsByLanguage: patternsByLanguage,
          selectedPatterns: mapConceptIdsToPatterns([], patternsByLanguage[lang] ?? patternIds),
          code: {
            code: languageBlockEditorState[lang]?.code ?? sourceCode,
            language: lang,
          },
          languageBlockEditorState,
          analysis: null,
          testCases,
          ioSchema: {
            inputFormat: IoValueKind.SCALAR,
            outputFormat: IoValueKind.SCALAR,
          },
          flow: { flow: [], nodes: [], edges: [] },
          isDebugTask,
          version: 1,
          updatedAt: new Date().toISOString(),
        }
      } catch {
        // Fall through to generic task payload below.
      }
    }

    let author: Record<string, unknown> | null = null
    try {
      const res = await httpClient.get(`/tasks/code-assembly/${taskId}/author`)
      author = res.data
    } catch {
      author = null
    }

    if (author) {
      const lang = String(author.language || getDefaultLanguageId())
      const rawType = String(author.task_type || author.type || "block_reorder")
      const testCases = mapTestCases(author.test_cases)
      const languageVariants = (author.language_variants as TaskDraft["languageVariants"]) || {}
      const patternsByLanguage = (author.patterns_by_language as Record<string, string[]>) ?? {}
      const patternIds = Array.isArray(author.patterns)
        ? author.patterns.map((id) => String(id))
        : patternsByLanguage[lang] ?? []
      if (Object.keys(patternsByLanguage).length === 0 && patternIds.length > 0) {
        patternsByLanguage[lang] = patternIds
      }
      const languageBlockEditorState = buildInitialLanguageBlockEditorState(
        lang,
        author,
        languageVariants,
      )
      return {
        id: String(taskId),
        title: String(author.title ?? ""),
        description: String(author.description ?? ""),
        type: toAssignmentTypeId(rawType) as TaskDraft["type"],
        difficulty:
          (String(author.difficulty || "easy") as DifficultyLevel) ||
          DifficultyLevel.EASY,
        languages: [lang],
        selectedPatternsByLanguage: patternsByLanguage,
        selectedPatterns: mapConceptIdsToPatterns([], patternsByLanguage[lang] ?? patternIds),
        code: { code: String(author.original_code ?? ""), language: lang },
        blockRanges: languageBlockEditorState[lang]?.blockRanges ?? inferBlockRangesFromAuthorPayload(author),
        languageVariants,
        languageBlockEditorState,
        analysis: null,
        testCases,
        ioSchema: {
          inputFormat: IoValueKind.SCALAR,
          outputFormat: IoValueKind.SCALAR,
        },
        flow: { flow: [], nodes: [], edges: [] },
        isDebugTask,
        version: 1,
        updatedAt: new Date().toISOString(),
      }
    }

    const lang =
      String(task.language || "") ||
      Object.keys((task.code_examples as Record<string, string>) || {})[0] ||
      getDefaultLanguageId()
    const examples = (task.code_examples as Record<string, string>) || {}
    const code = examples[lang] || Object.values(examples)[0] || ""

    const patternIds = Array.isArray(task.constructions)
      ? (task.constructions as string[]).map(String)
      : Array.isArray((task as { patterns?: string[] }).patterns)
        ? ((task as { patterns?: string[] }).patterns ?? []).map(String)
        : []
    const testCases = mapTestCases(task.test_cases)

    const flow = mapFlowPayload(task)

    return {
      id: String(taskId),
      title: String(task.title ?? ""),
      description: String(task.description ?? ""),
      type: toAssignmentTypeId(rawType) as TaskDraft["type"],
      difficulty: (String(task.difficulty || "easy") as DifficultyLevel),
      languages: [lang],
      selectedPatterns: mapConceptIdsToPatterns([], patternIds),
      code: { code, language: lang },
      analysis: null,
      testCases,
      ioSchema: {
        inputFormat: IoValueKind.SCALAR,
        outputFormat: IoValueKind.SCALAR,
      },
      flow,
      isDebugTask,
      version: 1,
      updatedAt: new Date().toISOString(),
    }
  }

  async updateBlockTask(
    taskId: number,
    body: Record<string, unknown>
  ): Promise<void> {
    await httpClient.put(`/tasks/code-assembly/${taskId}`, body)
  }

  async updateFlowchartTask(
    taskId: number,
    body: Record<string, unknown>
  ): Promise<void> {
    await httpClient.put(`/tasks/flowchart/${taskId}`, body)
  }

  async updateTranslationTask(
    taskId: number,
    body: Record<string, unknown>
  ): Promise<void> {
    await httpClient.put(`/tasks/translation/${taskId}`, body)
  }
}
