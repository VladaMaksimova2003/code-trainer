export default function ApChip({ active, children, onClick }) {
  return (
    <button type="button" className={`ap-chip${active ? " on" : ""}`} onClick={onClick}>
      {children}
    </button>
  )
}

export function ApProgressBar({ value, max = 100, variant = "purple" }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0
  const variantClass =
    variant === "lime" ? " lime" : variant === "orange" ? " orange" : ""
  return (
    <div className={`ap-progress${variantClass}`}>
      <i style={{ width: `${pct}%` }} />
    </div>
  )
}

export function ApAvatar({
  name,
  role = "student",
  purple,
  size = "sm",
}: {
  name?: string
  role?: "student" | "teacher" | "admin"
  purple?: boolean
  size?: "sm" | "lg"
}) {
  const resolvedRole =
    purple === true ? "teacher" : purple === false ? "student" : role
  const initials = String(name || "?")
    .trim()
    .split(/\s+/)
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()
  const roleClass = resolvedRole === "student" ? "" : ` ${resolvedRole}`
  return (
    <span className={`ap-avatar${roleClass}${size === "lg" ? " lg" : ""}`}>{initials}</span>
  )
}

export function ApFormField({ label, htmlFor, help, error, children }) {
  return (
    <div className="ap-field">
      {label ? (
        <label className="ap-label" htmlFor={htmlFor}>
          {label}
        </label>
      ) : null}
      {children}
      {error ? <p className="ap-help err">{error}</p> : help ? <p className="ap-help">{help}</p> : null}
    </div>
  )
}
