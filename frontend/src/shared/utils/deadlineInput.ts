export function combineDateAndTime(datePart: string | null | undefined, timePart: string | null | undefined): string | null {
  if (!datePart?.trim()) return null
  const time = timePart?.trim() || "23:59"
  const local = new Date(`${datePart}T${time}:00`)
  if (Number.isNaN(local.getTime())) return null
  return local.toISOString()
}

export function splitIsoToDateTimeParts(iso: string | null | undefined): { date: string; time: string } {
  if (!iso) return { date: "", time: "" }
  try {
    const d = new Date(iso)
    const pad = (n: number) => String(n).padStart(2, "0")
    const date = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
    const time = `${pad(d.getHours())}:${pad(d.getMinutes())}`
    return { date, time }
  } catch {
    return { date: "", time: "" }
  }
}
