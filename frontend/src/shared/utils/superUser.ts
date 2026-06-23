import type { UserLike } from "@/shared/types/user"

export const SUPER_USER_EMAIL = "admin@test.com"

export function isSuperUser(user: UserLike | null | undefined): boolean {
  return String(user?.email || "").trim().toLowerCase() === SUPER_USER_EMAIL
}

export function isProtectedSuperUserEmail(email: unknown): boolean {
  return String(email || "").trim().toLowerCase() === SUPER_USER_EMAIL
}
