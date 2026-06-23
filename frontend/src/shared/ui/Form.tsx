import type { ComponentPropsWithoutRef, ReactNode } from "react"
import { cn } from "@/shared/ui/cn"

interface FieldProps {
  label?: ReactNode
  hint?: ReactNode
  className?: string
  children?: ReactNode
}

export function Field({ label, hint, className, children }: FieldProps) {
  return (
    <label className={cn("block", className)}>
      {label && <span className="tp-label">{label}</span>}
      {children}
      {hint && <span className="mt-1.5 block text-xs text-ink-faint">{hint}</span>}
    </label>
  )
}

export function Input({ className, ...props }: ComponentPropsWithoutRef<"input">) {
  return <input className={cn("tp-input", className)} {...props} />
}

export function Select({ className, ...props }: ComponentPropsWithoutRef<"select">) {
  return <select className={cn("tp-select", className)} {...props} />
}

export function Textarea({ className, ...props }: ComponentPropsWithoutRef<"textarea">) {
  return <textarea className={cn("tp-input min-h-24 resize-y font-mono text-[13px]", className)} {...props} />
}
