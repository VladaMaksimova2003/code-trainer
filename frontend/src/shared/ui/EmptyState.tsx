import type { ReactNode } from "react"

interface EmptyStateProps {
  icon?: ReactNode
  title: ReactNode
  text?: ReactNode
  action?: ReactNode
}

export default function EmptyState({ icon = "⌕", title, text, action }: EmptyStateProps) {
  return (
    <div className="empty">
      <div className="ill">{icon}</div>
      <b style={{ fontSize: 16 }}>{title}</b>
      {text ? (
        <p className="muted" style={{ fontSize: 13.5, margin: "8px auto 18px", maxWidth: 320 }}>
          {text}
        </p>
      ) : null}
      {action}
    </div>
  )
}
