/** Max daily count in the period; 0 if no activity. */
export function maxDailyCount(counts: number[]): number {
  let max = 0
  for (const n of counts) {
    if (n > max) max = n
  }
  return max
}

/**
 * Level 0 = no activity; 1–4 = intensity vs max in the same period.
 * Buckets: [1, q), [q, 2q), [2q, 3q), [3q, ∞), q = max / 4.
 */
export function contributionLevelFromCount(count: number, maxDaily: number): number {
  if (count <= 0) return 0
  if (maxDaily <= 0) return 1
  if (maxDaily === 1) return 1

  const q = maxDaily / 4
  if (count < q) return 1
  if (count < 2 * q) return 2
  if (count < 3 * q) return 3
  return 4
}

export const CONTRIB_LEVEL_OPACITY = [0.22, 0.45, 0.72, 1]

export function contribLegendBackground(level: number, { pp = false }: { pp?: boolean } = {}): string {
  if (level <= 0) return "var(--surface-3)"
  const idx = Math.min(level, 4) - 1
  const alpha = CONTRIB_LEVEL_OPACITY[idx]
  return pp ? `rgba(139,83,254,${alpha})` : `rgba(142,255,1,${alpha})`
}
