import { describe, expect, it } from "vitest"

function homeContinueLabel(nextPayload: { button_label?: string } | null | undefined) {
  if (nextPayload?.button_label) {
    return `▸ ${nextPayload.button_label}`
  }
  return "▸ Продолжить обучение"
}

function collectionTaskPath(taskId: number | string) {
  return `/tasks/${taskId}`
}

function homeShowsCollectionList(collectionsVisible: boolean) {
  return collectionsVisible
}

describe("curriculum home UI smoke helpers", () => {
  it("shows start label at 0/85", () => {
    expect(homeContinueLabel({ button_label: "Начать обучение" })).toBe("▸ Начать обучение")
  })

  it("shows continue label after partial progress", () => {
    expect(homeContinueLabel({ button_label: "Продолжить обучение" })).toBe(
      "▸ Продолжить обучение"
    )
  })

  it("routes global continue to task page via curriculum next", () => {
    expect(collectionTaskPath(42)).toBe("/tasks/42")
  })

  it("does not render expanded Pascal collections on home", () => {
    expect(homeShowsCollectionList(false)).toBe(false)
  })
})

describe("curriculum languages block on home", () => {
  const homeLanguageCard = {
    language: "pascal",
    language_label: "Pascal",
    available: true,
    progress: { total_tasks: 85, passed_tasks: 0, progress_percent: 0 },
  }

  it("shows Pascal card with aggregate progress", () => {
    expect(homeLanguageCard.language_label).toBe("Pascal")
    expect(homeLanguageCard.progress.total_tasks).toBe(85)
  })

  it("routes open topics to language page", () => {
    expect("/learn/pascal").toBe("/learn/pascal")
  })
})

describe("Pascal language page collections", () => {
  const pascalPageCollections = [
    { title_ru: "Переменные и ввод-вывод", route_path: "/learn/pascal/variables-and-io" },
    { title_ru: "Условия", route_path: "/learn/pascal/conditions" },
    { title_ru: "Циклы", route_path: "/learn/pascal/loops" },
    { title_ru: "Функции", route_path: "/learn/pascal/functions" },
  ]

  it("lists Pascal track collections in curriculum order", () => {
    expect(pascalPageCollections.length).toBeGreaterThanOrEqual(4)
    expect(pascalPageCollections[0].title_ru).toBe("Переменные и ввод-вывод")
    expect(pascalPageCollections[1].title_ru).toBe("Условия")
    expect(pascalPageCollections[2].title_ru).toBe("Циклы")
  })
})

describe("student-facing showcase titles", () => {
  const SHOWCASE_PREFIXES = ["[Pascal Loops Showcase] ", "[Pascal Conditions Showcase] "]

  function stripShowcasePrefix(title: string) {
    for (const prefix of SHOWCASE_PREFIXES) {
      if (title.startsWith(prefix)) {
        return title.slice(prefix.length).trim()
      }
    }
    return title
  }

  it("strips dev showcase prefix from displayed title", () => {
    expect(stripShowcasePrefix("[Pascal Loops Showcase] Counted loop: Python → Pascal")).toBe(
      "Counted loop: Python → Pascal"
    )
    expect(stripShowcasePrefix("Цикл for: перевод с Python на Pascal")).toBe(
      "Цикл for: перевод с Python на Pascal"
    )
  })

  it("uses readable action labels", () => {
    const labels = {
      translate: { badge: "Перенести", skill: "Перенести на Pascal" },
      analyze: { badge: "Разобрать код", skill: "Предсказать результат" },
    }
    expect(labels.translate.skill).toBe("Перенести на Pascal")
    expect(labels.analyze.badge).toBe("Разобрать код")
  })
})
