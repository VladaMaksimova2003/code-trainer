import type { TaskDraft } from "@/features/task-editor/domain/entities"
import { toAssignmentTypeId } from "@/shared/types/taskLabels"
import { buildPatternsByLanguageForSave } from "@/features/task-editor/domain/expectedConceptPatterns"
import {
  currentDraftLanguage,
  snapshotDraftBlockEditor,
} from "@/features/task-editor/domain/languageBlockEditorState"

export function buildTranslationApiFields(draft: TaskDraft) {
  const source_language = currentDraftLanguage(draft)
  const snapshots = snapshotDraftBlockEditor(draft, source_language)
  const language_codes: Record<string, string> = {}

  for (const [language, snapshot] of Object.entries(snapshots)) {
    const code = String(snapshot.code ?? "")
    if (code.trim()) {
      language_codes[language] = code
    }
  }

  const source_code = language_codes[source_language] ?? draft.code.code ?? ""

  return {
    source_code,
    source_language,
    language_codes,
    patterns_by_language: buildPatternsByLanguageForSave(draft),
    task_type: toAssignmentTypeId(String(draft.type || "")),
    is_debug_task: Boolean(draft.isDebugTask),
  }
}
