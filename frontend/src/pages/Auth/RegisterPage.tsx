import { useState } from "react"
import { Link, Navigate, useNavigate } from "react-router-dom"
import { register, sendRegisterEmailCode, verifyEmailCode } from "@/shared/api"
import { setAuthTokens } from "@/shared/api/auth"
import { joinGroupByCode } from "@/features/groups/api/groupsApi"
import AuthFormField from "@/features/auth/ui/AuthFormField"
import AuthBrand from "@/features/auth/ui/AuthBrand"
import EmailVerificationFields from "@/features/auth/ui/EmailVerificationFields"
import { getErrorMessage, isEmailFormatError } from "@/shared/utils/errors"
import { emailValidationMessage, isValidEmail } from "@/shared/utils/email"
import SocialAuth from "@/features/auth/ui/SocialAuth"
import { redirectToOAuth } from "@/features/auth/utils/socialLogin"

const MIN_PASSWORD_LENGTH = 8
const MAX_PASSWORD_LENGTH = 64

function validatePassword(value) {
  const pw = value ?? ""
  if (!pw.length) return "Пароль не может быть пустым"
  if (pw.length < MIN_PASSWORD_LENGTH) return "Минимум 8 символов"
  if (pw.length > MAX_PASSWORD_LENGTH) return "Пароль должен содержать не больше 64 символов"
  return null
}

function formatRegisterError(err) {
  const detail = err?.response?.data?.detail
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d?.msg || d?.message || String(d)).join(". ")
  }
  const status = err?.response?.status
  return (
    err?.message ||
    (status ? `Не удалось зарегистрироваться (${status})` : "Не удалось зарегистрироваться")
  )
}

