import { Outlet } from "react-router-dom"
import LearningAppShell from "@/features/student/layout/LearningAppShell"
import PageHeader from "@/features/student/layout/PageHeader"

export default function SupportShell({ user = null, onSignOut = null }) {
  return (
    <LearningAppShell user={user} onSignOut={onSignOut}>
      <PageHeader
        title="Помощь и поддержка"
        subtitle="Обращения по заданиям и технические вопросы."
      />
      <Outlet context={{ user }} />
    </LearningAppShell>
  )
}
