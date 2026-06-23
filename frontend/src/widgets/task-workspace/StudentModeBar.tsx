import type { ReactNode } from "react"

type EditorMode = "code" | "blocks" | "flow" | string

interface StudentModeBarProps {
  mode: EditorMode
  setMode: (mode: EditorMode) => void
  knownLanguage?: string
  learningLanguage?: string
  showBlocks?: boolean
  showFlow?: boolean
  hasParallel?: boolean
}

function CodeIcon() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M6 4L2 8l4 4M10 4l4 4-4 4" />
    </svg>
  )
}

function BoltIcon() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor" aria-hidden>
      <path d="M9 1 3 9h4l-1 6 6-8H8l1-6z" />
    </svg>
  )
}

function EyeIcon() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M1.5 8s2.5-4.5 6.5-4.5S14.5 8 14.5 8 12 12.5 8 12.5 1.5 8z" />
      <circle cx="8" cy="8" r="2" />
    </svg>
  )
}

export default function StudentModeBar({
  mode,
  setMode,
  showBlocks,
  showFlow,
}: StudentModeBarProps) {
  const modes: { id: EditorMode; label: string; icon: ReactNode; show: boolean }[] = [
    { id: "code", label: "Код", icon: <CodeIcon />, show: true },
    { id: "blocks", label: "Блоки", icon: <BoltIcon />, show: Boolean(showBlocks) },
    { id: "flow", label: "Блок-схема", icon: <EyeIcon />, show: Boolean(showFlow) },
  ].filter((item) => item.show)

  const modesVisible = modes.length
  const isCodeOnly = modesVisible === 1 && modes[0]?.id === "code"
  if (isCodeOnly) return null

  return (
    <div className="px-4 py-2.5 border-b border-border bg-surface/40 flex items-center gap-2 shrink-0">
      <div className="inline-flex items-center gap-0.5 rounded-lg bg-surface p-1 border border-border">
        {modes.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setMode(item.id)}
            className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-[12.5px] font-medium transition ${
              mode === item.id
                ? "bg-surface-3 text-ink"
                : "text-ink-faint hover:text-ink"
            }`}
          >
            {item.icon}
            {item.label}
          </button>
        ))}
      </div>

      <div className="flex-1" />

      <div className="text-[11.5px] text-ink-faint">
        {mode === "code" && <>Редактор</>}
        {mode === "blocks" && <>Собери программу из готовых блоков</>}
        {mode === "flow" && <>Нарисуй алгоритм блок-схемой</>}
      </div>
    </div>
  )
}
