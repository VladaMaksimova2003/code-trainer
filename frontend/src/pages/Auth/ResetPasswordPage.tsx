import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { requestPasswordReset, resetPasswordWithCode } from "@/shared/api"
import AuthFormField from "@/features/auth/ui/AuthFormField"
import { getErrorMessage } from "@/shared/utils/errors"
import { emailValidationMessage } from "@/shared/utils/email"

const MIN_PASSWORD_LENGTH = 8
const MAX_PASSWORD_LENGTH = 64

function validatePassword(value) {
  const pw = value ?? ""
  if (!pw.length) return "Пароль не может быть пустым"
  if (pw.length < MIN_PASSWORD_LENGTH) return "Минимум 8 символов"
  if (pw.length > MAX_PASSWORD_LENGTH) return "Пароль должен содержать не больше 64 символов"
  return null
}

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [code, setCode] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [sent, setSent] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState("")
  const [fieldErrors, setFieldErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSendLink = async (event) => {
    event.preventDefault()
    const trimmed = email.trim()
    const emailError = emailValidationMessage(trimmed)
    if (emailError) {
      setError("")
      setFieldErrors({ email: emailError })
      return
    }

    setError("")
    setFieldErrors({})
    setIsSubmitting(true)
    try {
      await requestPasswordReset(trimmed)
      setSent(true)
    } catch (err) {
      setError(getErrorMessage(err, "Не удалось отправить запрос"))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleResend = async () => {
    setError("")
    setIsSubmitting(true)
    try {
      await requestPasswordReset(email.trim())
    } catch (err) {
      setError(getErrorMessage(err, "Не удалось отправить код повторно"))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleReset = async (event) => {
    event.preventDefault()
    const nextErrors = {}
    const passwordError = validatePassword(password)
    if (passwordError) nextErrors.password = passwordError
    if (!code.trim()) nextErrors.code = "Введите код из письма"
    if (password !== confirmPassword) nextErrors.confirmPassword = "Пароли не совпадают"
    if (Object.keys(nextErrors).length) {
      setFieldErrors(nextErrors)
      return
    }

    setFieldErrors({})
    setError("")
    setIsSubmitting(true)
    try {
      await resetPasswordWithCode({
        email: email.trim(),
        code: code.trim(),
        newPassword: password,
      })
      setDone(true)
    } catch (err) {
      setError(getErrorMessage(err, "Не удалось сменить пароль"))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="auth-shell">
      <form
        className="auth-card"
        style={{ textAlign: "center" }}
        onSubmit={
          done ? (e) => e.preventDefault() : sent ? handleReset : handleSendLink
        }
        noValidate
      >
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: 18,
            margin: "0 auto 18px",
            background: "var(--lime-soft)",
            border: "1px solid rgba(142,255,1,.3)",
            color: "var(--lime)",
            display: "grid",
            placeItems: "center",
            fontSize: 26,
          }}
        >
          {done ? "✓" : sent ? "✉" : "↻"}
        </div>

        <h1 style={{ fontSize: 22, fontWeight: 800, margin: "0 0 6px" }}>
          {done ? "Пароль изменён" : sent ? "Введите код" : "Сброс пароля"}
        </h1>

        <p className="muted" style={{ fontSize: 14, margin: "0 0 22px" }}>
          {done
            ? "Теперь можно войти с новым паролем."
            : sent
              ? `Мы отправили код на ${email.trim()}. Введите его и новый пароль.`
              : "Введите почту — пришлём код для восстановления."}
        </p>

        {error ? (
          <div
            className="note err"
            style={{ marginBottom: 14, padding: "10px 12px", textAlign: "left" }}
          >
            {error}
          </div>
        ) : null}

        {done ? (
          <button
            type="button"
            className="btn btn-primary btn-full"
            onClick={() => navigate("/login")}
          >
            Перейти ко входу
          </button>
        ) : !sent ? (
          <>
            <AuthFormField label="Почта" error={fieldErrors.email}>
              <input
                className="input"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                autoFocus
              />
            </AuthFormField>

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Отправка…" : "Отправить код"}
            </button>
          </>
        ) : (
          <>
            <AuthFormField label="Код из письма" error={fieldErrors.code}>
              <input
                className="input"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                placeholder="123456"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                autoFocus
              />
            </AuthFormField>

            <AuthFormField label="Новый пароль" error={fieldErrors.password}>
              <input
                className="input"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </AuthFormField>

            <AuthFormField label="Подтверждение" error={fieldErrors.confirmPassword}>
              <input
                className="input"
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </AuthFormField>

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Сохранение…" : "Сменить пароль"}
            </button>

            <button
              type="button"
              className="btn btn-ghost btn-full"
              style={{ marginTop: 10 }}
              disabled={isSubmitting}
              onClick={handleResend}
            >
              Отправить код ещё раз
            </button>
          </>
        )}

        {!done ? (
          <Link
            to="/login"
            style={{
              display: "inline-block",
              marginTop: 18,
              fontSize: 13.5,
              color: "var(--text-2)",
            }}
          >
            ← Назад ко входу
          </Link>
        ) : null}
      </form>
    </div>
  )
}
