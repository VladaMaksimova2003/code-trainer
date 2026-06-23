const NAV_SESSION_KEY = "task-navigation-context"

export interface NavigationContext {
  mode: string
  collectionId: number | string | null
}

const DEFAULT_CONTEXT: NavigationContext = { mode: "adaptive", collectionId: null }

export function readNavigationContext(): NavigationContext {
  try {
    const raw = window.sessionStorage.getItem(NAV_SESSION_KEY)
    return raw ? (JSON.parse(raw) as NavigationContext) : { ...DEFAULT_CONTEXT }
  } catch {
    return { ...DEFAULT_CONTEXT }
  }
}

export function writeNavigationContext(context: NavigationContext): void {
  window.sessionStorage.setItem(NAV_SESSION_KEY, JSON.stringify(context))
}
