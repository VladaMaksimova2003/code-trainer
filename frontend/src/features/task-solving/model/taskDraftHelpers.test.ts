import { describe, expect, it, beforeEach } from "vitest"
import {
  TASK_DRAFT_STORAGE_PREFIX,
  buildDraftPayload,
  getDraftStorageKey,
  getTaskDraftSignature,
  mergeDraft,
  readDraft,
  resolveDraftForTask,
  writeDraft,
} from "@/features/task-solving/model/taskDraftHelpers"

function createMemoryStorage() {
  const store = new Map()
  return {
    getItem: (key) => store.get(key) ?? null,
    setItem: (key, value) => {
      store.set(key, value)
    },
  }
}

describe("getDraftStorageKey", () => {
  it("uses task-draft prefix unchanged", () => {
    expect(getDraftStorageKey(42)).toBe(`${TASK_DRAFT_STORAGE_PREFIX}42`)
  })
})

describe("resolveDraftForTask", () => {
  const task = {
    id: 1,
    type: "algorithm",
    template: "",
    blocks: [],
    language: "python",
  }

  it("returns draft when signature matches", () => {
    const draft = { taskSignature: getTaskDraftSignature(task), code: "x = 1" }
    expect(resolveDraftForTask(draft, task)).toEqual(draft)
  })

  it("returns null when signature mismatches (task shape changed)", () => {
    const draft = { taskSignature: "old", code: "stale" }
    expect(resolveDraftForTask(draft, task)).toBeNull()
  })

  it("returns null when stored draft is missing", () => {
    expect(resolveDraftForTask(null, task)).toBeNull()
  })
})

describe("readDraft / writeDraft / mergeDraft", () => {
  let storage

  beforeEach(() => {
    storage = createMemoryStorage()
  })

  it("round-trips draft payload", () => {
    const task = { id: 5, type: "algorithm", blocks: [], language: "python" }
    const payload = buildDraftPayload(task, { code: "print(1)", activeTab: "task" })
    writeDraft(5, payload, storage)
    expect(readDraft(5, storage)).toEqual(payload)
  })

  it("mergeDraft preserves existing fields", () => {
    writeDraft(5, { code: "a", bottomTab: "case" }, storage)
    mergeDraft(5, { code: "b" }, storage)
    expect(readDraft(5, storage)).toEqual({ code: "b", bottomTab: "case" })
  })

  it("returns null for missing task id", () => {
    expect(readDraft("", storage)).toBeNull()
  })
})

describe("getTaskDraftSignature", () => {
  it("includes stable task identity fields", () => {
    const sig = getTaskDraftSignature({ id: 1, type: "blocks", blocks: [], language: "python" })
    expect(sig).toContain('"id":1')
    expect(sig).toContain('"type":"blocks"')
  })
})
