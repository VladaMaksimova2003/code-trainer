import { useEffect, useState } from "react"
import { dismissToast, getToasts, subscribe } from "./toastStore"
import type { ToastItem } from "./toastStore"

function kindClass(kind: ToastItem["kind"]): string {
  if (kind === "err") return "err"
  if (kind === "warn") return "warn"
  if (kind === "info") return "info"
  return ""
}

export default function ToastStack() {
  const [items, setItems] = useState(getToasts)

  useEffect(() => subscribe(setItems), [])

  if (items.length === 0) return null

  return (
    <div className="toast-stack" aria-live="polite" aria-relevant="additions">
      {items.map((item) => (
        <div key={item.id} className={`toast ${kindClass(item.kind)}`} role="status">
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="tt">{item.title}</div>
            {item.body ? <div className="tx">{item.body}</div> : null}
          </div>
          <button
            type="button"
            className="btn btn-ghost btn-icon btn-xs"
            aria-label="Закрыть"
            onClick={() => dismissToast(item.id)}
            style={{ flexShrink: 0, marginTop: -2 }}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}
