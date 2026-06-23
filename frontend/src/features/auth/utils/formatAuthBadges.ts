/** Task count for auth hero: exact below 100, then 100+, 200+, … */
export function formatTaskCountBadge(count: number | string | null | undefined): string {
  const n = Math.max(0, Number(count) || 0)
  if (n >= 100) {
    const bucket = Math.floor(n / 100) * 100
    return `${bucket}+ задач`
  }
  return `${n} ${tasksWord(n)}`
}

function tasksWord(n: number): string {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return "задача"
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "задачи"
  return "задач"
}

export function formatLanguageCountBadge(count: number | string | null | undefined): string {
  const n = Math.max(0, Number(count) || 0)
  return `${n} ${languagesWord(n)}`
}

function languagesWord(n: number): string {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return "язык"
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "языка"
  return "языков"
}
