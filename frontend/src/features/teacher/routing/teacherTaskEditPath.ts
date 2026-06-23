/** Единый URL редактора задания преподавателя. */
export function teacherTaskEditPath(taskId: number | string): string {
  return `/teacher/tasks/${taskId}/edit`
}
