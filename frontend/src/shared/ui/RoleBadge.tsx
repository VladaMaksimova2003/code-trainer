import Badge from "@/shared/ui/Badge"

const MAP: Record<string, { kind: "lime" | "purple" | "warn"; label: string }> = {
  STUDENT: { kind: "lime", label: "Студент" },
  TEACHER: { kind: "purple", label: "Преподаватель" },
  ADMIN: { kind: "warn", label: "Админ" },
  student: { kind: "lime", label: "Студент" },
  teacher: { kind: "purple", label: "Преподаватель" },
  admin: { kind: "warn", label: "Админ" },
}

interface RoleBadgeProps {
  role?: string | null
}

export default function RoleBadge({ role }: RoleBadgeProps) {
  const key = String(role || "STUDENT").toUpperCase()
  const v = MAP[key] || MAP.STUDENT
  return <Badge kind={v.kind}>{v.label}</Badge>
}
