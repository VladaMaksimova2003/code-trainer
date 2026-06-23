export { api } from "@/shared/api/client"

export { getTasks, getTask, getTaskTypes, getTaskOverview } from "@/shared/api/tasksClient"

export {
  submitSolution,
  resumeSubmissionCheck,
  createSubmission,
  getSubmission,
  abandonSubmission,
  getLatestPendingSubmission,
  getLatestSubmissionForTask,
  rememberPendingSubmission,
  clearPendingSubmission,
  readPendingSubmissionId,
  mapSubmissionToExecution,
} from "@/shared/api/submissionsClient"
export type { SubmitSolutionOptions, ResumeSubmissionCheckOptions } from "@/shared/api/submissionsClient"

export { lintSolution, checkPatterns } from "@/shared/api/solutionsClient"

export { checkFlow, submitBlockReorderSolution } from "@/shared/api/flowsClient"

export {
  register,
  login,
  sendRegisterEmailCode,
  verifyEmailCode,
  requestPasswordReset,
  resetPasswordWithCode,
  getMe,
} from "@/shared/api/authEndpoints"

export {
  getStudentProfile,
  getMyTeacherProfile,
  getTeacherProfile,
  getTeacherTasksList,
  getTeacherActivity,
  requestTeacherRole,
} from "@/shared/api/profilesClient"

export {
  createTeacher,
  listTeacherRoleRequests,
  approveTeacherRoleRequest,
  rejectTeacherRoleRequest,
} from "@/shared/api/adminEndpoints"

export {
  createCodeAssemblyTask,
  getCodeAssemblyTask,
  getCodeAssemblyAuthorTask,
  updateCodeAssemblyTask,
  createAssignment,
} from "@/shared/api/codeAssemblyClient"

export { getServerLanguages } from "@/shared/api/languagesClient"
