import { STATUS_LABELS } from "../api/supportApi"

const MAP: Record<string, string> = {
  open: "bg-lime-soft text-lime",
  in_progress: "bg-purple-soft text-purple",
  resolved: "bg-surface-2 text-ink-muted border border-border",
  closed: "bg-surface-2 text-ink-faint border border-border",
}

interface StatusPillProps {
  status: string
}

export default function StatusPill({ status }: StatusPillProps) {
  return (
    <span
      className={
        "inline-flex items-center gap-1.5 rounded-full px-2.5 h-6 text-[12px] font-semibold " +
        (MAP[status] || MAP.open)
      }
    >
      <i className="h-1.5 w-1.5 rounded-full bg-current" />
      {STATUS_LABELS[status as keyof typeof STATUS_LABELS] || status}
    </span>
  )
}
