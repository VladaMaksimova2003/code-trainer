interface StudentTopbarProps {
  user?: unknown | null
}

import StudentHeaderActions from "@/features/student/layout/StudentHeaderActions"

export default function StudentTopbar({
 user = null 
}: StudentTopbarProps) {
  return (
    <div className="topbar topbar-minimal">
      <div className="flex-1" />
      <StudentHeaderActions user={user} />
    </div>
  )
}
