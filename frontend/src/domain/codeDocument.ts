import { hasStructuralCodeContent } from "@/domain/codeInputNormalize"

export type DocumentNodeType = "code" | "block"

export interface DocumentNode {
  id: string
  type: DocumentNodeType
  text: string
}

export function createDocumentNodeId(): string {
  return `doc-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function createCodeNode(text = ""): DocumentNode {
  return { id: createDocumentNodeId(), type: "code", text }
}

export function createBlockNode(text = ""): DocumentNode {
  return { id: createDocumentNodeId(), type: "block", text }
}

/** @deprecated use text */
export function nodeText(node: DocumentNode): string {
  return node.text ?? (node as DocumentNode & { content?: string }).content ?? ""
}

export function documentToPlainText(document: DocumentNode[]): string {
  return document.map(nodeText).join("")
}

export function mergeAdjacentCodeNodes(
  document: DocumentNode[],
): DocumentNode[] {
  const merged: DocumentNode[] = []
  for (const node of document) {
    const text = nodeText(node)
    if (node.type === "block" && !hasStructuralCodeContent(text)) {
      continue
    }
    if (node.type === "code" && text.length === 0) {
      continue
    }
    if (
      node.type === "code" &&
      merged.length > 0 &&
      merged[merged.length - 1].type === "code"
    ) {
      const prev = merged[merged.length - 1]
      merged[merged.length - 1] = { ...prev, text: prev.text + text }
    } else {
      merged.push({ ...node, text })
    }
  }
  return merged
}

export function updateNodeText(
  document: DocumentNode[],
  nodeId: string,
  text: string,
): DocumentNode[] {
  return document.map((node) =>
    node.id === nodeId ? { ...node, text } : node,
  )
}

export function convertNodeType(
  document: DocumentNode[],
  nodeId: string,
  type: DocumentNodeType,
): DocumentNode[] {
  const next = document.map((node) =>
    node.id === nodeId ? { ...node, type } : node,
  )
  return type === "code" ? mergeAdjacentCodeNodes(next) : next
}

export function convertSelectionToBlock(
  document: DocumentNode[],
  nodeId: string,
  selectionStart: number,
  selectionEnd: number,
): DocumentNode[] {
  const index = document.findIndex((n) => n.id === nodeId)
  if (index === -1) return document

  const node = document[index]
  if (node.type !== "code") return document

  const start = Math.max(0, Math.min(selectionStart, selectionEnd))
  const end = Math.max(start, Math.max(selectionStart, selectionEnd))
  const full = nodeText(node)
  const before = full.slice(0, start)
  const selected = full.slice(start, end)
  const after = full.slice(end)

  if (!selected || !hasStructuralCodeContent(selected)) return document

  const replacement: DocumentNode[] = []
  if (before) replacement.push(createCodeNode(before))
  replacement.push(createBlockNode(selected))
  if (after) replacement.push(createCodeNode(after))

  const next = [...document]
  next.splice(index, 1, ...replacement)
  return mergeAdjacentCodeNodes(next)
}

export function migrateSegmentContent(
  node: DocumentNode & { content?: string },
): DocumentNode {
  const text = node.text ?? node.content ?? ""
  return { id: node.id, type: node.type, text }
}

export function migrateDocument(
  document: (DocumentNode & { content?: string })[] | undefined,
  fallbackCode = "",
): DocumentNode[] {
  if (!document?.length) {
    return [createCodeNode(fallbackCode)]
  }
  return mergeAdjacentCodeNodes(document.map(migrateSegmentContent))
}
