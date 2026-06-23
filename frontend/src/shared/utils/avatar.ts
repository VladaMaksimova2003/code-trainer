import type { UserLike } from "@/shared/types/user"

/** Must stay in sync with backend AvatarService role colors */
export const AVATAR_COLOR_STUDENT = "#8eff01"
export const AVATAR_COLOR_TEACHER = "#8b53fe"
export const AVATAR_COLOR_ADMIN = "#ffb43d"

/** Legacy palette — only used when role is unknown */
export const NEON_AVATAR_COLORS = [
  "#39ff14",
  "#00ffff",
  "#ff00ff",
  "#ff3864",
  "#fcee09",
  "#7df9ff",
  "#ff6ec7",
  "#bf00ff",
  "#0ff0fc",
  "#ff3131",
  "#ccff00",
  "#ff5f1f",
]

export function generateAvatarInitial(name: unknown): string {
  const cleaned = String(name || "").trim()
  if (!cleaned) return "?"
  return cleaned[0].toUpperCase()
}

export function generateAvatarColor(userId: unknown): string {
  const id = Number(userId)
  const safe = Number.isFinite(id) && id >= 0 ? id : 0
  return NEON_AVATAR_COLORS[safe % NEON_AVATAR_COLORS.length]
}

type AvatarRole = "student" | "teacher" | "admin"

function inferRole(user: UserLike | null | undefined, explicitRole: AvatarRole | null): AvatarRole {
  if (explicitRole === "student" || explicitRole === "teacher" || explicitRole === "admin") {
    return explicitRole
  }
  const label = String(user?.role_label || user?.role || "").toLowerCase()
  if (label.includes("admin") || label.includes("админ")) return "admin"
  if (label.includes("teacher") || label.includes("препод")) return "teacher"
  if (label.includes("student") || label.includes("студент")) return "student"
  return explicitRole || "student"
}

export function resolveAvatar(
  user: UserLike | null | undefined,
  displayName: string | null | undefined,
  role: AvatarRole | null = null,
): { initial: string; color: string; role: AvatarRole } {
  const name = displayName || user?.name || user?.display_name || user?.full_name || ""
  const initial = generateAvatarInitial(name) || user?.avatar?.initial || "?"
  const resolvedRole = inferRole(user, role)
  const color =
    resolvedRole === "admin"
      ? AVATAR_COLOR_ADMIN
      : resolvedRole === "teacher"
        ? AVATAR_COLOR_TEACHER
        : AVATAR_COLOR_STUDENT
  return { initial, color, role: resolvedRole }
}
