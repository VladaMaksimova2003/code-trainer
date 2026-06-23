import Badge from "@/shared/ui/Badge"

const META: Record<string, { label: string; kind: "lime" | "purple" | "muted" | "danger" | "warn" }> = {
  solved: { label: "Решено", kind: "lime" },
  attempted: { label: "В процессе", kind: "purple" },
  todo: { label: "Не начато", kind: "muted" },
  accepted: { label: "Решено", kind: "lime" },
  failed: { label: "Ошибка тестов", kind: "danger" },
  reviewing: { label: "На проверке", kind: "warn" },
}

function Dot() {
  return <span className="dotb" />
}

interface StatusBadgeProps {
  status?: string
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const meta = (status && META[status]) || { label: status || "", kind: "muted" as const }
  return (
    <Badge kind={meta.kind}>
      <Dot /> {meta.label}
    </Badge>
  )
}

export { Dot }
