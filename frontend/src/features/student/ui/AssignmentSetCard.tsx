import Badge from "@/shared/ui/Badge"
import {
  deadlineUrgencyStyle,
  formatSetDeadline,
} from "@/features/student/utils/deadlineView"

export default function AssignmentSetCard({ set, onOpen }) {
  const total = Math.max(set.total, 1)
  const pct = Math.round((set.solved / total) * 100)
  const pp = set.color === "purple"
  const deadlineLabel = formatSetDeadline(set.deadlineAt)
  const deadlineStyle = deadlineUrgencyStyle(set.deadlineAt)

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onOpen}
      onKeyDown={(e: unknown) => {
        if (e.key === "Enter") onOpen?.()
      }}
      style={{
        border: "1px solid var(--border)",
        borderRadius: 12,
        padding: 13,
        cursor: "pointer",
        transition: ".12s",
      }}
      onMouseEnter={(e: unknown) => {
        e.currentTarget.style.borderColor = pp ? "var(--purple)" : "var(--lime)"
      }}
      onMouseLeave={(e: unknown) => {
        e.currentTarget.style.borderColor = "var(--border)"
      }}
    >
      <div className="between">
        <b style={{ fontSize: 13.5 }}>{set.name}</b>
        <Badge kind={pp ? "purple" : "lime"}>
          {set.solved}/{set.total}
        </Badge>
      </div>
      {deadlineLabel ? (
        <p
          className="mono"
          style={{
            fontSize: 12,
            margin: "8px 0 0",
            ...deadlineStyle,
          }}
        >
          {deadlineLabel}
        </p>
      ) : null}
      <div className={`progress ${pp ? "pp" : ""}`} style={{ marginTop: deadlineLabel ? 8 : 10 }}>
        <i style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
