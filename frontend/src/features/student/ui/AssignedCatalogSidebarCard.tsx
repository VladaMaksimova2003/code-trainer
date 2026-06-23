import Badge from "@/shared/ui/Badge"
import {
  deadlineUrgencyStyle,
  formatSetDeadline,
} from "@/features/student/utils/deadlineView"
import type { AssignedCatalogCardModel } from "@/features/curriculum/components/AssignedCatalogCard"

interface AssignedCatalogSidebarCardProps {
  catalog: AssignedCatalogCardModel
  onOpen: () => void
}

export default function AssignedCatalogSidebarCard({
  catalog,
  onOpen,
}: AssignedCatalogSidebarCardProps) {
  const total = Math.max(catalog.total_tasks, 1)
  const pct = Math.round((catalog.solved_count / total) * 100)
  const deadlineLabel = formatSetDeadline(catalog.deadline_at)
  const deadlineStyle = deadlineUrgencyStyle(catalog.deadline_at)

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
        <b style={{ fontSize: 13.5 }}>{catalog.catalog_title}</b>
        <Badge kind="lime">
          {catalog.solved_count}/{catalog.total_tasks}
        </Badge>
      </div>
      <p className="mut3" style={{ fontSize: 12, margin: "6px 0 0" }}>
        {catalog.group_name}
      </p>
      {deadlineLabel ? (
        <p className="mono" style={{ fontSize: 12, margin: "8px 0 0", ...deadlineStyle }}>
          {deadlineLabel}
        </p>
      ) : null}
      <div className="progress" style={{ marginTop: deadlineLabel ? 8 : 10 }}>
        <i style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
