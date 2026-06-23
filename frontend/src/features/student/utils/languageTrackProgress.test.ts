import { describe, expect, it } from "vitest"
import {
  aggregateLanguageTrackStatus,
  buildLanguageMatrix,
} from "@/features/student/utils/languageTrackProgress"

describe("languageTrackProgress", () => {
  it("marks all tracks mastered when every available language is solved", () => {
    const task = {
      id: 4,
      title: "Reverse array",
      available_language_tracks: ["python", "pascal", "cpp", "csharp", "java"],
      language_track_states: {
        python: "solved",
        pascal: "solved",
        cpp: "solved",
        csharp: "solved",
        java: "solved",
      },
    }

    expect(aggregateLanguageTrackStatus(task)).toBe("solved")
    expect(buildLanguageMatrix(task).every((entry) => entry.state === "solved")).toBe(true)
  })

  it("shows attempted when only part of tracks is solved", () => {
    const task = {
      id: 2,
      title: "Linear search",
      available_language_tracks: ["python", "pascal", "cpp", "csharp", "java"],
      language_track_states: {
        python: "solved",
        pascal: "solved",
        cpp: "attempted",
      },
    }

    expect(aggregateLanguageTrackStatus(task)).toBe("attempted")
  })

  it("falls back to global solved for single-track tasks", () => {
    const task = {
      id: 9,
      title: "Hello",
      language: "python",
      solved: true,
      attempted: true,
    }

    const matrix = buildLanguageMatrix(task)
    const python = matrix.find((entry) => entry.id === "python")
    expect(python?.state).toBe("solved")
    expect(aggregateLanguageTrackStatus(task)).toBe("solved")
  })
})
