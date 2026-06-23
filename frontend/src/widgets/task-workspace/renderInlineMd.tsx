import type { ReactNode } from "react"

export function renderInlineMd(text: unknown): ReactNode[] {
  const parts = String(text ?? "").split(/(`[^`]+`)/g)
  return parts.map((part, index) =>
    part.startsWith("`") && part.endsWith("`") ? (
      <code
        key={index}
        className="font-mono text-[12.5px] bg-surface-2 text-lime border border-border px-1.5 py-0.5 rounded-md"
      >
        {part.slice(1, -1)}
      </code>
    ) : (
      <span key={index}>{part}</span>
    ),
  )
}
