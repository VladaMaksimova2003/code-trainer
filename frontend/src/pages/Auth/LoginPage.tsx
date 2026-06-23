import { useEffect, useState } from "react"
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom"
import { login } from "@/shared/api"
import { AuthHeroPanel } from "@/features/auth/ui/AuthBrand"
import SocialAuth from "@/features/auth/ui/SocialAuth"
import { roleHome } from "@/features/auth/utils/roleHome"
import {
  getAccessToken,
  getRememberMe,
  getRememberedEmail,
  getRoleFromAccessToken,
  setAuthTokens,
  setRememberMePreference,
} from "@/shared/api/auth"
import { redirectToOAuth } from "@/features/auth/utils/socialLogin"
import { resolvePostLoginPath } from "@/features/auth/utils/authReturnPath"

function formatLoginError(err) {
  const detail = err?.response?.data?.detail
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d?.msg || d?.message || String(d)).join(". ")
  }
  return err?.message || "Не удалось войти"
}

export default function LoginPage({ isAuthenticated, isCheckingAuth = false, onAuthSuccess }) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(true)
  const [error, setError] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const fromPath = location.state?.from?.pathname
  const fromSearch = location.state?.from?.search || ""
  const safeFromPath =
    fromPath &&
    fromPath !== "/login" &&
    fromPath !== "/register" &&
    fromPath !== "/reset-password"
      ? `${fromPath}${fromSearch}`
      : null

  useEffect(() => {
    setRememberMe(getRememberMe())
    setEmail(getRememberedEmail())
  }, [])

  if (!isCheckingAuth && isAuthenticated) {
    const token = getAccessToken()
    const role = token ? getRoleFromAccessToken(token) : null
    const target = resolvePostLoginPath({
      locationStatePath: safeFromPath,
      roleHomePath: role ? roleHome(role) : "/",
    })
    return <Navigate to={target} replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!email.trim() || !password) {
      setError("Заполните email и пароль.")
      return
    }
    if (password.length < 6) {
      setError("Пароль слишком короткий.")
      return
    }

    setError("")
    setIsSubmitting(true)
    try {
      const data = await login({ email: email.trim(), password })
      setRememberMePreference(rememberMe, email)
      setAuthTokens({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        persist: rememberMe,
      })

      const role = getRoleFromAccessToken(data.access_token)
      if (!role) {
        setError("Не удалось определить роль пользователя. Попробуйте ещё раз.")
        return
      }

      await onAuthSuccess?.()

      const target = resolvePostLoginPath({
        locationStatePath: safeFromPath,
        roleHomePath: roleHome(role),
      })
      navigate(target, { replace: true })
    } catch (err) {
      setError(formatLoginError(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSocialLogin = (provider) => {
    redirectToOAuth(provider)
  }

  return (
    <div className="auth-shell">
      <div className="auth-split">
        <AuthHeroPanel />

        <div className="auth-form">
          <form className="auth-form-inner" onSubmit={handleSubmit}>
            <h1 style={{ fontSize: 24, fontWeight: 800, margin: "0 0 6px" }}>С возвращением</h1>
            <p className="muted" style={{ fontSize: 14, margin: "0 0 24px" }}>
              Войдите, чтобы продолжить обучение.
            </p>

            {isCheckingAuth ? (
              <div className="note" style={{ marginBottom: 14, padding: "10px 12px", fontSize: 13 }}>
                Проверка сохранённой сессии…
              </div>
            ) : null}

            {error ? (
              <div className="note err" style={{ marginBottom: 14, padding: "10px 12px" }}>
                {error}
              </div>
            ) : null}

            <div className="field">
              <label className="label">Email</label>
              <input
                className="input"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                autoFocus
                required
              />
            </div>

            <div className="field">
              <label className="label">Пароль</label>
              <input
                className="input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={rememberMe ? "current-password" : "password"}
                required
              />
            </div>

            <div className="between" style={{ margin: "4px 0 20px" }}>
              <label
                className="check-row"
                onClick={(e) => {
                  e.preventDefault()
                  setRememberMe((r) => !r)
                }}
              >
                <span className={`checkbox${rememberMe ? " on" : ""}`} />
                Запомнить меня
              </label>
              <Link
                to="/reset-password"
                style={{ fontSize: 13, color: "var(--lime)", fontWeight: 600 }}
              >
                Забыли пароль?
              </Link>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Вход…" : "Войти"}
            </button>

            <Link to="/" className="btn-guest" style={{ marginTop: 10 }}>
              → Войти без регистрации
            </Link>

            <p className="muted" style={{ textAlign: "center", fontSize: 13.5, marginTop: 20 }}>
              Нет аккаунта?{" "}
              <Link to="/register" style={{ color: "#b89bff", fontWeight: 600 }}>
                Зарегистрироваться
              </Link>
            </p>

            <SocialAuth onPick={handleSocialLogin} />
          </form>
        </div>
      </div>
    </div>
  )
}
