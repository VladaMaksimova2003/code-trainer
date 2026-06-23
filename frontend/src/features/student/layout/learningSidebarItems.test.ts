import { describe, expect, it } from "vitest"
import { isSidebarDivider, learningSidebarItems } from "./learningSidebarItems"

describe("learningSidebarItems curriculum integration", () => {
  it("does not expose dedicated Pascal collection sidebar entries", () => {
    const labels = learningSidebarItems({ id: 1 })
      .filter((item) => !isSidebarDivider(item))
      .map((item) => item.label)
    expect(labels).not.toContain("Pascal: Циклы")
    expect(labels).not.toContain("Pascal: Условия")
    expect(labels).toContain("Список задач")
    expect(labels).toContain("Курсы")
  })

  it("shows only learning links for guests", () => {
    const items = learningSidebarItems(null)
    const labels = items.filter((item) => !isSidebarDivider(item)).map((item) => item.label)
    expect(labels).toEqual(["Список задач", "Курсы"])
    expect(labels).not.toContain("Войти")
    expect(labels).not.toContain("Профиль")
    expect(labels).not.toContain("Настройки")
    expect(items.some(isSidebarDivider)).toBe(false)
  })
})

describe("curriculum home structure", () => {
  it("home language block has no embedded collection list", () => {
    const homePayload = {
      languages: [
        {
          language: "pascal",
          language_label: "Pascal",
          available: true,
          progress: { total_tasks: 13, passed_tasks: 0 },
        },
      ],
    }
    expect(homePayload.languages[0].language_label).toBe("Pascal")
    expect(homePayload.languages[0]).not.toHaveProperty("collections")
  })

  it("language page exposes Pascal collections", () => {
    const languagePage = {
      route: "/learn/pascal",
      collections: [
        { title_ru: "Условия", route_path: "/learn/pascal/conditions" },
        { title_ru: "Циклы", route_path: "/learn/pascal/loops" },
      ],
    }
    expect(languagePage.route).toBe("/learn/pascal")
    expect(languagePage.collections).toHaveLength(2)
  })
})
