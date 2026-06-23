import { Link } from "react-router-dom"
import type { ComponentPropsWithoutRef, ReactNode } from "react"
import { userProfilePath } from "@/shared/utils/profileLinks"

interface ProfileLinkProps extends Omit<ComponentPropsWithoutRef<typeof Link>, "to" | "children"> {
  userId?: number | string | null
  teacherId?: number | string | null
  children?: ReactNode
  className?: string
}

export default function ProfileLink({
  userId,
  teacherId = null,
  children,
  className = "t-name",
  onClick,
  ...rest
}: ProfileLinkProps) {
  if (!userId) {
    return <span className={className}>{children}</span>
  }
  return (
    <Link
      to={userProfilePath(userId, { teacherId })}
      className={className}
      onClick={onClick}
      {...rest}
    >
      {children}
    </Link>
  )
}
