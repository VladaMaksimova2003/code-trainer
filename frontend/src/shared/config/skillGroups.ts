/**
 * Группы навыков профиля — зеркало backend/domain/learning/skill_groups.py
 */

export const CONCEPT_IDS = new Set([
  "function",
  "loop",
  "condition",
  "class",
  "variable",
  "recursion",
  "map",
  "filter",
  "sort",
  "reduce",
  "file_io",
  "exception",
  "import",
  "lambda",
  "comprehension",
  "io",
  "nested_loops",
])

export interface SkillGroup {
  id: string
  label: string
  concepts: string[]
  hint: string
}

export const SKILL_GROUPS: SkillGroup[] = [
  {
    id: "conditions_logic",
    label: "Условия и логика",
    concepts: ["condition", "exception"],
    hint: "Ветвление, проверки и обработка ошибок",
  },
  {
    id: "loops_recursion",
    label: "Циклы и рекурсия",
    concepts: ["loop", "recursion", "nested_loops"],
    hint: "Повторение, обход и рекурсивные алгоритмы",
  },
  {
    id: "functions",
    label: "Функции",
    concepts: ["function", "lambda"],
    hint: "Определение функций и лямбда-выражения",
  },
  {
    id: "collections",
    label: "Работа с коллекциями",
    concepts: ["map", "filter", "reduce", "comprehension"],
    hint: "Преобразование и обход коллекций",
  },
  {
    id: "sorting_data",
    label: "Сортировка и обработка данных",
    concepts: ["sort"],
    hint: "Упорядочивание и подготовка данных",
  },
  {
    id: "variables_basics",
    label: "Переменные и базовые операции",
    concepts: ["variable", "io"],
    hint: "Присваивание, выражения, ввод и вывод",
  },
  {
    id: "file_io",
    label: "Работа с файлами",
    concepts: ["file_io"],
    hint: "Чтение и запись файлов",
  },
  {
    id: "program_structure",
    label: "Структура программы",
    concepts: ["class", "import"],
    hint: "Классы, модули и организация кода",
  },
]

const CONSTRUCTION_TO_CONCEPTS: Record<string, string[]> = {
  for_loop: ["loop"],
  while_loop: ["loop"],
  nested_loops: ["nested_loops"],
  loop: ["loop"],
  foreach: ["loop"],
  recursion: ["recursion"],
  if_statement: ["condition"],
  cond: ["condition"],
  condition: ["condition"],
  exception: ["exception"],
  function_definition: ["function"],
  function_def: ["function"],
  function: ["function"],
  return_statement: ["function"],
  return: ["function"],
  method: ["function"],
  method_call: ["function"],
  direct_call: ["function"],
  chained_call: ["function"],
  call: ["function"],
  lambda: ["lambda"],
  binary_expression: ["variable"],
  identifier: ["variable"],
  arith: ["variable"],
  assign: ["variable"],
  assignment: ["variable"],
  variable: ["variable"],
  io: ["io"],
  map: ["map"],
  filter: ["filter"],
  reduce: ["reduce"],
  comprehension: ["comprehension"],
  sort: ["sort"],
  file_io: ["file_io"],
  class: ["class"],
  import: ["import"],
}

const conceptToGroupIds = new Map<string, string[]>()
for (const group of SKILL_GROUPS) {
  for (const concept of group.concepts) {
    if (!conceptToGroupIds.has(concept)) conceptToGroupIds.set(concept, [])
    conceptToGroupIds.get(concept)!.push(group.id)
  }
}

function conceptsForTag(tag: unknown): string[] {
  const normalized = String(tag || "").toLowerCase().trim()
  if (!normalized) return []
  if (CONCEPT_IDS.has(normalized)) return [normalized]
  return (CONSTRUCTION_TO_CONCEPTS[normalized] || []).filter((id) => CONCEPT_IDS.has(id))
}

/** Task tags → unique concept ids for task requirements. */
export function normalizeConstructionTags(constructions: string[] = []): string[] {
  const seen = new Set<string>()
  const ordered: string[] = []
  for (const raw of constructions) {
    for (const concept of conceptsForTag(raw)) {
      if (!seen.has(concept)) {
        seen.add(concept)
        ordered.push(concept)
      }
    }
  }
  return ordered
}

export function constructionsToConcepts(constructions: string[] = []): Set<string> {
  const concepts = new Set<string>()
  for (const raw of constructions) {
    const tag = String(raw || "").toLowerCase()
    if (!tag) continue
    if (CONCEPT_IDS.has(tag)) {
      concepts.add(tag)
      continue
    }
    for (const concept of CONSTRUCTION_TO_CONCEPTS[tag] || []) {
      concepts.add(concept)
    }
  }
  return concepts
}

export function skillGroupIdsForConstructions(constructions: string[] = []): Set<string> {
  const concepts = constructionsToConcepts(constructions)
  const groupIds = new Set<string>()
  for (const concept of concepts) {
    for (const gid of conceptToGroupIds.get(concept) || []) {
      groupIds.add(gid)
    }
  }
  return groupIds
}

export interface SkillProgressTask {
  id: number | string
  constructions?: string[]
  solved?: boolean
}

export interface SkillProgressEntry {
  id: string
  label: string
  hint: string
  concepts: string[]
  total: number
  solved: number
  percent: number
}

export function buildSkillProgress(tasks: SkillProgressTask[] = []): SkillProgressEntry[] {
  const stats = Object.fromEntries(SKILL_GROUPS.map((g) => [g.id, { total: 0, solved: 0 }]))

  for (const task of tasks) {
    const groupIds = skillGroupIdsForConstructions(task.constructions || [])
    if (!groupIds.size) continue
    const isSolved = Boolean(task.solved)
    for (const gid of groupIds) {
      stats[gid].total += 1
      if (isSolved) stats[gid].solved += 1
    }
  }

  return SKILL_GROUPS.map((group) => {
    const { total, solved } = stats[group.id]
    return {
      id: group.id,
      label: group.label,
      hint: group.hint,
      concepts: [...group.concepts],
      total,
      solved,
      percent: total > 0 ? Math.round((1000 * solved) / total) / 10 : 0,
    }
  })
}
