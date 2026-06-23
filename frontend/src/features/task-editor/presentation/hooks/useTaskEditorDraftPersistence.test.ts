import { describe, expect, it, beforeEach, beforeAll } from "vitest"
import {
  clearEditDraftAutosave,
  isMeaningfulEditDraft,
  isPageReload,
  loadEditDraftAutosave,
  saveEditDraftAutosave,
} from "@/features/task-editor/presentation/hooks/useTaskEditorDraftPersistence"
import { createEmptyAssignmentDraft } from "@/features/task-editor/application/use-cases/clearAssignmentDraft"

function mockSessionStorage(): void {
  const store = new Map<string, string>()
  const storage = {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => {
      store.set(key, value)
    },
    removeItem: (key: string) => {
      store.delete(key)
    },
    clear: () => {
      store.clear()
    },
  }
  Object.defineProperty(globalThis, "sessionStorage", {
    value: storage,
    configurable: true,
  })
}

describe("useTaskEditorDraftPersistence storage", () => {
  beforeAll(() => {
    mockSessionStorage()
  })

  beforeEach(() => {
    sessionStorage.clear()
  })

  it("round-trips edit draft in sessionStorage", () => {
    const draft = { ...createEmptyAssignmentDraft(), title: "Edited title" }
    saveEditDraftAutosave("42", draft)
    const loaded = loadEditDraftAutosave("42")
    expect(loaded?.title).toBe("Edited title")
  })

  it("clearEditDraftAutosave removes stored draft", () => {
    saveEditDraftAutosave("42", { ...createEmptyAssignmentDraft(), title: "X" })
    clearEditDraftAutosave("42")
    expect(loadEditDraftAutosave("42")).toBeNull()
  })

  it("isMeaningfulEditDraft rejects empty cached payload", () => {
    saveEditDraftAutosave("42", createEmptyAssignmentDraft())
    expect(loadEditDraftAutosave("42")).toBeNull()
    expect(isMeaningfulEditDraft(createEmptyAssignmentDraft())).toBe(false)
  })

  it("isPageReload returns boolean", () => {
    expect(typeof isPageReload()).toBe("boolean")
  })
})
