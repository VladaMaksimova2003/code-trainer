import FlowchartNodeIcon from "@/widgets/BlockEditor/ui/FlowchartNodeIcon"
import { FLOWCHART_BLOCK_ORDER, FLOWCHART_BLOCKS } from "@/widgets/BlockEditor/lib/flowchartBlockConfig"

function TrashIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      width="14"
      height="14"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M3 5h10M6.5 5V3.5h3V5M5 5l.7 8.2a1 1 0 001 .8h2.6a1 1 0 001-.8L11 5" />
    </svg>
  )
}

export default function FlowchartPalette({
  onClear,
  onDeleteSelected,
  hasSelection = false,
  readOnly = false,
}) {
  const onDragStart = (event, blockType) => {
    if (readOnly) return
    event.dataTransfer.setData("flowchart/block-type", blockType)
    event.dataTransfer.effectAllowed = "move"
  }

  return (
    <aside className="flex flex-col gap-2 overflow-y-auto border-r border-border bg-surface p-3">
      <div className="mb-1 px-1 text-[10.5px] font-semibold uppercase tracking-[0.08em] text-ink-faint">
        Перетащи
      </div>

      {FLOWCHART_BLOCK_ORDER.map((blockType) => (
        <div
          key={blockType}
          draggable={!readOnly}
          onDragStart={(event) => onDragStart(event, blockType)}
          className="flex cursor-grab select-none items-center gap-2.5 rounded-lg border border-[#333d4f] bg-surface-2 px-3 py-2 transition hover:border-[#3e4a60] hover:bg-surface-3"
        >
          <FlowchartNodeIcon type={blockType} />
          <span className="text-[12.5px] font-medium text-ink">{FLOWCHART_BLOCKS[blockType].label}</span>
        </div>
      ))}

      {!readOnly ? (
        <div className="mt-auto flex flex-col gap-2">
          <button
            type="button"
            onClick={onDeleteSelected}
            disabled={!hasSelection}
            className="inline-flex h-9 items-center justify-center gap-1.5 rounded-lg border border-[#333d4f] bg-surface-2 text-[12.5px] font-medium text-ink-muted transition hover:border-[#3e4a60] hover:bg-surface-3 hover:text-ink disabled:cursor-not-allowed disabled:opacity-45"
          >
            <TrashIcon />
            Удалить блок
          </button>
          <button
            type="button"
            onClick={onClear}
            className="inline-flex h-9 items-center justify-center gap-1.5 rounded-lg border border-[#333d4f] bg-surface-2 text-[12.5px] font-medium text-ink-muted transition hover:border-danger/40 hover:bg-[rgba(255,77,106,.14)] hover:text-danger"
          >
            <TrashIcon />
            Очистить всё
          </button>
        </div>
      ) : null}
    </aside>
  )
}