export default function RegisterPage({ isAuthenticated, isCheckingAuth = false, onAuthSuccess }) {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [emailCode, setEmailCode] = useState("")
  const [emailVerified, setEmailVerified] = useState(false)
  const [verificationOpen, setVerificationOpen] = useState(false)
  const [codeSent, setCodeSent] = useState(false)
  const [sendingCode, setSendingCode] = useState(false)
  const [sendCodeError, setSendCodeError] = useState("")
  const [inviteCode, setInviteCode] = useState("")
  const [fieldErrors, setFieldErrors] = useState({})
  const [error, setError] = useState("")
  const [pwHint, setPwHint] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const navigate = useNavigate()

  if (!isCheckingAuth && isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const handleSendCode = async () => {
    const trimmedEmail = email.trim()
    const emailError = emailValidationMessage(trimmedEmail)
    if (emailError) {
      setSendCodeError("")
      setFieldErrors((prev) => ({ ...prev, email: emailError }))
      return
    }
    setSendingCode(true)
    setSendCodeError("")
    setFieldErrors((prev) => {
      const next = { ...prev }
      delete next.email
      return next
    })
    try {
      await sendRegisterEmailCode(trimmedEmail)
      setCodeSent(true)
    } catch (err) {
      const message = getErrorMessage(err, "Не удалось отправить код")
      if (err?.response?.status === 422 || isEmailFormatError(message)) {
        setFieldErrors((prev) => ({ ...prev, email: message }))
        setSendCodeError("")
        setVerificationOpen(false)
      } else {
        setSendCodeError(message)
      }
    } finally {
      setSendingCode(false)
    }
  }

  const handleVerifyCode = async (code) => {
    await verifyEmailCode({ email: email.trim(), purpose: "register", code })
  }

  const handleEmailCodeChange = (code) => {
    setEmailCode(code)
    if (code.length !== 6) setEmailVerified(false)
  }

  const handleBannerDismissUnverified = () => {
    setEmailVerified(false)
    setEmailCode("")
    setVerificationOpen(false)
    setCodeSent(false)
    setSendCodeError("")
  }

  const performRegister = async () => {
    const trimmedName = name.trim()
    const trimmedEmail = email.trim()

    setError("")
    setIsSubmitting(true)
    try {
      const response = await register({
        name: trimmedName,
        email: trimmedEmail,
        password,
        email_verification_code: emailCode,
      })

      if (response?.status !== 200 && response?.status !== 201) {
        setError("Не удалось зарегистрироваться")
        return
      }

      const { access_token: accessToken, refresh_token: refreshToken } = response.data || {}
      if (accessToken) {
        setAuthTokens({ accessToken, refreshToken })
        await onAuthSuccess?.()
      }

      const trimmedInvite = inviteCode.trim()
      if (trimmedInvite) {
        try {
          const group = await joinGroupByCode(trimmedInvite)
          navigate(`/student/groups/${group.id}`, { replace: true })
          return
        } catch {
          navigate("/", { replace: true })
          return
        }
      }

      navigate("/", { replace: true })
    } catch (err) {
      setError(formatRegisterError(err))
      setEmailVerified(false)
      setVerificationOpen(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleVerified = async () => {
    setEmailVerified(true)
    await performRegister()
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const trimmedName = name.trim()
    const trimmedEmail = email.trim()
    const nextErrors = {}
    if (!trimmedName) nextErrors.name = "Укажите имя"
    if (!isValidEmail(trimmedEmail)) {
      nextErrors.email = "Укажите корректный email"
    }
    const pwErr = validatePassword(password)
    if (pwErr) nextErrors.password = pwErr
    setFieldErrors(nextErrors)
    if (Object.keys(nextErrors).length) return

    if (!emailVerified) {
      setError("")
      setVerificationOpen(true)
      return
    }

    await performRegister()
  }

  const trimmedEmail = email.trim()
  const emailIsValid = isValidEmail(trimmedEmail)

  return (
    <>
      {verificationOpen && emailIsValid ? (
        <EmailVerificationFields
          fixed
          open
          email={email.trim()}
          purpose="register"
          code={emailCode}
          onCodeChange={handleEmailCodeChange}
          onSendCode={handleSendCode}
          onVerifyCode={handleVerifyCode}
          onVerified={handleVerified}
          onDismissUnverified={handleBannerDismissUnverified}
          verified={emailVerified}
          codeSent={codeSent}
          sending={sendingCode}
          sendError={sendCodeError}
        />
      ) : null}

      <div className="auth-shell">
        <form className="auth-card" onSubmit={handleSubmit} noValidate>
        <AuthBrand centered />

        <h1 style={{ fontSize: 24, fontWeight: 800, textAlign: "center", margin: "0 0 24px" }}>
          Создать аккаунт
        </h1>

        {error ? (
          <div className="note err" style={{ marginBottom: 14, padding: "10px 12px" }}>
            {error}
          </div>
        ) : null}

        <AuthFormField label="Имя" error={fieldErrors.name}>
          <input
            className={`input${fieldErrors.name ? " err" : ""}`}
            type="text"
            placeholder="Влада"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoComplete="name"
          />
        </AuthFormField>

        <AuthFormField label="Email" error={fieldErrors.email}>
          <input
            className={`input${fieldErrors.email ? " err" : ""}`}
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => {
              const value = e.target.value
              setEmail(value)
              setEmailCode("")
              setEmailVerified(false)
              setVerificationOpen(false)
              setCodeSent(false)
              setSendCodeError("")
              const nextEmailError = emailValidationMessage(value.trim())
              setFieldErrors((prev) => {
                const next = { ...prev }
                if (nextEmailError && value.trim()) next.email = nextEmailError
                else delete next.email
                return next
              })
            }}
            autoComplete="email"
          />
        </AuthFormField>

        <AuthFormField
          label="Пароль"
          error={fieldErrors.password}
          help={
            pwHint && !fieldErrors.password
              ? "Используйте хотя бы 8 символов, цифры и буквы."
              : null
          }
        >
          <input
            className={`input${fieldErrors.password ? " err" : ""}`}
            type="password"
            placeholder="Минимум 8 символов"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onFocus={() => setPwHint(true)}
            onBlur={() => setPwHint(false)}
            autoComplete="new-password"
          />
        </AuthFormField>

        <AuthFormField
          label={
            <>
              Инвайт-код группы <span className="mut3">(необязательно)</span>
            </>
          }
        >
          <input
            className="input mono"
            type="text"
            placeholder="GRP-7K2A"
            value={inviteCode}
            onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
            autoComplete="off"
          />
        </AuthFormField>

        <button
          type="submit"
          className="btn btn-primary btn-full"
          style={{ marginTop: 6 }}
          disabled={isSubmitting}
        >
          {isSubmitting ? "Создание…" : "Зарегистрироваться"}
        </button>

        <p className="muted" style={{ textAlign: "center", fontSize: 13.5, marginTop: 14 }}>
          Уже есть аккаунт?{" "}
          <Link to="/login" style={{ color: "var(--lime)", fontWeight: 600 }}>
            Войти
          </Link>
        </p>

        <SocialAuth
          onPick={redirectToOAuth}
          title="Или зарегистрируйтесь через"
        />
      </form>
      </div>
    </>
  )
}
