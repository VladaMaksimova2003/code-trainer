import type { ComponentPropsWithoutRef, ElementType } from "react"
import { cn } from "@/shared/ui/cn"

interface CardProps extends ComponentPropsWithoutRef<"div"> {
  as?: ElementType
  padded?: boolean
  interactive?: boolean
}

export default function Card({
  as: Component = "div",
  className,
  padded = true,
  interactive = false,
  ...props
}: CardProps) {
  return (
    <Component
      className={cn(
        "rounded-lg border border-border bg-surface shadow-card",
        padded && "p-[22px]",
        interactive && "transition duration-150 ease-out hover:-translate-y-0.5 hover:border-lime/70 hover:shadow-glow-lime",
        className,
      )}
      {...props}
    />
  )
}
