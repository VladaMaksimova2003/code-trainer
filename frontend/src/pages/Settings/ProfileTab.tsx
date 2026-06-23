import { useEffect, useMemo, useState } from "react"
import { verifyEmailCode } from "@/shared/api"
import {
  getAccountSettings,
  sendChangeEmailCode,
  updateAccountSettings,
} from "@/features/settings/api/settingsApi"
import FormField from "@/features/settings/ui/FormField"
import EmailVerificationFields from "@/features/auth/ui/EmailVerificationFields"
import { getErrorMessage, isEmailFormatError } from "@/shared/utils/errors"
import {
  displayContactEmail,
  emailValidationMessage,
  isValidEmail,
} from "@/shared/utils/email"
import { toast } from "@/shared/ui/toast"

export default function ProfileTab({ onAccountUpdated }) {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [sendingCode, setSendingCode] = useState(false)
  const [account, setAccount] = useState(null)
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [savedEmail, setSavedEmail] = useState("")
  const [about, setAbout] = useState("")
  const [emailCode, setEmailCode] = useState("")
  const [emailVerified, setEmailVerified] = useState(false)
  const [verificationOpen, setVerificationOpen] = useState(false)
  const [codeSent, setCodeSent] = useState(false)
  const [sendCodeError, setSendCodeError] = useState("")
  const [emailFieldError, setEmailFieldError] = useState("")
  const [error, setError] = useState("")

  const emailChanged = useMemo(() => {
    const next = email.trim().toLowerCase()
    const prev = savedEmail.trim().toLowerCase()
    return Boolean(next && prev && next !== prev)
  }, [email, savedEmail])

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setLoading(true)
      setError("")
      try {
        const data = await getAccountSettings()
        if (!cancelled) {
          setAccount(data)
          setName(data.name || "")
          const visibleEmail = displayContactEmail(data.email)
          setEmail(visibleEmail)
          setSavedEmail(visibleEmail)
          setAbout(data.about || "")
        }
      } catch (err) {
        if (!cancelled) {
          setError(getErrorMessage(err, "Не удалось загрузить профиль"))
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    setEmailCode("")
    setEmailVerified(false)
    setVerificationOpen(false)
    setCodeSent(false)
    setSendCodeError("")
  }, [email, savedEmail])

  const handleVerifyCode = async (code) => {
    await verifyEmailCode({ email: email.trim(), purpose: "change_email", code })
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

  const handleSendCode = async () => {
    const trimmedEmail = email.trim()
    const emailError = emailValidationMessage(trimmedEmail)
    if (emailError) {
      setSendCodeError("")
      setEmailFieldError(emailError)
      setVerificationOpen(false)
      return
    }
    setSendingCode(true)
    setSendCodeError("")
    setEmailFieldError("")
    try {
      await sendChangeEmailCode(trimmedEmail)
      setCodeSent(true)
    } catch (err) {
      const message = getErrorMessage(err, "Не удалось отправить код")
      if (err?.response?.status === 422 || isEmailFormatError(message)) {
        setEmailFieldError(message)
        setSendCodeError("")
        setVerificationOpen(false)
      } else {
        setSendCodeError(message)
      }
    } finally {
      setSendingCode(false)
    }
  }

  const performSave = async () => {
    const trimmedEmail = email.trim()

    setSaving(true)
    setError("")
    try {
      const payload = {
        name: name.trim(),
        email: trimmedEmail,
        about: about.trim() || null,
      }
      if (emailChanged) {
        payload.email_verification_code = emailCode
      }
      const updated = await updateAccountSettings(payload)
      setAccount(updated)
      setSavedEmail(updated.email || trimmedEmail)
      setEmailCode("")
      setEmailVerified(false)
      setVerificationOpen(false)
      setCodeSent(false)
      toast.push({ kind: "lime", title: "Профиль сохранён", body: updated.name || name.trim() })
      onAccountUpdated?.(updated)
    } catch (err) {
      setError(getErrorMessage(err, "Не удалось сохранить профиль"))
      setEmailVerified(false)
      setVerificationOpen(false)
    } finally {
      setSaving(false)
    }
  }

  const handleVerified = async () => {
    setEmailVerified(true)
    await performSave()
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const trimmedEmail = email.trim()
    const emailError = emailValidationMessage(trimmedEmail)
    if (emailError) {
      setEmailFieldError(emailError)
      return
    }

    if (emailChanged && !emailVerified) {
      setError("")
      setVerificationOpen(true)
      return
    }

    await performSave()
  }

  if (loading) {
    return <p className="muted">Загрузка профиля…</p>
  }

  const trimmedEmail = email.trim()
  const emailIsValid = isValidEmail(trimmedEmail)

  return (
    <>
      {verificationOpen && emailChanged && emailIsValid ? (
        <EmailVerificationFields
          fixed
          open
          email={email.trim()}
          purpose="change_email"
          currentEmail={savedEmail}
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

      {error ? (
        <div className="toast err" style={{ marginBottom: 16, maxWidth: "none" }}>
          <div className="tt">{error}</div>
        </div>
      ) : null}

      <form className="card card-pad" style={{ maxWidth: 640 }} onSubmit={handleSubmit}>
        <b style={{ fontSize: 14, display: "block", marginBottom: 14 }}>Профиль</b>
        <FormField label="Имя" htmlFor="settings-name">
          <input
            id="settings-name"
            className="input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            maxLength={64}
          />
        </FormField>
        <FormField label="Email" htmlFor="settings-email" error={emailFieldError}>
          <input
            id="settings-email"
            className={`input${emailFieldError ? " err" : ""}`}
            type="email"
            value={email}
            onChange={(e) => {
              const value = e.target.value
              setEmail(value)
              const nextEmailError = emailValidationMessage(value.trim())
              setEmailFieldError(nextEmailError && value.trim() ? nextEmailError : "")
            }}
            required
          />
        </FormField>
        <FormField label="О себе" htmlFor="settings-about">
          <textarea
            id="settings-about"
            className="textarea"
            style={{ fontFamily: "var(--font)", minHeight: 80 }}
            value={about}
            onChange={(e) => setAbout(e.target.value)}
            maxLength={2000}
          />
        </FormField>
        <div className="row" style={{ justifyContent: "flex-end", gap: 10 }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Сохранение…" : "Сохранить"}
          </button>
        </div>
      </form>
    </>
  )
}
