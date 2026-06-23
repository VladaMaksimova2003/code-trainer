import type { CSSProperties } from "react"
import { resolveAvatar } from "@/shared/utils/avatar"
import type { UserLike } from "@/shared/types/user"

const SIZE = {
  xs: { className: "avatar xs", style: {} as CSSProperties },
  sm: { className: "avatar sm", style: {} as CSSProperties },
  md: { className: "avatar", style: {} as CSSProperties },
  lg: { className: "avatar lg", style: {} as CSSProperties },
}

type AvatarSize = keyof typeof SIZE
type AvatarRole = "student" | "teacher" | "admin"

interface RoleAvatarProps {
  user?: UserLike | null
  name?: string | null
  role?: AvatarRole
  size?: AvatarSize
  className?: string
  style?: CSSProperties
}

export default function RoleAvatar({
  user,
  name,
  role = "student",
  size = "md",
  className = "",
  style = {},
}: RoleAvatarProps) {
  const { initial, color } = resolveAvatar(user, name, role)
  const sizeDef = SIZE[size] || SIZE.md
  return (
    <span
      className={`${sizeDef.className} avatar-role-${role}${className ? ` ${className}` : ""}`}
      style={{ background: color, ...sizeDef.style, ...style }}
      aria-hidden="true"
    >
      {initial}
    </span>
  )
}
