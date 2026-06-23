import type { ReactNode } from "react"
import type { BadgeTone } from "../actionMeta"
import { BADGE_TONE_CLASS } from "../actionMeta"

interface CurriculumBadgeProps {
  tone?: BadgeTone
  children: ReactNode
  className?: string
}

export default function CurriculumBadge({
  tone = "muted",
  children,
  className = "",
}: CurriculumBadgeProps) {
  return (
    <span
      className={
        "inline-flex h-6 items-center gap-1.5 rounded-full border px-2.5 text-[12px] font-semibold " +
        BADGE_TONE_CLASS[tone] +
        " " +
        className
      }
    >
      {children}
    </span>
  )
}
