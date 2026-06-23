import Badge from "@/shared/ui/Badge"

const LABELS: Record<string, string> = {
  easy: "Лёгкая",
  medium: "Средняя",
  hard: "Сложная",
}

const KIND: Record<string, "muted" | "warn" | "danger"> = {
  easy: "muted",
  medium: "warn",
  hard: "danger",
  лёгкая: "muted",
  средняя: "warn",
  сложная: "danger",
}

interface DiffBadgeProps {
  diff?: string | null
}

export default function DiffBadge({ diff }: DiffBadgeProps) {
  const raw = String(diff || "")
  const key = raw.toLowerCase()
  const label = LABELS[key] || raw || "—"
  const kindKey = label.toLowerCase()
  return (
    <Badge kind={KIND[key] || KIND[kindKey] || "muted"}>{label}</Badge>
  )
}
