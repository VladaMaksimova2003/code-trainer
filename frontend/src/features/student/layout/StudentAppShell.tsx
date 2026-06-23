import type { ReactNode } from "react"

interface StudentAppShellProps {
  children: ReactNode
  user?: unknown | null
  onSignOut?: (...args: unknown[]) => unknown
  sidebarItems?: unknown | null
  brandPP?: boolean
}

import StudentSidebar from "./StudentSidebar"
import StudentTopbar from "./StudentTopbar"
import StudentMobileNav from "./StudentMobileNav"
import { studentSidebarItems } from "./studentSidebarItems"
import { useStudentStreakDays } from "@/shared/hooks/useStudentStreakDays"

export default function StudentAppShell({

  children,
  user = null,
  onSignOut = null,
  streakDays: streakDaysProp = null,
  sidebarItems = null,
  brandPP = false,

}: StudentAppShellProps) {
  const streakFromProfile = useStudentStreakDays(Boolean(user), user?.id)
  const streakDays = streakDaysProp ?? streakFromProfile.streakDays
  const streakReady = streakDaysProp != null || streakFromProfile.ready

  return (
    <div className="app-root app-root--student">
      <StudentSidebar
        user={user}
        items={sidebarItems ?? studentSidebarItems(user)}
        brandPP={brandPP}
        onSignOut={onSignOut}
        streakDays={streakDays}
        streakReady={streakReady}
      />
      <div className="app-main app-main--student">
        <StudentTopbar user={user} />
        <div className="content content--student">{children}</div>
        <StudentMobileNav user={user} />
      </div>
    </div>
  )
}
