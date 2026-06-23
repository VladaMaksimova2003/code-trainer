import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"

describe("TasksPage data loading", () => {
  it("uses useTaskOverview instead of useTasks", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/pages/Student/TasksPage.tsx"),
      "utf8",
    )
    expect(source).toContain("useTaskOverview")
    expect(source).not.toMatch(/useTasks\s*\(/)
  })
})

describe("tasksClient", () => {
  it("loads overview endpoint for list requests", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/shared/api/tasksClient.ts"),
      "utf8",
    )
    expect(source).toContain("/tasks/overview")
    expect(source).toContain("TASK_OVERVIEW_STALE_MS")
  })
})
