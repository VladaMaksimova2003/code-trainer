import { Navigate, useSearchParams } from "react-router-dom"

const LEGACY_TAB_MAP = {
  tasks: "tasks",
  "teacher-tasks": "tasks",
  solutions: "solutions",
  "teacher-solutions": "solutions",
  analytics: "analytics",
  catalogs: "catalogs",
  groups: "groups",
  "teacher-groups": "groups",
  settings: "tasks",
}

export default function TeacherProfileRedirect() {
  const [searchParams] = useSearchParams()
  const legacy = searchParams.get("tab")
  const tab = LEGACY_TAB_MAP[legacy] || legacy || "tasks"
  const qs = tab ? `?tab=${tab}` : ""
  return <Navigate to={`/teacher/cabinet${qs}`} replace />
}
