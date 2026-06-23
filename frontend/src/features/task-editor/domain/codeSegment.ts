import type { TaskDraft } from "@/features/task-editor/domain/entities"
import {
  createCodeNode,
  createDocumentNodeId,
  type DocumentNode,
  type DocumentNodeType,
  documentToPlainText,
  migrateDocument,
} from "@/domain/codeDocument"

export type SegmentType = DocumentNodeType
export type CodeSegment = DocumentNode

export function createSegmentId(): string {
  return createDocumentNodeId()
}

export function createDefaultSegments(code = ""): DocumentNode[] {
  return migrateDocument(undefined, code)
}

export function ensureDraftSegments(draft: TaskDraft): TaskDraft {
  const document = migrateDocument(
    draft.segments as (DocumentNode & { content?: string })[] | undefined,
    draft.code.code,
  )
  const selectedSegmentId =
    draft.selectedSegmentId &&
    document.some((s) => s.id === draft.selectedSegmentId)
      ? draft.selectedSegmentId
      : document[0]?.id ?? null

  return {
    ...draft,
    segments: document,
    selectedSegmentId,
  }
}

export function segmentsToCode(segments: DocumentNode[]): string {
  return documentToPlainText(segments)
}

export {
  createBlockNode,
  createCodeNode,
} from "@/domain/codeDocument"
