import { describe, expect, it } from "vitest"

import {
  displayCollectionTotal,
  displayTrackTotal,
  effectiveCollectionTotal,
  progressPercent,
} from "@/features/curriculum/actionMeta"

describe("effectiveCollectionTotal", () => {
  it("returns 0 when only catalog plan exists without seeded tasks", () => {
    expect(effectiveCollectionTotal({ total_tasks: 0, catalog_tasks: 8 })).toBe(0)
  })

  it("caps inflated seeded totals by catalog", () => {
    expect(effectiveCollectionTotal({ total_tasks: 10, catalog_tasks: 8 })).toBe(8)
  })

  it("uses seeded total when within catalog", () => {
    expect(effectiveCollectionTotal({ total_tasks: 5, catalog_tasks: 8 })).toBe(5)
  })
})

describe("displayCollectionTotal", () => {
  it("uses catalog plan when chapter is not seeded yet", () => {
    expect(displayCollectionTotal({ total_tasks: 0, catalog_tasks: 8 })).toBe(8)
  })

  it("falls back to seeded total without catalog", () => {
    expect(displayCollectionTotal({ total_tasks: 5, catalog_tasks: 0 })).toBe(5)
  })
})

describe("displayTrackTotal", () => {
  it("sums chapter catalog plans when track total_tasks is behind catalog", () => {
    expect(
      displayTrackTotal({
        progress: { total_tasks: 120, catalog_tasks: 128 },
        collections: Array.from({ length: 16 }, (_, index) => ({
          progress: {
            total_tasks: index === 14 ? 0 : 8,
            catalog_tasks: 8,
          },
        })),
      }),
    ).toBe(128)
  })
})

describe("progressPercent", () => {
  it("returns 0 for empty collections", () => {
    expect(progressPercent({ total_tasks: 0, catalog_tasks: 8, passed_tasks: 0 })).toBe(0)
  })
})
