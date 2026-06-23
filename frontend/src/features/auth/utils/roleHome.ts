import type { NormalizedUserRole } from "@/shared/types/user"

/** Default landing route after login by normalized role. */
export function roleHome(role: NormalizedUserRole | string): string {
  if (role === "ADMIN") return "/"
  return "/"
}
