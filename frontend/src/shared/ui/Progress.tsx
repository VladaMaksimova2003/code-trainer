import { cn } from "@/shared/ui/cn"

interface ProgressProps {
  value?: number
  tone?: "lime" | "purple"
  className?: string
}

export default function Progress({ value = 0, tone = "lime", className }: ProgressProps) {
  const width = `${Math.max(0, Math.min(100, Number(value) || 0))}%`

  return (
    <div className={cn("h-2 overflow-hidden rounded-full bg-surface-3", className)}>
      <div
        className={cn(
          "h-full rounded-full",
          tone === "purple"
            ? "bg-gradient-to-r from-purple to-[#a877ff]"
            : "bg-gradient-to-r from-lime to-lime-600",
        )}
        style={{ width }}
      />
    </div>
  )
}
