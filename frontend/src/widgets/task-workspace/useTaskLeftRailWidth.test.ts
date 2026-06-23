import { describe, expect, it } from "vitest"
import {
  TASK_LEFT_RAIL_DEFAULT_WIDTH,
  TASK_LEFT_RAIL_MAX_WIDTH,
  TASK_LEFT_RAIL_MIN_WIDTH,
  clampTaskLeftRailWidth,
  getTaskLeftRailMaxWidth,
} from "@/widgets/task-workspace/useTaskLeftRailWidth"

describe("task left rail width", () => {
  it("clamps to min and max", () => {
    expect(clampTaskLeftRailWidth(100, 1600)).toBe(TASK_LEFT_RAIL_MIN_WIDTH)
    expect(clampTaskLeftRailWidth(900, 1600)).toBe(TASK_LEFT_RAIL_MAX_WIDTH)
    expect(clampTaskLeftRailWidth(TASK_LEFT_RAIL_DEFAULT_WIDTH, 1600)).toBe(
      TASK_LEFT_RAIL_DEFAULT_WIDTH,
    )
  })

  it("limits max width on narrow viewports", () => {
    expect(getTaskLeftRailMaxWidth(900)).toBeLessThan(TASK_LEFT_RAIL_MAX_WIDTH)
    expect(clampTaskLeftRailWidth(500, 900)).toBe(getTaskLeftRailMaxWidth(900))
  })
})
