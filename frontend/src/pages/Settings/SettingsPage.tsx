import { Navigate, Route, Routes } from "react-router-dom"
import SettingsLayout from "@/features/settings/ui/SettingsLayout"
import LearningTab from "@/pages/Settings/LearningTab"
import SupportTicketsPage from "@/pages/Support/SupportTicketsPage"
import ProfileTab from "@/pages/Settings/ProfileTab"
import SecurityTab from "@/pages/Settings/SecurityTab"
export default function SettingsPage({ user, onSignOut, onAccountUpdated }) {
  return (
    <Routes>
      <Route
        element={<SettingsLayout user={user} onSignOut={onSignOut} />}
      >
        <Route index element={<Navigate to="profile" replace />} />
        <Route
          path="profile"
          element={<ProfileTab onAccountUpdated={onAccountUpdated} />}
        />
        <Route path="security" element={<SecurityTab onSignOut={onSignOut} />} />
        <Route path="learning" element={<LearningTab />} />
        <Route path="help" element={<SupportTicketsPage />} />
        <Route path="teacher" element={<Navigate to="/settings/profile" replace />} />
      </Route>
    </Routes>
  )
}
