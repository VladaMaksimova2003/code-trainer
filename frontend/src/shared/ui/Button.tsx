import type { ComponentPropsWithoutRef, ElementType, ReactNode } from "react"
import { Link } from "react-router-dom"
import { cn } from "@/shared/ui/cn"

const variants = {
  primary:
    "border-transparent bg-lime text-bg shadow-[0_6px_22px_-10px_rgba(142,255,1,.45)] hover:bg-lime-600 hover:shadow-glow-lime disabled:hover:shadow-none",
  secondary:
    "border-purple/40 bg-purple/15 text-[#cbb6ff] hover:bg-purple hover:text-white hover:shadow-glow-purple",
  ghost:
    "border-border-strong bg-transparent text-ink-muted hover:border-lime hover:bg-surface hover:text-ink",
  danger:
    "border-danger/40 bg-danger/15 text-[#ff8198] hover:bg-danger hover:text-white",
}

const sizes = {
  sm: "h-8 px-3 text-[13px]",
  md: "h-[42px] px-4 text-sm",
  icon: "h-[42px] w-[42px] justify-center p-0 text-sm",
}

type ButtonVariant = keyof typeof variants
type ButtonSize = keyof typeof sizes

interface ButtonProps extends Omit<ComponentPropsWithoutRef<"button">, "children"> {
  as?: ElementType
  to?: string
  variant?: ButtonVariant
  size?: ButtonSize
  className?: string
  children?: ReactNode
}

export default function Button({
  as: Component = "button",
  to,
  variant = "primary",
  size = "md",
  className,
  type,
  children,
  ...props
}: ButtonProps) {
  const Root = to ? Link : Component

  return (
    <Root
      to={to}
      type={Root === "button" ? type || "button" : type}
      className={cn(
        "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md border font-semibold leading-none transition duration-150 ease-out hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0",
        variants[variant] || variants.primary,
        sizes[size] || sizes.md,
        className,
      )}
      {...props}
    >
      {children}
    </Root>
  )
}
