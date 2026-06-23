import { useCallback, useMemo } from "react"
import {
  applyDrop,
  normalizePlacements,
  removePlacement,
} from "@/domain/blockAssembly"
import { shuffleBlockIndices } from "@/domain/blockReorderAssembly"
import { templateScaffoldIsWhitespaceOnly } from "@/domain/blockAssembly/blockScaffold"
import { buildTemplateDisplayLines } from "@/widgets/BlockAssemblyEditor/lib/buildTemplateDisplayLines"
import BlockAssemblyLayout from "@/widgets/BlockAssemblyEditor/ui/BlockAssemblyLayout"
import { DRAG_TYPE } from "@/widgets/BlockAssemblyEditor/ui/BlockAssemblyBank"
import { FixedCodeTokens, TemplateSlot } from "@/widgets/BlockAssemblyEditor/ui/TemplateCodeTokens"
export default function TemplateBlockAssemblyView({
  blocks = [],
  baseCode = "",
  rawTemplate,
  placements,
  onChange,
  language,
  primaryLanguage,
  shuffleKey = "",
  correctOrder,
}) {
  const lang = language || primaryLanguage || "python"
  const blocksOnlyScaffold = templateScaffoldIsWhitespaceOnly(String(rawTemplate ?? ""))

  const displayLines = useMemo(
    () => buildTemplateDisplayLines(baseCode, rawTemplate, placements, blocks),
    [baseCode, rawTemplate, placements, blocks],
  )

  const normalized = useMemo(
    () => normalizePlacements(placements, baseCode),
    [placements, baseCode],
  )

  const bankOrder = useMemo(
    () => shuffleBlockIndices(blocks.length, shuffleKey || blocks.join("|")),
    [blocks, shuffleKey],
  )

  const usedIndices = new Set(normalized.map((placement) => placement.blockIndex))
  const bankBlocks = bankOrder.filter((index) => !usedIndices.has(index))

  const emitPlacements = useCallback(
    (nextPlacements) => {
      onChange({
        placements: normalizePlacements(nextPlacements, baseCode),
      })
    },
    [baseCode, onChange],
  )

  const allowDrop = (event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"
  }

  const onDragStart = (event, blockIndex) => {
    event.dataTransfer.setData(DRAG_TYPE, String(blockIndex))
    event.dataTransfer.effectAllowed = "move"
  }

  const dropOnSlot = useCallback(
    (lineNum, dropColumn, templateSlot) => (event) => {
      event.preventDefault()
      event.stopPropagation()
      const raw = event.dataTransfer.getData(DRAG_TYPE)
      if (raw === "") return
      const blockIndex = Number(raw)
      if (Number.isNaN(blockIndex)) return

      emitPlacements(
        applyDrop(
          normalized,
          blocks,
          baseCode,
          blockIndex,
          lineNum,
          dropColumn,
          templateSlot,
        ),
      )
    },
    [normalized, blocks, baseCode, emitPlacements],
  )

  const clearSlotPlacement = useCallback(
    (placement) => {
      if (!placement) return
      emitPlacements(
        removePlacement(normalized, placement.blockIndex, placement.id),
      )
    },
    [normalized, emitPlacements],
  )

  const handleBankDrop = (event) => {
    event.preventDefault()
    const raw = event.dataTransfer.getData(DRAG_TYPE)
    if (raw === "") return
    const blockIndex = Number(raw)
    if (Number.isNaN(blockIndex)) return
    emitPlacements(removePlacement(normalized, blockIndex))
  }

  return (
    <BlockAssemblyLayout
      solution={
        <pre className="m-0 px-4 py-3 font-mono text-[14px] leading-[1.85]">
          {displayLines.map((line) => (
              <div key={line.lineNum} className="code-line">
                <div className="ln">{line.lineNum}</div>
                <div className="whitespace-pre">
                  {line.indentStr ? (
                    <span aria-hidden>{line.indentStr}</span>
                  ) : null}
                  {line.tokens.map((token, tokenIndex) => {
                    if (token.kind === "fixed") {
                      return (
                        <span key={`f-${line.lineNum}-${tokenIndex}`}>
                          <FixedCodeTokens text={token.text} language={lang} />
                        </span>
                      )
                    }

                    const placement = token.placement
                    const blockIndex = placement?.blockIndex
                    const blockText =
                      blockIndex != null ? (blocks[blockIndex] ?? "") : null
                    const dropColumn = token.dropColumn ?? 1

                    return (
                      <span key={`s-${line.lineNum}-${tokenIndex}`}>
                        <TemplateSlot
                          blockText={blockText}
                          compact={blocksOnlyScaffold}
                          onDragOver={allowDrop}
                          onDrop={dropOnSlot(
                            line.lineNum,
                            dropColumn,
                            token.templateSlot,
                          )}
                          onClear={() => clearSlotPlacement(placement)}
                        />
                      </span>
                    )
                  })}
                </div>
              </div>
          ))}
        </pre>
      }
      bank={{
        blocks,
        blockIndices: bankBlocks,
        hint: "· перетащи в пропуск",
        onDragStart,
        onDragOver: allowDrop,
        onDrop: handleBankDrop,
      }}
    />
  )
}
