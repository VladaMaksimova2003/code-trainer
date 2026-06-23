import { useEffect } from "react"
import {
  getConstructionLabel,
  langDisplay,
} from "@/features/task-solving/model/studentUiUtils"
import { getConstructVariants } from "@/features/task-solving/model/constructionHintsUtils"
import CodeBlockView from "@/widgets/task-workspace/CodeBlockView"
import {
  useDraggablePopover,
  type PopoverAnchorRect,
} from "@/widgets/task-workspace/useDraggablePopover"

interface ConstructPopoverProps {
  pattern?: string | null
  anchorRect?: PopoverAnchorRect | null
  hints?: Record<string, unknown>
  learningLang?: string
  used?: boolean
  onClose?: () => void
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M3 8.5l3.5 3.5L13 5" />
    </svg>
  )
}

function hintRecord(hints: Record<string, unknown>, pattern: string | null | undefined) {
  if (!pattern) return null
  const raw = hints[pattern]
  if (raw == null || typeof raw !== "object") return null
  return raw as { description?: string; [key: string]: unknown }
}

export default function ConstructPopover({
  pattern,
  anchorRect,
  hints = {},
  learningLang,
  used = false,
  onClose,
}: ConstructPopoverProps) {
  const hint = hintRecord(hints, pattern)
  const title = getConstructionLabel(pattern ?? "", hints)
  const popW = 440
  const { pos, onDragStart, maxHeight } = useDraggablePopover({
    anchorRect,
    width: popW,
    enabled: Boolean(pattern && anchorRect),
  })

  useEffect(() => {
    if (!pattern) return undefined
    const onDoc = (event: MouseEvent) => {
      const target = event.target
      if (!(target instanceof Element)) return
      if (
        !target.closest("[data-construct-popover]") &&
        !target.closest("[data-construct-id]")
      ) {
        onClose?.()
      }
    }
    const onEsc = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose?.()
    }
    document.addEventListener("mousedown", onDoc)
    document.addEventListener("keydown", onEsc)
    return () => {
      document.removeEventListener("mousedown", onDoc)
      document.removeEventListener("keydown", onEsc)
    }
  }, [pattern, onClose])

  if (!pattern || !anchorRect || !pos) return null

  const variants = getConstructVariants(hint, learningLang ?? "", title)

  return (
    <div
      data-construct-popover
      className="fixed z-50 pop-in"
      style={{ left: pos.left, top: pos.top, width: popW, maxHeight }}
    >
      <div className="flex max-h-[inherit] flex-col overflow-hidden rounded-xl border border-border bg-surface shadow-[0_30px_60px_-20px_rgba(0,0,0,0.8)]">
        <div
          className="flex shrink-0 cursor-grab select-none items-center gap-2 border-b border-border px-4 py-3 active:cursor-grabbing"
          onMouseDown={onDragStart}
          title="Перетащите, чтобы переместить"
        >
          <div className="text-[15px] font-semibold text-ink">{title}</div>
          <span className="text-ink-faint text-[12px]">·</span>
          <span className="text-[12px] text-lime font-medium">{langDisplay(learningLang ?? "")}</span>
          <div className="flex-1" />
          {used ? (
            <span className="inline-flex items-center gap-1 rounded-md border border-lime/25 bg-lime-soft px-2 py-0.5 text-[11px] font-semibold text-lime">
              <CheckIcon />
              уже используется
            </span>
          ) : (
            <span className="inline-flex items-center rounded-md border border-border bg-surface-2 px-2 py-0.5 text-[11px] font-semibold text-ink-faint">
              не используется
            </span>
          )}
          <button
            type="button"
            onClick={onClose}
            className="h-6 w-6 ml-1 rounded-md text-ink-faint hover:text-ink hover:bg-surface-2 flex items-center justify-center transition cursor-pointer"
            aria-label="Закрыть"
            onMouseDown={(event) => event.stopPropagation()}
          >
            ×
          </button>
        </div>

        {hint?.description && (
          <div className="shrink-0 px-4 pt-3.5 pb-1">
            <p className="text-[13px] text-ink-muted leading-relaxed">{hint.description}</p>
          </div>
        )}

        <div className="min-h-0 flex-1 overflow-y-auto px-4 pb-4 pt-2">
          <div className="text-[10.5px] font-semibold uppercase tracking-[0.1em] text-ink-faint mb-2">
            Примеры на {langDisplay(learningLang ?? "")}
          </div>
          <div className="space-y-2">
            {variants.length > 0 ? (
              variants.map((variant, index) => (
                <div
                  key={`${variant.name}-${index}`}
                  className="overflow-x-auto rounded-lg border border-border bg-bg-2"
                >
                  <div className="px-3 py-1.5 border-b border-border bg-surface-2/40 flex items-center gap-2">
                    <span className="h-1 w-1 rounded-full bg-lime shrink-0" />
                    <span className="text-[12px] font-medium text-ink">{variant.name}</span>
                  </div>
                  <CodeBlockView code={variant.code} language={learningLang ?? "python"} />
                </div>
              ))
            ) : (
              <div className="text-[12.5px] text-ink-faint italic">
                Для языка {langDisplay(learningLang ?? "")} примеров пока нет.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
