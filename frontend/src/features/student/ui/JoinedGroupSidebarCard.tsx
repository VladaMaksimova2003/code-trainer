import Badge from "@/shared/ui/Badge"
import type { StudentJoinedGroupOverviewDto } from "@/shared/types/groups"

interface JoinedGroupSidebarCardProps {
  group: StudentJoinedGroupOverviewDto
  onOpen: () => void
}

export default function JoinedGroupSidebarCard({
  group,
  onOpen,
}: JoinedGroupSidebarCardProps) {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onOpen}
      onKeyDown={(e) => {
        if (e.key === "Enter") onOpen()
      }}
      style={{
        border: "1px solid var(--border)",
        borderRadius: 12,
        padding: 13,
        cursor: "pointer",
        transition: ".12s",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = "var(--lime)"
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "var(--border)"
      }}
    >
      <div className="between">
        <b style={{ fontSize: 13.5 }}>{group.name}</b>
        <Badge kind="purple">Группа</Badge>
      </div>
      <p className="mut3" style={{ fontSize: 12, margin: "6px 0 0" }}>
        {group.teacher?.name ? `Преподаватель: ${group.teacher.name}` : "Вы в группе"}
      </p>
      <p className="muted" style={{ fontSize: 12, margin: "8px 0 0", lineHeight: 1.45 }}>
        Каталоги пока не назначены — ожидайте задания от преподавателя.
      </p>
    </div>
  )
}
