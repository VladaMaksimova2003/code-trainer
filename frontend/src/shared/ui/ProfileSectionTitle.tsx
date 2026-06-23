import type { ReactNode } from "react"

interface ProfileSectionTitleProps {
  children: ReactNode
  className?: string
}

export default function ProfileSectionTitle({ children, className = "" }: ProfileSectionTitleProps) {
  return <b className={`profile-section-title${className ? ` ${className}` : ""}`}>{children}</b>
}
