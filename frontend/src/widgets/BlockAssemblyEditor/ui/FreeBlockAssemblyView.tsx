import { useCallback, useEffect, useMemo, useState } from "react"
import { shuffleBlockIndices } from "@/domain/blockReorderAssembly"
import {
  linesFromPlacements,
  placementsFromLines,
} from "@/widgets/BlockAssemblyEditor/lib/freeAssemblyLines"
import BlockAssemblyLayout from "@/widgets/BlockAssemblyEditor/ui/BlockAssemblyLayout"
import { DRAG_TYPE } from "@/widgets/BlockAssemblyEditor/ui/BlockAssemblyBank"
import { formatBlockDisplayText } from "@/domain/blockAssembly"

function newLineId() {
  return `L${Math.random().toString(36).slice(2, 8)}`
}

function IconChevL() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
      <path d="M10 4L6 8l4 4" />
    </svg>
  )
}

function IconChevR() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
      <path d="M6 4l4 4-4 4" />
    </svg>
  )
}

function IconX() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
      <path d="M4 4l8 8M12 4l-8 8" />
    </svg>
  )
}

function LineIconButton({ onClick, title, disabled, tone, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      disabled={disabled}
      className={[
        "inline-flex h-7 w-7 items-center justify-center rounded-md border border-[#333d4f] bg-surface-2 text-ink-muted transition",
        !disabled && "hover:border-[#3e4a60] hover:text-ink",
        !disabled && tone === "danger" && "hover:border-danger/50 hover:bg-danger-soft hover:text-danger",
        !disabled && tone === "lime" && "hover:border-lime/50 hover:bg-lime-soft hover:text-lime",
        disabled && "cursor-not-allowed opacity-30",
      ].join(" ")}
    >
      {children}
    </button>
  )
}

