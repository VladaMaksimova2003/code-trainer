import type { CodeBlockRange } from "@/domain/codeBlockRanges"
import {
  documentFromRanges,
  documentToRanges,
  normalizeRanges,
} from "@/domain/codeBlockRanges"
import { migrateDocument } from "@/domain/codeDocument"
import type { TaskDraft } from "@/features/task-editor/domain/entities"

export type { CodeBlockRange }

export function ensureDraftBlockEditor(draft: TaskDraft): TaskDraft {
  const codeText = draft.code?.code ?? ""
  const code = { ...(draft.code ?? { code: "", language: "python" }), code: codeText }

  if (Array.isArray(draft.blockRanges)) {
    const blockRanges = normalizeRanges(draft.blockRanges, codeText)
    const segments = documentFromRanges(codeText, blockRanges)
    return { ...draft, code, blockRanges, segments }
  }

  const document = migrateDocument(
    draft.segments as Parameters<typeof migrateDocument>[0],
    codeText,
  )
  const { code: syncedCode, ranges: blockRanges } = documentToRanges(document)
  const normalizedRanges = normalizeRanges(blockRanges, syncedCode)
  const segments = documentFromRanges(syncedCode, normalizedRanges)

  return {
    ...draft,
    code: { ...code, code: syncedCode },
    blockRanges: normalizedRanges,
    segments,
  }
}
