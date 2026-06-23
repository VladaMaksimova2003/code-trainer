import { lazy, Suspense } from "react"
import { Navigate, Route, Routes, useParams } from "react-router-dom"
import ProtectedRoute from "@/shared/ui/ProtectedRoute"
import RoutePageFallback from "@/app/RoutePageFallback"
import LoginPage from "@/pages/Auth/LoginPage"
import LoginCallbackPage from "@/pages/Auth/LoginCallbackPage"
import RegisterPage from "@/pages/Auth/RegisterPage"
import ResetPasswordPage from "@/pages/Auth/ResetPasswordPage"
import HomePage from "@/pages/Student/HomePage"

const TaskPage = lazy(() => import("@/pages/task/TaskPage"))
const TeacherCabinetPage = lazy(() => import("@/pages/Teacher/TeacherCabinetPage"))
const TeacherProfileRedirect = lazy(() => import("@/pages/Teacher/TeacherProfileRedirect"))
const TaskEditorPage = lazy(() => import("@/features/task-editor/presentation/pages/TaskEditorPage"))
const LegacyCodeAssemblyEditRedirect = lazy(
  () => import("@/features/teacher/routing/LegacyCodeAssemblyEditRedirect"),
)
const TeacherTasksPage = lazy(() => import("@/features/task-catalog/presentation/pages/TeacherTasksPage"))
const TeacherCatalogPage = lazy(() => import("@/features/task-catalog/presentation/pages/TeacherCatalogPage"))
const ProfilePage = lazy(() => import("@/pages/Student/ProfilePage"))
const GroupDetailPage = lazy(() => import("@/pages/Student/GroupDetailPage"))
const UserProfilePage = lazy(() => import("@/pages/Users/UserProfilePage"))
const SettingsPage = lazy(() => import("@/pages/Settings/SettingsPage"))
const SupportShell = lazy(() => import("@/pages/Support/SupportShell"))
const SupportTicketsPage = lazy(() => import("@/pages/Support/SupportTicketsPage"))
const SupportTicketDetailPage = lazy(() => import("@/pages/Support/SupportTicketDetailPage"))
const LearnHubPage = lazy(() => import("@/pages/Student/LearnHubPage"))
const AssignedCatalogLearnPage = lazy(() => import("@/pages/Student/AssignedCatalogLearnPage"))
const PascalShowcasePage = lazy(() => import("@/pages/Student/PascalShowcasePage"))
const PascalLanguagePage = lazy(() => import("@/pages/Student/PascalLanguagePage"))
const PythonShowcasePage = lazy(() => import("@/pages/Student/PythonShowcasePage"))
const PythonLanguagePage = lazy(() => import("@/pages/Student/PythonLanguagePage"))
const CppShowcasePage = lazy(() => import("@/pages/Student/CppShowcasePage"))
const CppLanguagePage = lazy(() => import("@/pages/Student/CppLanguagePage"))
const CsharpShowcasePage = lazy(() => import("@/pages/Student/CsharpShowcasePage"))
const CsharpLanguagePage = lazy(() => import("@/pages/Student/CsharpLanguagePage"))
const JavaShowcasePage = lazy(() => import("@/pages/Student/JavaShowcasePage"))
const JavaLanguagePage = lazy(() => import("@/pages/Student/JavaLanguagePage"))

const AdminShell = lazy(() => import("@/admin-panel").then((m) => ({ default: m.AdminShell })))
const DashboardPage = lazy(() => import("@/admin-panel").then((m) => ({ default: m.DashboardPage })))
const UsersPage = lazy(() => import("@/admin-panel").then((m) => ({ default: m.UsersPage })))
const UserDetailPage = lazy(() => import("@/admin-panel").then((m) => ({ default: m.UserDetailPage })))
const TeacherRequestsPage = lazy(() =>
  import("@/admin-panel").then((m) => ({ default: m.TeacherRequestsPage })),
)
const AssignmentsPage = lazy(() => import("@/admin-panel").then((m) => ({ default: m.AssignmentsPage })))
const CreateTeacherPage = lazy(() => import("@/admin-panel").then((m) => ({ default: m.CreateTeacherPage })))
const CreateAdminPage = lazy(() => import("@/admin-panel").then((m) => ({ default: m.CreateAdminPage })))
const TcConceptsPage = lazy(() => import("@/admin-panel").then((m) => ({ default: m.TcConceptsPage })))

