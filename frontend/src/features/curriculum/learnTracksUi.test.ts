import { describe, expect, it } from "vitest"

import { PLATFORM_COURSE } from "./platformCourse"
import { buildLearnCourses, filterLearnCourses, isPlatformCurriculumChapter, learnCourseFootnote } from "./learnTracksUi"
import type { CurriculumCollectionsDto } from "@/shared/types/curriculum"

function makeCollection(
  language: string,
  chapterKey: string,
  title: string,
  total: number,
  passed = 0,
): NonNullable<CurriculumCollectionsDto["collections"]>[number] {
  return {
    collection_id: `${language}_${chapterKey}_v311`,
    language,
    chapter_key: chapterKey,
    learning_concept_id: chapterKey,
    title_ru: title,
    description_ru: "Описание главы.",
    route_path: `/learn/${language}/algo-basics`,
    progress: {
      total_tasks: total,
      passed_tasks: passed,
      progress_percent: total ? (passed / total) * 100 : 0,
      catalog_tasks: total,
    },
    completed: false,
    button_label: "Продолжить",
    next_task: null,
  }
}

describe("buildLearnCourses", () => {
  it("returns one platform course with five languages and python entry route", () => {
    const data: CurriculumCollectionsDto = {
      languages: [
        {
          language: "python",
          language_label: "Python",
          available: true,
          progress: { total_tasks: 8, passed_tasks: 2, progress_percent: 25, catalog_tasks: 8 },
          collections: [makeCollection("python", "algo_basics", "1. Базовый синтаксис", 8, 2)],
        },
      ],
      collections: [
        makeCollection("pascal", "algo_basics", "1. Базовый синтаксис", 8),
        makeCollection("python", "algo_basics", "1. Базовый синтаксис", 8, 2),
        makeCollection("cpp", "algo_basics", "1. Базовый синтаксис", 0),
        makeCollection("csharp", "algo_basics", "1. Базовый синтаксис", 0),
        makeCollection("java", "algo_basics", "1. Базовый синтаксис", 0),
      ],
    }

    const courses = buildLearnCourses(data, {
      guestMode: false,
      author: { name: "Анна Преподаватель", profilePath: "/users/42" },
    })

    expect(courses).toHaveLength(1)
    expect(courses[0]).toMatchObject({
      id: PLATFORM_COURSE.id,
      title: PLATFORM_COURSE.title,
      hubRoute: "/learn/python",
      preferredLanguage: "python",
      author: "Анна Преподаватель",
      authorProfilePath: "/users/42",
    })
    expect(courses[0].languages).toHaveLength(5)
    expect(courses[0].languages.filter((lang) => lang.available)).toHaveLength(2)
    expect(courses[0].passedTasks).toBe(2)
  })

  it("filters courses by language and author", () => {
    const courses = buildLearnCourses({
      languages: [{ language: "python", available: true, progress: { total_tasks: 1, passed_tasks: 0, progress_percent: 0 } }],
      collections: [makeCollection("python", "algo_basics", "1. Базовый синтаксис", 8)],
    })

    expect(filterLearnCourses(courses, "python")).toHaveLength(1)
    expect(filterLearnCourses(courses, "алгоритм")).toHaveLength(1)
    expect(filterLearnCourses(courses, "ветв")).toHaveLength(0)
    expect(learnCourseFootnote(courses[0])).toContain("5 языков")
  })

  it("uses platform course author from curriculum payload", () => {
    const data: CurriculumCollectionsDto = {
      platform_course: {
        title: "Базовый синтаксис через алгоритмы",
        author_user_id: 7,
        author_name: "Анна Преподаватель",
      },
      languages: [],
      collections: [],
    }

    const courses = buildLearnCourses(data)

    expect(courses[0]).toMatchObject({
      author: "Анна Преподаватель",
      authorProfilePath: "/users/7",
    })
  })

  it("returns fallback platform course when curriculum payload is empty", () => {
    const courses = buildLearnCourses(null)
    expect(courses).toHaveLength(1)
    expect(courses[0].title).toBe(PLATFORM_COURSE.title)
    expect(courses[0].totalTasks).toBe(128)
  })
})

describe("isPlatformCurriculumChapter", () => {
  it("skips meta and custom rows", () => {
    expect(
      isPlatformCurriculumChapter({
        collection_id: "__teacher_courses__1__",
        language: "",
        chapter_key: "__teacher_courses__1__",
      } as never),
    ).toBe(false)
    expect(
      isPlatformCurriculumChapter(makeCollection("python", "algo_basics", "1. Базовый синтаксис", 8)),
    ).toBe(true)
  })
})
