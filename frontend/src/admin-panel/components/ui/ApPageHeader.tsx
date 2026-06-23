export default function ApPageHeader({ title, subtitle, actions }) {
  return (
    <div className="ap-page-h">
      <div>
        <h1>{title}</h1>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      {actions ? <div className="ap-page-actions">{actions}</div> : null}
    </div>
  )
}
