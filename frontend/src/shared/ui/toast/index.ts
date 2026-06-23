import { dismissToast, pushToast } from "./toastStore"

export { default as ToastStack } from "./ToastStack"

export const toast = {
  push: pushToast,
  dismiss: dismissToast,
  success(title: string, body?: string | null) {
    return pushToast({ kind: "lime", title, body })
  },
  error(title: string, body?: string | null) {
    return pushToast({ kind: "err", title, body, duration: 6000 })
  },
  info(title: string, body?: string | null) {
    return pushToast({ kind: "info", title, body })
  },
  warn(title: string, body?: string | null) {
    return pushToast({ kind: "warn", title, body })
  },
}
