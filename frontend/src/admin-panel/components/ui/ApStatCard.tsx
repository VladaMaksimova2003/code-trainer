import ApBadge from "./ApBadge"

export default function ApStatCard({ label, value, badge, badgeKind = "muted" }) {
  return (
    <div className="ap-card ap-card-pad">
      <div className="ap-stat-label">{label}</div>
      <div className="ap-stat-value">{value}</div>
      {badge ? (
        <span style={{ marginTop: 8, display: "inline-flex" }}>
          <ApBadge kind={badgeKind}>{badge}</ApBadge>
        </span>
      ) : null}
    </div>
  )
}
