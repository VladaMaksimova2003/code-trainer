import type { ReactNode } from "react"

interface TeacherAppShellProps {
  children: ReactNode
  user?: unknown | null
  onSignOut?: (...args: unknown[]) => unknown
  streakDays?: unknown | null
  sidebarItems?: unknown | null
}

import StudentAppShell from "@/features/student/layout/StudentAppShell"
import { teacherSidebarItems } from "./teacherSidebarItems"

export default function TeacherAppShell({

  children,
  user = null,
  onSignOut = null,
  streakDays = null,
  sidebarItems = null,

}: TeacherAppShellProps) {
  return (
    <StudentAppShell
      sidebarItems={sidebarItems ?? teacherSidebarItems(user)}
      brandPP
      user={user}
      onSignOut={onSignOut}
      streakDays={streakDays}
    >
      {children}
    </StudentAppShell>
  )
}
