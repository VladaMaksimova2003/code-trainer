import { Link, useNavigate } from "react-router-dom"
import RoleAvatar from "@/shared/ui/RoleAvatar"
import { userHasRole } from "@/shared/api/auth"
import type { UserLike } from "@/shared/types/user"
import StudentNotificationsButton from "@/features/notifications/components/NotificationsDropdown"

interface StudentHeaderActionsProps {
  user?: UserLike | null
}

export default function StudentHeaderActions({ user = null }: StudentHeaderActionsProps) {
  const navigate = useNavigate()

  if (!user) {
    return (
      <div className="flex items-center gap-2">
        <Link to="/login" className="btn btn-secondary btn-sm">
          Войти
        </Link>
        <Link to="/register" className="btn btn-primary btn-sm">
          Регистрация
        </Link>
      </div>
    )
  }

  const isTeacherOrAdmin = userHasRole(user, "TEACHER") || userHasRole(user, "ADMIN")
  const role = isTeacherOrAdmin ? "teacher" : "student"

  return (
    <div className="flex items-center gap-2">
      <StudentNotificationsButton />
      <button
        type="button"
        className="rounded-full border-0 bg-transparent p-0"
        title="Профиль"
        onClick={() => navigate("/student/profile")}
      >
        <RoleAvatar
          user={user}
          name={user?.name}
          role={role}
          size="sm"
          className={isTeacherOrAdmin ? "pp" : ""}
        />
      </button>
    </div>
  )
}
