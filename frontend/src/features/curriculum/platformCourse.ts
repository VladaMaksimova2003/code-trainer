import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"

export const PLATFORM_COURSE = {
  id: "algo-v128",
  title: "Базовый синтаксис через алгоритмы",
  description:
    "16 глав и 128 задач с одним сюжетом на Python, Pascal, C++, C# и Java. Языковые сборники ниже — зеркала одного курса; порядок глав и задач редактируется в любом из них.",
  teacherHint:
    "Перетаскивайте задачи между главами и сборниками — изменения синхронизируются на всех языках.",
  glyph: "Al",
  defaultLanguage: "python" as CurriculumLearningLanguage,
  plannedChapters: 16,
  plannedTasks: 128,
  fallbackAuthor: "Code Trainer",
} as const
