import type { ComponentPropsWithoutRef, CSSProperties, ReactNode } from "react"
import { cn } from "@/shared/ui/cn"

const tones = {
  lime: "border-lime/30 bg-lime/15 text-lime",
  purple: "border-purple/35 bg-purple/15 text-[#b89bff]",
  muted: "border-border-strong bg-surface-3 text-ink-muted",
  danger: "border-danger/35 bg-danger/15 text-[#ff8198]",
  warning: "border-warning/35 bg-warning/15 text-warning",
}

type BadgeTone = keyof typeof tones

/** Legacy global CSS kit (`kind` prop) — same visual as former `shared/ui/legacy/Badge`. */
const legacyKindClass = {
  lime: "badge-lime",
  purple: "badge-purple",
  muted: "badge-muted",
  danger: "badge-danger",
  warn: "badge-warn",
} as const

type LegacyBadgeKind = keyof typeof legacyKindClass

interface BadgeProps extends ComponentPropsWithoutRef<"span"> {
  /** Tailwind design-system variant (default path). */
  tone?: BadgeTone
  /** Legacy CSS `.badge-*` variant — when set, renders legacy kit (FE-ARCH-4B.5). */
  kind?: LegacyBadgeKind
  dot?: boolean
  children?: ReactNode
  style?: CSSProperties
}

export default function Badge({
  tone = "muted",
  kind,
  dot = false,
  className,
  children,
  style,
  ...props
}: BadgeProps) {
  if (kind != null) {
    return (
      <span
        className={`badge ${legacyKindClass[kind] || legacyKindClass.muted} ${className ?? ""}`}
        style={style}
        {...props}
      >
        {children}
      </span>
    )
  }

  return (
    <span
      className={cn(
        "inline-flex h-6 items-center gap-1.5 rounded-full border px-2.5 text-xs font-semibold leading-none",
        tones[tone] || tones.muted,
        className,
      )}
      style={style}
      {...props}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  )
}

export type { BadgeTone, LegacyBadgeKind }