export default function FreeBlockAssemblyView({
  blocks = [],
  placements,
  onChange,
  shuffleKey = "",
}) {
  const [lines, setLines] = useState(() => linesFromPlacements(placements, ""))
  const [hoverLineId, setHoverLineId] = useState(null)

  useEffect(() => {
    setLines(linesFromPlacements(placements, ""))
  }, [placements, shuffleKey])

  const bankOrder = useMemo(
    () => shuffleBlockIndices(blocks.length, shuffleKey || blocks.join("|")),
    [blocks, shuffleKey],
  )

  const placedIndices = useMemo(() => {
    const set = new Set()
    lines.forEach((line) => line.blockIndices.forEach((index) => set.add(index)))
    return set
  }, [lines])

  const bankBlocks = bankOrder.filter((index) => !placedIndices.has(index))

  const commitLines = useCallback(
    (nextLines) => {
      setLines(nextLines)
      onChange({ placements: placementsFromLines(nextLines, blocks) })
    },
    [blocks, onChange],
  )

  const ensureTrailing = (inputLines) => {
    const next = [...inputLines]
    const last = next[next.length - 1]
    if (!last || last.blockIndices.length > 0) {
      next.push({ id: newLineId(), indent: 0, blockIndices: [] })
    }
    return next
  }

  const onDragStart = (event, blockIndex) => {
    event.dataTransfer.setData(DRAG_TYPE, String(blockIndex))
    event.dataTransfer.effectAllowed = "move"
  }

  const allowDrop = (event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"
  }

  const dropOnLine = (lineId) => (event) => {
    event.preventDefault()
    event.stopPropagation()
    setHoverLineId(null)
    const raw = event.dataTransfer.getData(DRAG_TYPE)
    if (raw === "") return
    const blockIndex = Number(raw)
    if (Number.isNaN(blockIndex)) return

    commitLines(
      ensureTrailing(
        lines.map((line) => {
          const without = {
            ...line,
            blockIndices: line.blockIndices.filter((index) => index !== blockIndex),
          }
          if (line.id !== lineId) return without
          return { ...without, blockIndices: [...without.blockIndices, blockIndex] }
        }),
      ),
    )
  }

  const dropOnBank = (event) => {
    event.preventDefault()
    const raw = event.dataTransfer.getData(DRAG_TYPE)
    if (raw === "") return
    const blockIndex = Number(raw)
    if (Number.isNaN(blockIndex)) return

    commitLines(
      ensureTrailing(
        lines.map((line) => ({
          ...line,
          blockIndices: line.blockIndices.filter((index) => index !== blockIndex),
        })),
      ),
    )
  }

  const removeBlock = (blockIndex) => {
    commitLines(
      ensureTrailing(
        lines.map((line) => ({
          ...line,
          blockIndices: line.blockIndices.filter((index) => index !== blockIndex),
        })),
      ),
    )
  }

  const removeLine = (lineId) => {
    let next = lines.filter((line) => line.id !== lineId)
    if (next.length === 0) {
      next = [{ id: newLineId(), indent: 0, blockIndices: [] }]
    }
    commitLines(ensureTrailing(next))
  }

  const changeIndent = (lineId, delta) => {
    commitLines(
      lines.map((line) =>
        line.id === lineId
          ? { ...line, indent: Math.max(0, Math.min(8, line.indent + delta)) }
          : line,
      ),
    )
  }

  return (
    <BlockAssemblyLayout
      solution={
        <div className="px-4 py-3" onDragOver={allowDrop}>
          <div className="space-y-1">
            {lines.map((line, lineIndex) => (
            <div
              key={line.id}
              onDragOver={(event) => {
                allowDrop(event)
                setHoverLineId(line.id)
              }}
              onDragLeave={(event) => {
                if (event.currentTarget.contains(event.relatedTarget)) return
                setHoverLineId((current) => (current === line.id ? null : current))
              }}
              onDrop={dropOnLine(line.id)}
              className={[
                "group flex min-h-9 items-center gap-1.5 rounded-lg border border-transparent py-1 pl-1 pr-2 transition",
                hoverLineId === line.id && "border-lime/40 border-dashed bg-lime-soft/20",
              ].join(" ")}
            >
              <div className="w-9 select-none pr-2 text-right font-mono text-[12.5px] text-ink-faint">
                {lineIndex + 1}
              </div>

              {line.indent > 0 ? (
                <span className="whitespace-pre font-mono text-ink-faint/40 select-none" aria-hidden>
                  {"    ".repeat(line.indent)}
                </span>
              ) : null}

              {line.blockIndices.map((blockIndex) => {
                const displayText = formatBlockDisplayText(blocks[blockIndex] ?? "")
                const multiline = displayText.includes("\n")
                return (
                <span
                  key={`${line.id}-${blockIndex}`}
                  draggable
                  onDragStart={(event) => {
                    event.stopPropagation()
                    onDragStart(event, blockIndex)
                  }}
                  onClick={() => removeBlock(blockIndex)}
                  title="Клик — вернуть в банк"
                  className={[
                    "cursor-grab select-none rounded-md border border-[rgba(142,255,1,.4)] bg-bg-2 px-3 py-1.5 font-mono text-[13px] text-ink transition hover:border-danger/55 hover:bg-danger-soft hover:text-danger active:cursor-grabbing",
                    multiline
                      ? "inline-block align-top whitespace-pre-wrap"
                      : "inline-flex items-center whitespace-pre",
                  ].join(" ")}
                >
                  {displayText}
                </span>
                )
              })}

              <div className="ml-auto flex items-center gap-1 opacity-0 transition group-hover:opacity-100">
                <LineIconButton
                  onClick={() => changeIndent(line.id, -1)}
                  title="Уменьшить отступ"
                  disabled={line.indent === 0}
                  tone="lime"
                >
                  <IconChevL />
                </LineIconButton>
                <LineIconButton
                  onClick={() => changeIndent(line.id, 1)}
                  title="Увеличить отступ"
                  disabled={line.indent >= 8}
                >
                  <IconChevR />
                </LineIconButton>
                <LineIconButton
                  onClick={() => removeLine(line.id)}
                  title="Удалить строку"
                  tone="danger"
                  disabled={lines.length === 1 && line.blockIndices.length === 0}
                >
                  <IconX />
                </LineIconButton>
              </div>
            </div>
            ))}
          </div>
        </div>
      }
      bank={{
        blocks,
        blockIndices: bankBlocks,
        title: "Банк блоков",
        hint: "· перетащи в любую строку",
        onDragStart,
        onDragOver: allowDrop,
        onDrop: dropOnBank,
      }}
    />
  )
}
