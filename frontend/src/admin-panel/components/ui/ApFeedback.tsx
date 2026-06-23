export function ApSpinner() {
  return (
    <div className="ap-spinner-wrap">
      <div className="ap-spinner" aria-label="Загрузка" />
    </div>
  )
}

export function ApAlert({ message, kind = "error" }) {
  if (!message) return null
  return <div className={`ap-alert${kind === "info" ? " info" : ""}`}>{message}</div>
}

export function ApEmptyState({ icon = "∅", title, text, action }) {
  return (
    <div className="ap-empty">
      <div className="ap-empty-ill">{icon}</div>
      <b style={{ fontSize: 16 }}>{title}</b>
      {text ? (
        <p className="ap-muted" style={{ fontSize: 13.5, margin: "8px auto 18px", maxWidth: 320 }}>
          {text}
        </p>
      ) : null}
      {action}
    </div>
  )
}
