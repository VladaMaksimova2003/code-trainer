import { describe, expect, it } from "vitest"

import {
  firstShowcaseTaskId,
  resolveShowcaseStartTaskId,
  showcaseStartButtonLabel,
} from "@/features/curriculum/components/showcaseCollectionPageHelpers"

describe("showcaseCollectionPageHelpers", () => {
  it("picks the first task from sections", () => {
    expect(
      firstShowcaseTaskId([
        { name_ru: "A", tasks: [{ task_id: 10 }, { task_id: 11 }] },
        { name_ru: "B", tasks: [{ task_id: 20 }] },
      ]),
    ).toBe(10)
  })

  it("falls back to section tasks when next is missing", () => {
    expect(
      resolveShowcaseStartTaskId(
        {
          subtopics: [{ name_ru: "A", tasks: [{ task_id: 42, title: "Task" }] }],
          total_tasks: 1,
        },
        null,
      ),
    ).toBe(42)
  })

  it("uses guest start label", () => {
    expect(showcaseStartButtonLabel(true, null)).toBe("Начать сборник")
    expect(showcaseStartButtonLabel(false, { button_label: "Продолжить" })).toBe("Продолжить")
  })
})
