import { useEffect, useState } from "react"
import { Link, Navigate, useNavigate } from "react-router-dom"
import {
  getRoleFromAccessToken,
  setAuthTokens,
} from "@/shared/api/auth"
import { roleHome } from "@/features/auth/utils/roleHome"
import { resolvePostLoginPath } from "@/features/auth/utils/authReturnPath"

export default function LoginCallbackPage({
  isAuthenticated,
  isCheckingAuth = false,
  onAuthSuccess,
}) {
  const navigate = useNavigate()
  const [error, setError] = useState("")
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    let cancelled = false

    const finish = async () => {
      const params = new URLSearchParams(window.location.search)
      const oauthError = params.get("error")
      const accessToken = params.get("access_token")
      const refreshToken = params.get("refresh_token")

      if (oauthError) {
        if (!cancelled) {
          setError(oauthError)
          setIsProcessing(false)
        }
        return
      }

      if (!accessToken || !refreshToken) {
        if (!cancelled) {
          setError("Не удалось получить токены авторизации.")
          setIsProcessing(false)
        }
        return
      }

      setAuthTokens({
        accessToken,
        refreshToken,
        persist: true,
      })

      try {
        await onAuthSuccess?.()
      } catch {
        if (!cancelled) {
          setError("Вход выполнен, но не удалось загрузить профиль. Попробуйте обновить страницу.")
          setIsProcessing(false)
        }
        return
      }

      const role = getRoleFromAccessToken(accessToken)
      const target = resolvePostLoginPath({
        roleHomePath: role ? roleHome(role) : "/",
      })
      navigate(target, { replace: true })
    }

    finish()
    return () => {
      cancelled = true
    }
  }, [navigate, onAuthSuccess])

  if (!isCheckingAuth && isAuthenticated && !isProcessing && !error) {
    return <Navigate to="/" replace />
  }

  return (
    <div className="auth-shell">
      <div className="auth-card" style={{ maxWidth: 420, margin: "0 auto" }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, textAlign: "center", margin: "0 0 12px" }}>
          {error ? "Не удалось войти" : "Завершаем вход…"}
        </h1>

        {isProcessing && !error ? (
          <p className="muted" style={{ textAlign: "center", fontSize: 14, margin: 0 }}>
            Подключаем аккаунт, подождите несколько секунд.
          </p>
        ) : null}

        {error ? (
          <>
            <div className="note err" style={{ marginTop: 16, padding: "10px 12px" }}>
              {error}
            </div>
            <Link
              to="/login"
              className="btn btn-primary btn-full"
              style={{ marginTop: 16, display: "inline-flex" }}
            >
              Вернуться ко входу
            </Link>
          </>
        ) : null}
      </div>
    </div>
  )
}
