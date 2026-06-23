export type ToastKind = "lime" | "err" | "warn" | "info"

export interface ToastItem {
  id: number
  kind: ToastKind
  title: string
  body: string | null
}

type ToastListener = (items: ToastItem[]) => void

let idCounter = 0
const listeners = new Set<ToastListener>()
let toasts: ToastItem[] = []

function emit(): void {
  listeners.forEach((fn) => fn(toasts))
}

export function getToasts(): ToastItem[] {
  return toasts
}

export function subscribe(listener: ToastListener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export interface PushToastOptions {
  kind?: ToastKind
  title?: string
  body?: string | null
  duration?: number
}

export function pushToast({ kind = "lime", title, body = null, duration = 4500 }: PushToastOptions = {}): number | null {
  if (!title) return null
  const id = ++idCounter
  toasts = [...toasts, { id, kind, title, body }]
  emit()
  if (duration > 0) {
    window.setTimeout(() => dismissToast(id), duration)
  }
  return id
}

export function dismissToast(id: number): void {
  toasts = toasts.filter((t) => t.id !== id)
  emit()
}
