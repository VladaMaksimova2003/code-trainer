import { canAccessTeacherWorkspace } from "@/shared/api/auth"
import TeacherAppShell from "@/features/teacher/layout/TeacherAppShell"
import StudentAppShell from "./StudentAppShell"
import { learningSidebarItems } from "./learningSidebarItems"

/** Student shell, or teacher/admin shell with workspace navigation. */
export default function LearningAppShell(props: unknown) {
  const { user } = props as { user?: unknown }
  const sidebarItems = (props as { sidebarItems?: unknown }).sidebarItems ?? learningSidebarItems(user)
  if (canAccessTeacherWorkspace(user)) {
    return <TeacherAppShell {...props} sidebarItems={sidebarItems} />
  }
  return <StudentAppShell {...props} sidebarItems={sidebarItems} />
}
