import { formatBlockDisplayText } from "@/domain/blockAssembly"

const DRAG_TYPE = "application/x-block-reorder-index"

export function BlockAssemblyBank({
  title = "Доступные блоки",
  hint = "· перетащи в пропуск",
  blocks = [],
  blockIndices = [],
  onDragStart,
  onDragOver,
  onDrop,
  emptyText = "Все блоки расставлены.",
  embedded = false,
}) {
  return (
    <div
      className={[
        "bg-bg-2/60 px-4 py-3",
        embedded ? "" : "border-t border-border",
      ].join(" ")}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <div className="mb-2 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.08em] text-ink-faint">
        <span>{title}</span>
        {hint ? (
          <span className="font-normal normal-case tracking-normal text-ink-faint/70">{hint}</span>
        ) : null}
      </div>
      <div className="flex flex-wrap items-start gap-1.5">
        {blockIndices.length === 0 ? (
          <div className="text-[12.5px] italic text-ink-faint">{emptyText}</div>
        ) : (
          blockIndices.map((blockIndex) => {
            const displayText = formatBlockDisplayText(blocks[blockIndex] ?? "")
            const multiline = displayText.includes("\n")
            return (
              <span
                key={blockIndex}
                draggable
                onDragStart={(event) => onDragStart?.(event, blockIndex)}
                className={[
                  "cursor-grab select-none rounded-lg border border-border-2 bg-surface-2 px-3 py-1.5 font-mono text-[13px] text-ink break-words text-left transition hover:border-border-2 hover:bg-surface-3 active:cursor-grabbing",
                  multiline
                    ? "inline-block max-w-[min(100%,28rem)] self-start whitespace-pre-wrap"
                    : "inline-flex max-w-[min(100%,28rem)] self-start whitespace-pre",
                ].join(" ")}
              >
                {displayText}
              </span>
            )
          })
        )}
      </div>
    </div>
  )
}

export { DRAG_TYPE }
