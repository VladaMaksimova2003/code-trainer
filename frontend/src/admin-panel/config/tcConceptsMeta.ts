/** Display TC cards in tc_display_registry.json (keep in sync when the registry grows). */
export const TC_DISPLAY_CARD_COUNT = 29

export const TC_DISPLAY_LANGUAGE_COUNT = 5

export function formatRussianConstructionCount(count: number): string {
  const n = Math.abs(Math.trunc(count))
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod100 >= 11 && mod100 <= 14) {
    return `${n} конструкций`
  }
  if (mod10 === 1) {
    return `${n} конструкция`
  }
  if (mod10 >= 2 && mod10 <= 4) {
    return `${n} конструкции`
  }
  return `${n} конструкций`
}

export function buildTcConceptsSubtitle(count = TC_DISPLAY_CARD_COUNT): string {
  return `${formatRussianConstructionCount(count)} · примеры на ${TC_DISPLAY_LANGUAGE_COUNT} языках`
}
