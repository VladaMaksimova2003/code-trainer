import Badge from "@/shared/ui/Badge"
import {
  deadlineUrgencyStyle,
  formatSetDeadline,
} from "@/features/student/utils/deadlineView"

export interface AssignedCatalogCardModel {
  catalog_id: number
  catalog_title: string
  catalog_description?: string
  group_id: number
  group_name: string
  teacher_name?: string
  deadline_at?: string | null
  solved_count: number
  total_tasks: number
}

interface AssignedCatalogCardProps {
  catalog: AssignedCatalogCardModel
  onOpen: () => void
}

export default function AssignedCatalogCard({ catalog, onOpen }: AssignedCatalogCardProps) {
  const total = Math.max(catalog.total_tasks, 1)
  const pct = Math.round((catalog.solved_count / total) * 100)
  const deadlineLabel = formatSetDeadline(catalog.deadline_at)
  const deadlineStyle = deadlineUrgencyStyle(catalog.deadline_at)

  return (
    <button
      type="button"
      onClick={onOpen}
      className="track-card"
      style={{ textAlign: "left", width: "100%" }}
    >
      <div className="between mb-2">
        <b className="tc-name">{catalog.catalog_title}</b>
        <Badge kind="lime">
          {catalog.solved_count}/{catalog.total_tasks}
        </Badge>
      </div>
      <p className="tc-desc">
        {catalog.group_name}
        {catalog.teacher_name ? ` · ${catalog.teacher_name}` : ""}
      </p>
      {deadlineLabel ? (
        <p className="mono" style={{ fontSize: 12, margin: "0 0 8px", ...deadlineStyle }}>
          {deadlineLabel}
        </p>
      ) : (
        <p className="mut3" style={{ fontSize: 12, margin: "0 0 8px" }}>
          Без дедлайна
        </p>
      )}
      <div className="progress">
        <i style={{ width: `${pct}%` }} />
      </div>
    </button>
  )
}