function DemoTaskRedirect() {
  const { id } = useParams()
  return <Navigate to={`/tasks/${id}`} replace />
}

export function AppRouter({ currentUser, isCheckingAuth, onSignOut, onAccountUpdated, onAuthSuccess }) {
  const isAuthenticated = Boolean(currentUser)

  const protected_ = (element, roles = null) => (
    <ProtectedRoute
      isAuthenticated={isAuthenticated}
      isCheckingAuth={isCheckingAuth}
      allowedNormalizedRoles={roles}
      user={currentUser}
    >
      {element}
    </ProtectedRoute>
  )

  return (
    <Suspense fallback={<RoutePageFallback />}>
      <Routes>
        <Route
          path="/login"
          element={
            <LoginPage
              isAuthenticated={isAuthenticated}
              isCheckingAuth={isCheckingAuth}
              onAuthSuccess={onAuthSuccess}
            />
          }
        />
        <Route
          path="/login/callback"
          element={
            <LoginCallbackPage
              isAuthenticated={isAuthenticated}
              isCheckingAuth={isCheckingAuth}
              onAuthSuccess={onAuthSuccess}
            />
          }
        />
        <Route
          path="/register"
          element={
            <RegisterPage
              isAuthenticated={isAuthenticated}
              isCheckingAuth={isCheckingAuth}
              onAuthSuccess={onAuthSuccess}
            />
          }
        />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/demo" element={<Navigate to="/" replace />} />
        <Route path="/demo/tasks/:id" element={<DemoTaskRedirect />} />
        <Route path="/tasks" element={<Navigate to="/" replace />} />
        <Route path="/signin" element={<Navigate to="/login" replace />} />

        <Route path="/" element={<HomePage user={currentUser} onSignOut={onSignOut} />} />
        <Route path="/tasks/:id" element={<TaskPage user={currentUser} />} />
        <Route path="/learn" element={<LearnHubPage user={currentUser} onSignOut={onSignOut} />} />
        <Route
          path="/learn/assigned/:catalogId"
          element={<AssignedCatalogLearnPage user={currentUser} onSignOut={onSignOut} />}
        />
        <Route path="/learn/pascal" element={<PascalLanguagePage user={currentUser} onSignOut={onSignOut} />} />
        <Route
          path="/learn/pascal/:chapterSlug"
          element={<PascalShowcasePage user={currentUser} onSignOut={onSignOut} />}
        />
        <Route path="/learn/python" element={<PythonLanguagePage user={currentUser} onSignOut={onSignOut} />} />
        <Route
          path="/learn/python/:chapterSlug"
          element={<PythonShowcasePage user={currentUser} onSignOut={onSignOut} />}
        />
        <Route path="/learn/cpp" element={<CppLanguagePage user={currentUser} onSignOut={onSignOut} />} />
        <Route
          path="/learn/cpp/:chapterSlug"
          element={<CppShowcasePage user={currentUser} onSignOut={onSignOut} />}
        />
        <Route path="/learn/csharp" element={<CsharpLanguagePage user={currentUser} onSignOut={onSignOut} />} />
        <Route
          path="/learn/csharp/:chapterSlug"
          element={<CsharpShowcasePage user={currentUser} onSignOut={onSignOut} />}
        />
        <Route path="/learn/java" element={<JavaLanguagePage user={currentUser} onSignOut={onSignOut} />} />
        <Route
          path="/learn/java/:chapterSlug"
          element={<JavaShowcasePage user={currentUser} onSignOut={onSignOut} />}
        />

        {/* Admin */}
        <Route path="/admin" element={protected_(<AdminShell user={currentUser} onSignOut={onSignOut} />, ["ADMIN"])}>
          <Route index element={<DashboardPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="users/:userId" element={<UserDetailPage />} />
          <Route path="teacher-requests" element={<TeacherRequestsPage />} />
          <Route path="assignments" element={<AssignmentsPage />} />
          <Route path="create-teacher" element={<CreateTeacherPage />} />
          <Route path="create-admin" element={<CreateAdminPage user={currentUser} />} />
          <Route path="tc-concepts" element={<TcConceptsPage />} />
          <Route path="concepts" element={<Navigate to="/admin" replace />} />
          <Route path="curriculum" element={<Navigate to="/admin" replace />} />
          <Route path="groups" element={<Navigate to="/admin" replace />} />
          <Route path="statistics" element={<Navigate to="/admin" replace />} />
        </Route>

        {/* Teacher */}
        <Route
          path="/teacher/cabinet"
          element={protected_(<TeacherCabinetPage user={currentUser} onSignOut={onSignOut} />, ["TEACHER", "ADMIN"])}
        />
        <Route
          path="/teacher/profile"
          element={protected_(<TeacherProfileRedirect />, ["TEACHER", "ADMIN"])}
        />
        <Route path="/teacher/tasks" element={protected_(<TeacherTasksPage user={currentUser} onSignOut={onSignOut} />, ["TEACHER", "ADMIN"])} />
        <Route path="/teacher/catalogs" element={protected_(<TeacherCatalogPage user={currentUser} onSignOut={onSignOut} />, ["TEACHER", "ADMIN"])} />
        <Route path="/teacher/catalogs/:catalogId" element={protected_(<TeacherCatalogPage user={currentUser} onSignOut={onSignOut} />, ["TEACHER", "ADMIN"])} />
        <Route path="/teacher/create-task" element={protected_(<TaskEditorPage />, ["TEACHER", "ADMIN"])} />
        <Route path="/teacher/task-editor" element={protected_(<TaskEditorPage />, ["TEACHER", "ADMIN"])} />
        <Route path="/teacher/tasks/:id/edit" element={protected_(<TaskEditorPage />, ["TEACHER", "ADMIN"])} />
        <Route path="/teacher/assignments/:id/edit" element={protected_(<TaskEditorPage />, ["TEACHER", "ADMIN"])} />
        <Route
          path="/teacher/code-assembly/:taskId/edit"
          element={protected_(<LegacyCodeAssemblyEditRedirect />, ["TEACHER", "ADMIN"])}
        />

        {/* Student */}
        <Route path="/student/groups" element={<Navigate to="/student/profile?tab=groups" replace />} />
        <Route
          path="/student/groups/:groupId"
          element={protected_(<GroupDetailPage user={currentUser} onSignOut={onSignOut} />, ["STUDENT", "TEACHER", "ADMIN"])}
        />
        <Route
          path="/student/profile"
          element={protected_(<ProfilePage user={currentUser} onSignOut={onSignOut} />, ["STUDENT", "TEACHER", "ADMIN"])}
        />
        <Route
          path="/users/:userId"
          element={protected_(<UserProfilePage user={currentUser} onSignOut={onSignOut} />)}
        />

        {/* Settings */}
        <Route path="/settings/*" element={protected_(<SettingsPage user={currentUser} onSignOut={onSignOut} onAccountUpdated={onAccountUpdated} />)} />

        {/* Support (standalone) */}
        <Route
          path="/support"
          element={protected_(<SupportShell user={currentUser} onSignOut={onSignOut} />)}
        >
          <Route index element={<SupportTicketsPage />} />
          <Route path="tickets/:id" element={<SupportTicketDetailPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
