const AUTH_RETURN_PATH_KEY = "auth_return_path"

const BLOCKED_PREFIXES = ["/login", "/register", "/reset-password", "/login/callback"]

export function isSafeReturnPath(path: string | null | undefined): boolean {
  if (!path || typeof path !== "string") return false
  const normalized = path.startsWith("/") ? path : `/${path}`
  return !BLOCKED_PREFIXES.some(
    (prefix) => normalized === prefix || normalized.startsWith(`${prefix}/`) || normalized.startsWith(`${prefix}?`),
  )
}

export function buildReturnPath(pathname: string, search = ""): string {
  return `${pathname || "/"}${search || ""}`
}

export function saveAuthReturnPath(path: string | null | undefined): void {
  if (!isSafeReturnPath(path)) return
  try {
    window.sessionStorage.setItem(AUTH_RETURN_PATH_KEY, String(path))
  } catch {
    /* ignore quota / private mode */
  }
}

export function peekAuthReturnPath(): string | null {
  try {
    const stored = window.sessionStorage.getItem(AUTH_RETURN_PATH_KEY)
    return isSafeReturnPath(stored) ? stored : null
  } catch {
    return null
  }
}

export function consumeAuthReturnPath(): string | null {
  const stored = peekAuthReturnPath()
  try {
    window.sessionStorage.removeItem(AUTH_RETURN_PATH_KEY)
  } catch {
    /* ignore */
  }
  return stored
}

export function resolvePostLoginPath(options: {
  locationStatePath?: string | null
  roleHomePath: string
}): string {
  const fromState =
    options.locationStatePath && isSafeReturnPath(options.locationStatePath)
      ? options.locationStatePath
      : null
  const fromStorage = peekAuthReturnPath()
  const saved = fromState || fromStorage

  if (saved) {
    consumeAuthReturnPath()
    return saved
  }

  return options.roleHomePath || "/"
}
