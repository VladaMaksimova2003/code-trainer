interface TeacherReviewRow {
  id: number | string
  task_id: number | string
  student_name?: string | null
  success?: boolean | null
}

interface TeacherReviewContext {
  submissionId: number | string
  studentName?: string | null
  success?: boolean | null
}

/** Task page URL with query params so review mode survives refresh. */
export function teacherReviewTaskPath(taskId: number | string, submissionId: number | string): string {
  const params = new URLSearchParams({
    reviewSubmission: String(submissionId),
    tab: "comments",
  })
  return `/tasks/${taskId}?${params.toString()}`
}

export function buildTeacherReviewContext(row: TeacherReviewRow): TeacherReviewContext {
  return {
    submissionId: row.id,
    studentName: row.student_name ?? null,
    success: row.success ?? null,
  }
}

export function teacherReviewNavigation(row: TeacherReviewRow): {
  pathname: string
  search: string
  state: { teacherReview: TeacherReviewContext }
} {
  const params = new URLSearchParams({
    reviewSubmission: String(row.id),
    tab: "comments",
  })
  return {
    pathname: `/tasks/${row.task_id}`,
    search: `?${params.toString()}`,
    state: { teacherReview: buildTeacherReviewContext(row) },
  }
}
