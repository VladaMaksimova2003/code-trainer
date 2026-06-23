import type { ReactNode } from "react"

interface PageHeaderProps {
  title: ReactNode
  subtitle?: ReactNode
  right?: ReactNode[]
}

export default function PageHeader({ title, subtitle, right = [] }: PageHeaderProps) {
  return (
    <div className="page-h">
      <div>
        <h1>{title}</h1>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      {right?.length ? <div className="wrap">{right}</div> : null}
    </div>
  )
}
