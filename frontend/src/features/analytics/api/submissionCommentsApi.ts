import { api } from "@/shared/api"
import { isMockApiEnabled } from "@/mocks/config"

const USE_MOCK = isMockApiEnabled()

interface SubmissionComment {
  id: number
  submission_id: number
  teacher_id: number
  teacher_name: string
  body: string
  created_at: string
  updated_at: string
}

let _mockComments: SubmissionComment[] = [
  {
    id: 1,
    submission_id: 42,
    teacher_id: 5,
    teacher_name: "Петрова А.",
    body: "Хорошее решение, но добавь проверку на пустой ввод.",
    created_at: "2026-06-04T10:00:00Z",
    updated_at: "2026-06-04T10:00:00Z",
  },
  {
    id: 2,
    submission_id: 42,
    teacher_id: 5,
    teacher_name: "Петрова А.",
    body: "Проверь граничный случай n=0 — цикл не обрабатывает пустой ввод.",
    created_at: "2026-06-04T14:32:00Z",
    updated_at: "2026-06-04T14:32:00Z",
  },
]

const delay = (ms = 300) => new Promise((r: unknown) => setTimeout(r, ms))

function normalizeList(data: unknown): SubmissionComment[] {
  if (Array.isArray(data)) return data as SubmissionComment[]
  const items = (data as { items?: SubmissionComment[] } | null)?.items
  return items ?? []
}

export async function listTeacherComments(submissionId: number | string): Promise<SubmissionComment[]> {
  if (USE_MOCK) {
    await delay()
    return _mockComments.filter((c: unknown) => c.submission_id === Number(submissionId))
  }
  const { data } = await api.get(`/teacher/submissions/${submissionId}/comments`)
  return normalizeList(data)
}

export async function createComment(
  submissionId: number | string,
  body: string,
): Promise<SubmissionComment | undefined> {
  if (USE_MOCK) {
    await delay()
    const item: SubmissionComment = {
      id: Math.max(0, ..._mockComments.map((c: unknown) => c.id)) + 1,
      submission_id: Number(submissionId),
      teacher_id: 5,
      teacher_name: "Вы",
      body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    _mockComments = [..._mockComments, item]
    return item
  }
  const { data } = await api.post(`/teacher/submissions/${submissionId}/comments`, { body })
  return data as SubmissionComment
}

export async function updateComment(
  submissionId: number | string,
  commentId: number,
  body: string,
): Promise<SubmissionComment | undefined> {
  if (USE_MOCK) {
    await delay()
    _mockComments = _mockComments.map((c: unknown) =>
      c.id === commentId ? { ...c, body, updated_at: new Date().toISOString() } : c,
    )
    return _mockComments.find((c: unknown) => c.id === commentId)
  }
  const { data } = await api.patch(`/teacher/submissions/${submissionId}/comments/${commentId}`, { body })
  return data as SubmissionComment
}

export async function deleteComment(
  submissionId: number | string,
  commentId: number,
): Promise<{ ok: boolean }> {
  if (USE_MOCK) {
    await delay()
    _mockComments = _mockComments.filter((c: unknown) => c.id !== commentId)
    return { ok: true }
  }
  await api.delete(`/teacher/submissions/${submissionId}/comments/${commentId}`)
  return { ok: true }
}

export async function listStudentComments(submissionId: number | string): Promise<SubmissionComment[]> {
  if (USE_MOCK) {
    await delay()
    return _mockComments.filter((c: unknown) => c.submission_id === Number(submissionId))
  }
  const { data } = await api.get(`/student/submissions/${submissionId}/comments`)
  return normalizeList(data)
}
