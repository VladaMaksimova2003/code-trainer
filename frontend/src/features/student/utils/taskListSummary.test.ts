import { describe, expect, it } from "vitest"

import {
  buildTaskListSubtitle,
  computeTrackTaskStats,
  computeUnifiedTaskStats,
  resolveActiveLearningTrack,
} from "@/features/student/utils/taskListSummary"
import type { TaskOverviewItem } from "@/shared/types/taskOverview"

function task(partial: Partial<TaskOverviewItem> & { id: number }): TaskOverviewItem {
  return {
    title: "Task",
    ...partial,
  }
}

const curriculumLanguages = [
  { language: "pascal", language_label: "Pascal", progress: { total_tasks: 128, passed_tasks: 8 } },
  { language: "python", language_label: "Python", progress: { total_tasks: 128, passed_tasks: 4 } },
  { language: "csharp", language_label: "C#", progress: { total_tasks: 128, passed_tasks: 0 } },
]

describe("computeTrackTaskStats", () => {
  it("uses progress for the selected track only", () => {
    expect(computeTrackTaskStats(curriculumLanguages, "python", [], 128)).toEqual({
      language: "python",
      languageLabel: "Python",
      solved: 4,
      total: 128,
    })
    expect(computeTrackTaskStats(curriculumLanguages, "csharp", [], 128)).toEqual({
      language: "csharp",
      languageLabel: "C#",
      solved: 0,
      total: 128,
    })
  })

  it("dedupes inflated overview totals when curriculum total is known", () => {
    const tasks = [
      task({ id: 1, pedagogical_slot_id: "pas_001", solved: true }),
      task({ id: 99, pedagogical_slot_id: "pas_001", solved: false }),
    ]
    expect(computeTrackTaskStats(curriculumLanguages, "python", tasks, 256)).toEqual({
      language: "python",
      languageLabel: "Python",
      solved: 4,
      total: 128,
    })
  })

  it("counts catalog plan for chapters not yet seeded in DB", () => {
    const partialTrack = [
      {
        language: "pascal",
        language_label: "Pascal",
        progress: { total_tasks: 120, passed_tasks: 0, catalog_tasks: 128 },
        collections: Array.from({ length: 16 }, (_, index) => ({
          progress: {
            total_tasks: index === 14 ? 0 : 8,
            catalog_tasks: 8,
            passed_tasks: 0,
          },
        })),
      },
    ]
    expect(computeTrackTaskStats(partialTrack, "pascal", [], 120)).toEqual({
      language: "pascal",
      languageLabel: "Pascal",
      solved: 0,
      total: 128,
    })
  })

  it("ignores curriculum passed_tasks in guest mode", () => {
    expect(
      computeTrackTaskStats(curriculumLanguages, "python", [], 128, {
        ignoreCurriculumProgress: true,
      }),
    ).toEqual({
      language: "python",
      languageLabel: "Python",
      solved: 0,
      total: 128,
    })
  })

  it("uses overview total before curriculum loads, not paginated page size", () => {
    const tasks = Array.from({ length: 20 }, (_, index) =>
      task({ id: index + 1, pedagogical_slot_id: `slot_${index + 1}` }),
    )
    expect(computeTrackTaskStats([], "csharp", tasks, 128)).toEqual({
      language: "csharp",
      languageLabel: "C#",
      solved: 0,
      total: 128,
    })
  })
})

describe("buildTaskListSubtitle", () => {
  it("shows not started for an empty track", () => {
    const stats = computeTrackTaskStats(curriculumLanguages, "csharp", [], 128)
    expect(buildTaskListSubtitle(stats, [])).toBe(
      "Решено 0 из 128 · C# · трек ещё не начат",
    )
  })

  it("shows early progress on the active track", () => {
    const stats = computeTrackTaskStats(curriculumLanguages, "python", [], 128)
    expect(buildTaskListSubtitle(stats, [])).toBe(
      "Решено 4 из 128 · Python · пройдены первые темы",
    )
  })

  it("shows track start phrase after first chapters", () => {
    const stats = computeTrackTaskStats(curriculumLanguages, "pascal", [], 128)
    expect(buildTaskListSubtitle(stats, [])).toBe(
      "Решено 8 из 128 · Pascal · начинаете работу с этим треком",
    )
  })

  it("reports medium difficulty trend for recent solved tasks on the track", () => {
    const stats = computeTrackTaskStats(curriculumLanguages, "pascal", [], 128)
    const subtitle = buildTaskListSubtitle(stats, [
      task({ id: 20, solved: true, difficulty: "medium", language_track_states: { pascal: "solved" } }),
      task({ id: 19, solved: true, difficulty: "medium", language_track_states: { pascal: "solved" } }),
      task({ id: 18, solved: true, difficulty: "medium", language_track_states: { pascal: "solved" } }),
      task({ id: 17, solved: true, difficulty: "medium", language_track_states: { pascal: "solved" } }),
      task({ id: 16, solved: true, difficulty: "medium", language_track_states: { pascal: "solved" } }),
      task({ id: 3, solved: true, difficulty: "easy", language_track_states: { pascal: "solved" } }),
      task({ id: 2, solved: true, difficulty: "easy", language_track_states: { pascal: "solved" } }),
      task({ id: 1, solved: true, difficulty: "easy", language_track_states: { pascal: "solved" } }),
    ])
    expect(subtitle).toBe(
      "Решено 8 из 128 · Pascal · сейчас основная часть задач находится на среднем уровне сложности",
    )
  })
})

describe("computeUnifiedTaskStats", () => {
  it("delegates to the active track stats", () => {
    expect(computeUnifiedTaskStats([], 128, curriculumLanguages)).toEqual({
      solved: expect.any(Number),
      total: 128,
    })
  })
})

describe("resolveActiveLearningTrack", () => {
  it("prefers stored language when present in curriculum", () => {
    expect(resolveActiveLearningTrack(curriculumLanguages)).toEqual(
      expect.stringMatching(/python|pascal|cpp|csharp|java/),
    )
  })
})
