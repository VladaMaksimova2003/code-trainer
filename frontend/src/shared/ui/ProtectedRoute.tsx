import { Navigate, useLocation } from "react-router-dom"
import type { ReactNode } from "react"
import { roleHome } from "@/features/auth/utils/roleHome"
import { getUserRoles, userHasAnyRole } from "@/shared/api/auth"
import type { NormalizedUserRole, UserLike } from "@/shared/types/user"
import { buildReturnPath, saveAuthReturnPath } from "@/features/auth/utils/authReturnPath"
import LoadingPage from "@/shared/ui/LoadingPage"

interface ProtectedRouteProps {
  isAuthenticated: boolean
  isCheckingAuth: boolean
  children: ReactNode
  allowedNormalizedRoles?: NormalizedUserRole[]
  user?: UserLike | null
}

function ProtectedRoute({
  isAuthenticated,
  isCheckingAuth,
  children,
  allowedNormalizedRoles,
  user,
}: ProtectedRouteProps) {
  const location = useLocation()

  if (isCheckingAuth) {
    return <LoadingPage text="Загрузка…" fullscreen />
  }

  if (!isAuthenticated) {
    saveAuthReturnPath(buildReturnPath(location.pathname, location.search))
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedNormalizedRoles?.length) {
    if (!userHasAnyRole(user, allowedNormalizedRoles)) {
      const roles = getUserRoles(user)
      const fallback = roles[0] ? roleHome(roles[0]) : "/login"
      return <Navigate to={fallback} replace />
    }
  }

  return children
}

export default ProtectedRoute
