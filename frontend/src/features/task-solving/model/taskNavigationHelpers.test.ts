import { describe, expect, it } from "vitest"
import {
  buildAdaptiveNavigateState,
  buildAdaptiveNavigationContext,
  buildTaskRouteState,
  resolveBackLabel,
  resolveBackTarget,
  resolveCurriculumNextAction,
  resolveHasPrev,
  resolveMergedNavigationContext,
  resolveNextTaskAction,
  resolvePrevTaskAction,
  resolveReturnTo,
} from "@/features/task-solving/model/taskNavigationHelpers"

describe("resolveMergedNavigationContext", () => {
  it("prefers location.state over session storage", () => {
    expect(
      resolveMergedNavigationContext(
        { navigationMode: "manual", collectionId: 5 },
        { mode: "adaptive", collectionId: null },
      ),
    ).toEqual({ mode: "manual", collectionId: 5 })
  })

  it("falls back to stored context when location.state is missing", () => {
    expect(
      resolveMergedNavigationContext(undefined, { mode: "curriculum", collectionId: 12 }),
    ).toEqual({ mode: "curriculum", collectionId: 12 })
  })

  it("defaults to adaptive when no context exists", () => {
    expect(resolveMergedNavigationContext(undefined, { mode: "adaptive", collectionId: null })).toEqual({
      mode: "adaptive",
      collectionId: null,
    })
  })
})

describe("back / returnTo helpers", () => {
  it("resolves returnTo from location or curriculum path", () => {
    expect(resolveReturnTo("/learn/pascal", null)).toBe("/learn/pascal")
    expect(resolveReturnTo(null, "/learn/pascal/theme-1")).toBe("/learn/pascal/theme-1")
    expect(resolveReturnTo(null, null)).toBeNull()
  })

  it("back target uses returnTo or home fallback", () => {
    expect(resolveBackTarget("/learn/pascal", "/")).toBe("/learn/pascal")
    expect(resolveBackTarget(null, "/")).toBe("/")
  })

  it("back label reflects returnTo path", () => {
    expect(resolveBackLabel("/learn/pascal")).toBe("К сборнику")
    expect(resolveBackLabel("/groups/1")).toBe("Назад")
    expect(resolveBackLabel(null)).toBe("Каталог")
  })
})

describe("resolvePrevTaskAction", () => {
  const ordered = [10, 11, 12]

  it("uses collectionNav.prev_task_id when present", () => {
    expect(resolvePrevTaskAction({ prev_task_id: 9 }, 1, ordered)).toEqual({
      kind: "task",
      taskId: 9,
      collectionId: null,
    })
  })

  it("uses ordered list when index > 0", () => {
    expect(resolvePrevTaskAction(null, 2, ordered)).toEqual({
      kind: "task",
      taskId: 11,
      collectionId: null,
    })
  })

  it("returns null at first task", () => {
    expect(resolvePrevTaskAction(null, 0, ordered)).toBeNull()
  })

  it("hasPrev when prev_task_id is set even without collection list", () => {
    expect(resolveHasPrev(false, { prev_task_id: 5 }, -1)).toBe(true)
  })
})

describe("resolveNextTaskAction", () => {
  const ordered = [10, 11, 12]

  it("uses collectionNav.next_task_id with next collection", () => {
    expect(
      resolveNextTaskAction({
        collectionNav: { next_task_id: 13, next_collection_id: 7 },
        index: 2,
        orderedTaskIds: ordered,
        hasAdaptiveNext: false,
      }),
    ).toEqual({ kind: "task", taskId: 13, collectionId: 7 })
  })

  it("walks ordered list when no explicit next_task_id", () => {
    expect(
      resolveNextTaskAction({
        collectionNav: null,
        index: 0,
        orderedTaskIds: ordered,
        hasAdaptiveNext: false,
      }),
    ).toEqual({ kind: "task", taskId: 11, collectionId: null })
  })

  it("returns returnTo when course completed", () => {
    expect(
      resolveNextTaskAction({
        collectionNav: { course_completed: true },
        index: 2,
        orderedTaskIds: ordered,
        hasAdaptiveNext: true,
      }),
    ).toEqual({ kind: "returnTo" })
  })

  it("falls back to adaptive when no collection next", () => {
    expect(
      resolveNextTaskAction({
        collectionNav: null,
        index: 2,
        orderedTaskIds: ordered,
        hasAdaptiveNext: true,
      }),
    ).toEqual({ kind: "adaptive" })
  })

  it("falls back to curriculumNext when adaptive unavailable", () => {
    expect(
      resolveNextTaskAction({
        collectionNav: null,
        index: 2,
        orderedTaskIds: ordered,
        hasAdaptiveNext: false,
      }),
    ).toEqual({ kind: "curriculumNext" })
  })
})

describe("resolveCurriculumNextAction", () => {
  it("returns returnTo when curriculum reports completed", () => {
    expect(resolveCurriculumNextAction({ completed: true }, "/learn/pascal")).toEqual({
      kind: "returnTo",
      path: "/learn/pascal",
    })
  })

  it("returns next task with collection id", () => {
    expect(
      resolveCurriculumNextAction(
        {
          next_task: { task_id: 26 },
          collection: { collection_id: 3 },
        },
        "/",
      ),
    ).toEqual({ kind: "task", taskId: 26, collectionId: 3 })
  })

  it("returns null when payload has no next step", () => {
    expect(resolveCurriculumNextAction({}, "/")).toBeNull()
  })
})

describe("buildTaskRouteState", () => {
  it("preserves manual mode and returnTo", () => {
    expect(
      buildTaskRouteState({
        navigationMode: "manual",
        collectionId: 4,
        collectionNavCollectionId: 4,
        returnTo: "/groups",
      }),
    ).toEqual({
      navigationMode: "manual",
      collectionId: 4,
      returnTo: "/groups",
    })
  })

  it("maps curriculum mode and next collection id", () => {
    expect(
      buildTaskRouteState({
        navigationMode: "curriculum",
        collectionId: 2,
        collectionNavCollectionId: 2,
        returnTo: "/learn/pascal",
        nextCollectionId: 5,
      }),
    ).toEqual({
      navigationMode: "curriculum",
      collectionId: 5,
      returnTo: "/learn/pascal",
    })
  })
})

describe("adaptive navigation shapes", () => {
  it("buildAdaptiveNavigateState matches router location.state", () => {
    expect(buildAdaptiveNavigateState()).toEqual({
      navigationMode: "adaptive",
      collectionId: null,
    })
  })

  it("buildAdaptiveNavigationContext matches session storage write shape", () => {
    expect(buildAdaptiveNavigationContext()).toEqual({
      mode: "adaptive",
      collectionId: null,
    })
  })
})
