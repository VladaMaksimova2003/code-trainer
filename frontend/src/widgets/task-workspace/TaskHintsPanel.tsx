import { useEffect, useState } from "react"

interface TaskHintsPanelProps {
  hints: string[]
  taskId?: number | string | null
}

function EyeOpenIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      width="15"
      height="15"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M1.5 8s2.5-4.5 6.5-4.5S14.5 8 14.5 8 12 12.5 8 12.5 1.5 8z" />
      <circle cx="8" cy="8" r="2" />
    </svg>
  )
}

function EyeOffIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      width="15"
      height="15"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M2 2l12 12" />
      <path d="M6.2 6.2A2 2 0 0 0 8 12.5a6.5 6.5 0 0 0 6.5-4.5 6.4 6.4 0 0 0-1.2-2.1" />
      <path d="M3.6 4.1A6.4 6.4 0 0 0 1.5 8s2.5 4.5 6.5 4.5c.9 0 1.7-.2 2.5-.5" />
    </svg>
  )
}

export default function TaskHintsPanel({ hints, taskId }: TaskHintsPanelProps) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    setVisible(false)
  }, [taskId])

  if (hints.length === 0) return null

  return (
    <div className="mt-3 w-full rounded-xl border border-[rgba(139,83,254,.35)] bg-purple-soft px-4 py-3">
      <div className={`flex items-center justify-between gap-2${visible ? " mb-2" : ""}`}>
        <div className="text-[10.5px] font-semibold uppercase tracking-[0.08em] text-[#b89bff]">
          Подсказки
        </div>
        <button
          type="button"
          onClick={() => setVisible((current) => !current)}
          className="inline-flex items-center gap-1.5 rounded-md border border-[rgba(139,83,254,.35)] bg-transparent px-2 py-1 text-[11px] font-medium text-[#cbb6ff] hover:bg-[rgba(139,83,254,.12)] transition"
          aria-expanded={visible}
          aria-label={visible ? "Скрыть подсказки" : "Показать подсказки"}
          title={visible ? "Скрыть подсказки" : "Показать подсказки"}
        >
          {visible ? <EyeOffIcon /> : <EyeOpenIcon />}
          <span>{visible ? "Скрыть" : "Показать"}</span>
        </button>
      </div>
      {visible ? (
        <ul className="space-y-2 text-[13px] text-[#cbb6ff] leading-relaxed">
          {hints.map((hint, index) => (
            <li key={`task-hint-${index}`} className="border-l-2 border-purple/45 pl-3">
              {hint}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
