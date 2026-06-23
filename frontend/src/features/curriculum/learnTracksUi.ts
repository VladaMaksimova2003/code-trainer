import {
  CURRICULUM_LANGUAGE_OPTIONS,
  LANGUAGE_LABELS,
  LANGUAGE_ROUTES,
} from "@/features/curriculum/curriculumLanguageUi"
import { displayCollectionTotal, displayTrackTotal, progressPercent } from "@/features/curriculum/actionMeta"
import { PLATFORM_COURSE } from "@/features/curriculum/platformCourse"
import { deriveLabelGlyph } from "@/shared/utils/labelGlyph"
import type { CurriculumCollectionsDto } from "@/shared/types/curriculum"
import type { CurriculumLearningLanguage } from "@/shared/config/curriculumLanguages"

export interface LearnTrackLanguage {
  id: CurriculumLearningLanguage
  glyph: string
  label: string
  available: boolean
  routePath: string
}

export interface LearnCourse {
  id: string
  title: string
  description: string
  author: string
  authorProfilePath: string | null
  order: number
  languages: LearnTrackLanguage[]
  chapterCount: number
  totalTasks: number
  passedTasks: number
  progressPercent: number
  preferredLanguage: CurriculumLearningLanguage
  hubRoute: string
}

/** @deprecated use LearnCourse */
export type LearnTrack = LearnCourse & { chapterKey?: string }

type CollectionSummary = NonNullable<CurriculumCollectionsDto["collections"]>[number]

/** Skip teacher/catalog meta rows that leak into /curriculum/collections. */
export function isPlatformCurriculumChapter(item: CollectionSummary | null | undefined): boolean {
  if (!item) return false
  const language = String(item.language ?? "").trim()
  if (!language) return false
  const chapterKey = String(item.chapter_key ?? "").trim()
  if (chapterKey.startsWith("__") && chapterKey.endsWith("__")) return false
  const collectionId = String(item.collection_id ?? "")
  if (collectionId.includes("_custom")) return false
  return true
}

function collectionHasContent(item: CollectionSummary): boolean {
  return displayCollectionTotal(item.progress) > 0
}

function buildCourseLanguages(collections: CollectionSummary[]): LearnTrackLanguage[] {
  const chapters = collections.filter(isPlatformCurriculumChapter)
  return CURRICULUM_LANGUAGE_OPTIONS.map((option) => {
    const variants = chapters.filter((item) => item.language === option.id)
    const available = variants.some(collectionHasContent)
    return {
      id: option.id,
      glyph: option.glyph,
      label: option.label,
      available,
      routePath: LANGUAGE_ROUTES[option.id],
    }
  })
}

function countActiveChapters(collections: CollectionSummary[]): number {
  const keys = new Set(
    collections
      .filter(isPlatformCurriculumChapter)
      .filter(collectionHasContent)
      .map((item) => item.chapter_key)
      .filter(Boolean),
  )
  return keys.size
}

function resolveCourseAuthor(
  data: CurriculumCollectionsDto | null | undefined,
  options?: Parameters<typeof buildLearnCourses>[1],
): { name: string; profilePath: string | null } {
  const platformAuthor = data?.platform_course
  const name =
    platformAuthor?.author_name?.trim() ||
    options?.author?.name?.trim() ||
    PLATFORM_COURSE.fallbackAuthor
  const authorUserId = platformAuthor?.author_user_id ?? null
  const profilePath =
    authorUserId != null
      ? `/users/${authorUserId}`
      : options?.author?.profilePath ?? null
  return { name, profilePath }
}

function buildFallbackPlatformCourse(
  options?: Parameters<typeof buildLearnCourses>[1],
  data?: CurriculumCollectionsDto | null,
): LearnCourse {
  const { name: authorName, profilePath: authorProfilePath } = resolveCourseAuthor(data, options)
  const platformMeta = data?.platform_course
  return {
    id: PLATFORM_COURSE.id,
    title: platformMeta?.title?.trim() || PLATFORM_COURSE.title,
    description: platformMeta?.description?.trim() || PLATFORM_COURSE.description,
    author: authorName,
    authorProfilePath,
    order: 0,
    languages: CURRICULUM_LANGUAGE_OPTIONS.map((option) => ({
      id: option.id,
      glyph: option.glyph,
      label: option.label,
      available: true,
      routePath: LANGUAGE_ROUTES[option.id],
    })),
    chapterCount: PLATFORM_COURSE.plannedChapters,
    totalTasks: PLATFORM_COURSE.plannedTasks,
    passedTasks: 0,
    progressPercent: 0,
    preferredLanguage: PLATFORM_COURSE.defaultLanguage,
    hubRoute: LANGUAGE_ROUTES[PLATFORM_COURSE.defaultLanguage],
  }
}

