import { FormEvent, useState } from "react"

import { joinGroupByCode } from "@/features/groups/api/groupsApi"
import { toast } from "@/shared/ui/toast"
import type { GroupDto } from "@/shared/types/groups"

interface StudentGroupInviteCardProps {
  onJoined?: (group: GroupDto) => void | Promise<void>
}

export default function StudentGroupInviteCard({ onJoined }: StudentGroupInviteCardProps) {
  const [inviteCode, setInviteCode] = useState("")
  const [joining, setJoining] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const trimmed = inviteCode.trim()
    if (!trimmed) return

    setJoining(true)
    setError(null)
    try {
      const group = await joinGroupByCode(trimmed)
      setInviteCode("")
      toast.push({
        kind: "lime",
        title: "Вы вступили в группу",
        body: group.name,
      })
      await onJoined?.(group)
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (err as Error)?.message ||
        "Не удалось вступить в группу"
      setError(String(message))
    } finally {
      setJoining(false)
    }
  }

  return (
    <form
      onSubmit={(event) => void handleSubmit(event)}
      style={{
        border: "1px dashed var(--border-2)",
        background: "transparent",
        borderRadius: 12,
        padding: 13,
      }}
    >
      <p className="muted" style={{ fontSize: 12.5, margin: "0 0 10px", lineHeight: 1.45 }}>
        Введите инвайт-код от преподавателя, чтобы получить назначенные задачи.
      </p>
      <input
        className="input mono"
        placeholder="GRP-XXXX"
        value={inviteCode}
        onChange={(event) => {
          setInviteCode(event.target.value.toUpperCase())
          if (error) setError(null)
        }}
        aria-label="Инвайт-код группы"
        autoComplete="off"
        spellCheck={false}
        disabled={joining}
      />
      {error ? (
        <p className="mut3" style={{ fontSize: 12, margin: "8px 0 0", color: "var(--danger)" }}>
          {error}
        </p>
      ) : null}
      <button
        type="submit"
        className="btn btn-primary btn-sm"
        style={{ marginTop: 10, width: "100%" }}
        disabled={joining || !inviteCode.trim()}
      >
        {joining ? "Вступление…" : "Вступить в группу"}
      </button>
    </form>
  )
}
