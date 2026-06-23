import { assembleSlotTemplate, buildCode, getInitialBaseCode } from "@/domain/blockAssembly/buildCode"
import { templateScaffoldIsWhitespaceOnly } from "@/domain/blockAssembly/blockScaffold"
import { formatAssemblyTemplate } from "@/domain/blockAssembly/formatTemplate"
import { normalizePlacements } from "@/domain/blockAssembly/normalize"
import type { BlockPlacement } from "@/domain/blockAssembly/types"

export function prepareBlockAssemblyScaffold(
  template: string | null | undefined,
  blocks: string[] = [],
  language: string,
): { template: string; baseCode: string } {
  const formatted = formatAssemblyTemplate(String(template ?? ""), language)
  return {
    template: formatted,
    baseCode: getInitialBaseCode(formatted, blocks),
  }
}

/** Code preview for concept highlighting — matches submit assembly when possible. */
export function buildAssemblyPreviewCode(
  template: string | null | undefined,
  blocks: string[] = [],
  placements: BlockPlacement[] = [],
  baseCode = "",
  language: string,
): string {
  const raw = String(template ?? "")
  const formatted = formatAssemblyTemplate(raw, language)
  const base = baseCode || getInitialBaseCode(formatted, blocks)
  const normalized = normalizePlacements(placements, base)

  // Numbered `{n}` templates: slot replacement matches backend + authoring analysis.
  if (/\{\d+\}/.test(raw)) {
    const slotAssembled = assembleSlotTemplate(raw, blocks, normalized)
    if (slotAssembled.trim()) return slotAssembled
  }

  const whitespaceScaffold = templateScaffoldIsWhitespaceOnly(raw)
  const assemblyBase = whitespaceScaffold ? "" : base
  const assembled = buildCode(assemblyBase, normalized, blocks)
  if (assembled.trim()) return assembled

  const fromPlacements = normalizePlacements(placements, base)
    .sort((a, b) => a.line - b.line || a.slot - b.slot || a.column - b.column)
    .map((p) => blocks[p.blockIndex] ?? "")
    .filter(Boolean)
    .join("\n")
  if (fromPlacements.trim()) return fromPlacements

  if (/\{\d+\}/.test(formatted)) {
    return formatted.replace(/\{\d+\}/g, " ")
  }
  return /^_+$/i.test(formatted.trim()) ? "" : formatted
}
