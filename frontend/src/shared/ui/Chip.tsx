import type { ComponentPropsWithoutRef, CSSProperties, KeyboardEvent, MouseEvent, ReactNode } from "react"
import { cn } from "@/shared/ui/cn"

type ChipVariant = "default" | "legacy"

interface ChipProps extends Omit<ComponentPropsWithoutRef<"button">, "onClick"> {
  active?: boolean
  tone?: "lime" | "purple"
  /** Legacy `.chip` kit (span + global CSS). Auto when `variant="legacy"`. */
  variant?: ChipVariant
  pp?: boolean
  sm?: boolean
  style?: CSSProperties
  onClick?: (event: MouseEvent<HTMLElement> | KeyboardEvent<HTMLElement>) => void
  children?: ReactNode
}

export default function Chip({
  active = false,
  tone,
  variant,
  pp,
  sm,
  className,
  style,
  onClick,
  children,
  ...props
}: ChipProps) {
  const useLegacy =
    variant === "legacy" ||
    pp !== undefined ||
    sm !== undefined ||
    style !== undefined ||
    (tone === undefined && variant !== "default")

  if (useLegacy) {
    return (
      <span
        role="button"
        tabIndex={0}
        className={`chip ${active ? "on" : ""} ${active && pp ? "pp" : ""} ${sm ? "sm" : ""} ${className ?? ""}`}
        style={style}
        onClick={onClick as ChipProps["onClick"]}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault()
            onClick?.(e)
          }
        }}
      >
        {children}
      </span>
    )
  }

  return (
    <button
      type="button"
      className={cn(
        "tp-chip",
        active && (tone ?? "lime") === "lime" && "border-lime/45 bg-lime/15 text-lime",
        active && tone === "purple" && "border-purple/45 bg-purple/15 text-[#b89bff]",
        className,
      )}
      style={style}
      onClick={onClick as ChipProps["onClick"]}
      {...props}
    >
      {children}
    </button>
  )
}
