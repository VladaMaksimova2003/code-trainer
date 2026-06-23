import { Navigate, useParams } from "react-router-dom"

/** Старые ссылки /teacher/code-assembly/:id/edit → единый редактор. */
export default function LegacyCodeAssemblyEditRedirect() {
  const { taskId } = useParams()
  return <Navigate to={`/teacher/tasks/${taskId}/edit`} replace />
}
