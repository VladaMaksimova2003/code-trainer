interface SkillProgressRow {
  id?: number | string
  label?: string
  percent?: number
}

interface SkillsProgressCardProps {
  skills?: SkillProgressRow[]
  title?: string
}

export default function SkillsProgressCard({ skills = [], title = "Навыки" }: SkillsProgressCardProps) {
  if (!skills.length) {
    return (
      <div className="card card-pad profile-skills-card">
        <b className="profile-card-title">{title}</b>
        <p className="mut3" style={{ fontSize: 13, marginTop: 12 }}>
          Пока нет данных по темам.
        </p>
      </div>
    )
  }

  return (
    <div className="card card-pad profile-skills-card">
      <b className="profile-card-title">{title}</b>
      <div style={{ marginTop: 14 }}>
        {skills.map((row, i) => {
          const pp = i % 2 === 1
          const pct = Math.min(100, Math.max(0, Number(row.percent) || 0))
          return (
            <div key={row.id || i} style={{ marginBottom: i < skills.length - 1 ? 16 : 0 }}>
              <div className="between" style={{ fontSize: 13, marginBottom: 6 }}>
                <span className="muted">{row.label}</span>
                <span className="mono" style={{ color: pp ? "#b89bff" : "var(--lime)" }}>
                  {pct}%
                </span>
              </div>
              <div className={`progress ${pp ? "pp" : ""}`}>
                <i style={{ width: `${pct}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
