import { useState } from "react"
import { clearAuthTokens } from "@/shared/api/auth"
import {
  changePassword,
  logoutAllSessions,
  logoutSession,
} from "@/features/settings/api/settingsApi"
import ConfirmDialog from "@/shared/ui/ConfirmDialog"
import FormField from "@/features/settings/ui/FormField"
import { getErrorMessage } from "@/shared/utils/errors"
import { toast } from "@/shared/ui/toast"

export default function SecurityTab({ onSignOut }) {
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [confirmLogoutAll, setConfirmLogoutAll] = useState(false)
  const [logoutAllLoading, setLogoutAllLoading] = useState(false)

  const handleChangePassword = async (event) => {
    event.preventDefault()
    if (newPassword !== confirmPassword) {
      setError("Пароли не совпадают")
      return
    }
    if (newPassword.length < 8) {
      setError("Пароль должен содержать минимум 8 символов")
      return
    }
    setSaving(true)
    setError("")
    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
      toast.push({ kind: "lime", title: "Пароль изменён" })
    } catch (err) {
      setError(getErrorMessage(err, "Не удалось изменить пароль"))
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = async () => {
    try {
      await logoutSession()
    } catch {
      // clear local session anyway
    }
    clearAuthTokens()
    onSignOut?.()
  }

  const handleLogoutAll = async () => {
    setLogoutAllLoading(true)
    try {
      await logoutAllSessions()
      clearAuthTokens()
      onSignOut?.()
    } catch (err) {
      setError(getErrorMessage(err, "Не удалось выйти со всех устройств"))
      setConfirmLogoutAll(false)
    } finally {
      setLogoutAllLoading(false)
    }
  }

  return (
    <div style={{ display: "grid", gap: 16, maxWidth: 640 }}>
      {error ? (
        <div className="toast err" style={{ maxWidth: "none" }}>
          <div className="tt">{error}</div>
        </div>
      ) : null}

      <form className="card card-pad" onSubmit={handleChangePassword}>
        <b style={{ fontSize: 14, display: "block", marginBottom: 14 }}>Смена пароля</b>
        <FormField label="Текущий пароль" htmlFor="current-password">
          <input
            id="current-password"
            type="password"
            className="input"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </FormField>
        <FormField label="Новый пароль" htmlFor="new-password" help="Минимум 8 символов.">
          <input
            id="new-password"
            type="password"
            className="input"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            minLength={8}
            autoComplete="new-password"
          />
        </FormField>
        <FormField label="Подтверждение" htmlFor="confirm-password">
          <input
            id="confirm-password"
            type="password"
            className="input"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={8}
            autoComplete="new-password"
          />
        </FormField>
        <div className="row" style={{ justifyContent: "flex-end" }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "…" : "Сменить пароль"}
          </button>
        </div>
        <p className="muted" style={{ fontSize: 13, margin: "12px 0 0" }}>
          Не помните текущий пароль?{" "}
          <a href="/reset-password" style={{ color: "var(--lime)", fontWeight: 600 }}>
            Сбросить через почту
          </a>
        </p>
      </form>

      <div className="card card-pad">
        <b style={{ fontSize: 14, display: "block", marginBottom: 6 }}>Сессии</b>
        <p className="muted" style={{ fontSize: 13.5, margin: "0 0 14px" }}>
          Завершайте сессии на устройствах, которыми больше не пользуетесь.
        </p>
        <div className="row" style={{ flexWrap: "wrap" }}>
          <button type="button" className="btn btn-ghost btn-sm" onClick={handleLogout}>
            Завершить текущую
          </button>
          <button
            type="button"
            className="btn btn-danger btn-sm"
            onClick={() => setConfirmLogoutAll(true)}
          >
            Выйти со всех устройств
          </button>
        </div>
      </div>

      <ConfirmDialog
        open={confirmLogoutAll}
        title="Выйти на всех устройствах?"
        message="Все активные сессии будут отозваны. На каждом устройстве потребуется войти заново."
        confirmLabel="Выйти везде"
        loading={logoutAllLoading}
        onConfirm={handleLogoutAll}
        onCancel={() => setConfirmLogoutAll(false)}
      />
    </div>
  )
}
