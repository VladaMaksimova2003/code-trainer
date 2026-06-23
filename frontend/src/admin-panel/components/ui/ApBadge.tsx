const KIND_CLASS = {
  lime: "ap-badge-lime",
  purple: "ap-badge-purple",
  muted: "ap-badge-muted",
  danger: "ap-badge-danger",
  warn: "ap-badge-warn",
}

export default function ApBadge({ kind = "muted", children, dot = false }) {
  return (
    <span className={`ap-badge ${KIND_CLASS[kind] || KIND_CLASS.muted}`}>
      {dot ? <span className="ap-dot" /> : null}
      {children}
    </span>
  )
}

export function ApRoleBadge({ role }) {
  const normalized = String(role || "").toUpperCase()
  const map = {
    STUDENT: { kind: "lime", label: "Студент" },
    TEACHER: { kind: "purple", label: "Преподаватель" },
    ADMIN: { kind: "warn", label: "Админ" },
    student: { kind: "lime", label: "Студент" },
    teacher: { kind: "purple", label: "Преподаватель" },
    admin: { kind: "warn", label: "Админ" },
  }
  const item = map[normalized] || map[normalized.toLowerCase()] || { kind: "muted", label: role }
  return <ApBadge kind={item.kind}>{item.label}</ApBadge>
}