export function buildLearnCourses(
  data: CurriculumCollectionsDto | null | undefined,
  options?: {
    guestMode?: boolean
    author?: { name?: string | null; profilePath?: string | null }
  },
): LearnCourse[] {
  const languagesPayload = Array.isArray(data?.languages) ? data.languages : []
  const collections = Array.isArray(data?.collections)
    ? data.collections.filter(isPlatformCurriculumChapter)
    : []
  if (!languagesPayload.length && !collections.length) {
    return [buildFallbackPlatformCourse(options, data)]
  }

  const guestMode = options?.guestMode ?? false
  const preferredLanguage = PLATFORM_COURSE.defaultLanguage
  const pythonBlock = languagesPayload.find((row) => row.language === "python")

  const totalTasks =
    displayTrackTotal(pythonBlock) ||
    collections
      .filter((item) => item.language === preferredLanguage)
      .reduce((sum, item) => sum + displayCollectionTotal(item.progress), 0) ||
    PLATFORM_COURSE.plannedTasks

  const passedTasks = guestMode ? 0 : (pythonBlock?.progress?.passed_tasks ?? 0)
  const progressPercentValue = guestMode
    ? 0
    : progressPercent({
        ...pythonBlock?.progress,
        catalog_tasks: pythonBlock?.progress?.catalog_tasks ?? totalTasks,
      })

  const chapterCount =
    (Array.isArray(pythonBlock?.collections) ? pythonBlock.collections : [])
      .filter(isPlatformCurriculumChapter)
      .filter((item) => displayCollectionTotal(item.progress) > 0).length ||
    countActiveChapters(collections) ||
    PLATFORM_COURSE.plannedChapters

  const { name: authorName, profilePath: authorProfilePath } = resolveCourseAuthor(data, options)
  const platformMeta = data?.platform_course

  return [
    {
      id: PLATFORM_COURSE.id,
      title: platformMeta?.title?.trim() || PLATFORM_COURSE.title,
      description: platformMeta?.description?.trim() || PLATFORM_COURSE.description,
      author: authorName,
      authorProfilePath,
      order: 0,
      languages: buildCourseLanguages(collections),
      chapterCount,
      totalTasks,
      passedTasks,
      progressPercent: progressPercentValue,
      preferredLanguage,
      hubRoute: LANGUAGE_ROUTES[preferredLanguage],
    },
  ]
}

/** @deprecated use buildLearnCourses */
export function buildLearnTracks(
  data: CurriculumCollectionsDto | null | undefined,
  options?: Parameters<typeof buildLearnCourses>[1],
): LearnCourse[] {
  return buildLearnCourses(data, options)
}

export function learnCourseGlyph(title?: string | null): string {
  const text = title?.trim()
  if (text) return deriveLabelGlyph(text)
  return deriveLabelGlyph(PLATFORM_COURSE.title)
}

export function filterLearnCourses(courses: LearnCourse[], query: string): LearnCourse[] {
  const q = query.trim().toLowerCase()
  if (!q) return courses
  return courses.filter((course) => {
    if (course.title.toLowerCase().includes(q)) return true
    if (course.description.toLowerCase().includes(q)) return true
    if (course.author.toLowerCase().includes(q)) return true
    return course.languages.some(
      (lang) =>
        lang.label.toLowerCase().includes(q) ||
        lang.glyph.toLowerCase().includes(q) ||
        LANGUAGE_LABELS[lang.id].toLowerCase().includes(q),
    )
  })
}

/** @deprecated use filterLearnCourses */
export const filterLearnTracks = filterLearnCourses

export function learnCourseFootnote(course: LearnCourse): string {
  const langCount = course.languages.length
  const langLabel =
    langCount === 1 ? "язык" : langCount < 5 ? "языка" : "языков"
  const chapterLabel =
    course.chapterCount === 1 ? "глава" : course.chapterCount < 5 ? "главы" : "глав"
  return `${langCount} ${langLabel} · ${course.chapterCount} ${chapterLabel} · ${course.totalTasks} задач`
}

/** @deprecated use learnCourseFootnote */
export const learnTrackFootnote = learnCourseFootnote
