import "@/admin-panel/styles/admin-panel.css"
import { useEffect, useState } from "react"
import { Outlet, useLocation } from "react-router-dom"
import StudentSidebar from "@/features/student/layout/StudentSidebar"
import { learningSidebarItems } from "@/features/student/layout/learningSidebarItems"
import { useStudentStreakDays } from "@/shared/hooks/useStudentStreakDays"
import AdminSubNav from "./AdminSubNav"
import AdminTopbar from "./AdminTopbar"
import ApPageHeader from "@/admin-panel/components/ui/ApPageHeader"
import { getAdminPageMeta } from "@/admin-panel/config/adminSections"

export default function AdminShell({ user, onSignOut, streakDays: streakDaysProp = null }) {
  const streakFromProfile = useStudentStreakDays(Boolean(user), user?.id)
  const streakDays = streakDaysProp ?? streakFromProfile.streakDays
  const streakReady = streakDaysProp != null || streakFromProfile.ready
  const location = useLocation()
  const pageMeta = getAdminPageMeta(location.pathname)
  const [subtitleOverride, setSubtitleOverride] = useState<string | null>(null)

  useEffect(() => {
    setSubtitleOverride(null)
  }, [location.pathname])

  const subtitle = subtitleOverride ?? pageMeta.subtitle

  return (
    <div className="ap-root">
      <StudentSidebar
        items={learningSidebarItems(user)}
        brandPP
        user={user}
        onSignOut={onSignOut}
        streakDays={streakDays}
        streakReady={streakReady}
      />
      <div className="ap-main">
        <AdminTopbar />
        <div className="ap-content">
          <ApPageHeader title={pageMeta.title} subtitle={subtitle} />
          <AdminSubNav user={user} />
          <Outlet context={{ currentAdminUser: user, setAdminPageSubtitle: setSubtitleOverride }} />
        </div>
      </div>
    </div>
  )
}
