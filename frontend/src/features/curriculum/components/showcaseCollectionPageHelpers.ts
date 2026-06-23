import type { CurriculumShowcaseNextDto, CurriculumShowcaseStudentDto } from "@/shared/types/curriculum"

import { sectionsOf, type SubtopicSectionData } from "./SubtopicSection"

export function firstShowcaseTaskId(sections: SubtopicSectionData[]): number | null {
  for (const section of sections) {
    for (const raw of section.tasks ?? []) {
      const id = Number((raw as { task_id?: number }).task_id)
      if (Number.isFinite(id) && id > 0) return id
    }
  }
  return null
}

export function resolveShowcaseStartTaskId(
  data: CurriculumShowcaseStudentDto | null,
  next: CurriculumShowcaseNextDto | null,
): number | null {
  const fromNext = next?.next_task?.task_id
  if (fromNext) return fromNext
  return firstShowcaseTaskId(data ? sectionsOf(data) : [])
}

export function showcaseStartButtonLabel(
  isGuest: boolean,
  next: CurriculumShowcaseNextDto | null,
): string {
  if (isGuest) return "Начать сборник"
  return next?.button_label ?? "Продолжить сборник"
}
