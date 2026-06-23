interface EmailVerificationFieldsProps {
  email: unknown
  purpose: unknown
  onSendCode: (...args: unknown[]) => unknown
  onVerifyCode: (...args: unknown[]) => unknown
  code: unknown
  onCodeChange: (...args: unknown[]) => unknown
  onVerified: (...args: unknown[]) => unknown
  onDismissUnverified: (...args: unknown[]) => unknown
  codeSent?: boolean
  sending?: boolean
  sendError?: string
  verified?: boolean
  currentEmail?: unknown | null
  open?: boolean
  autoSend?: boolean
  dismissible?: boolean
  fixed?: boolean
}

import { useCallback, useEffect, useRef, useState } from "react"
import { createPortal } from "react-dom"
import { getErrorMessage } from "@/shared/utils/errors"
import { isValidEmail } from "@/shared/utils/email"

const EMPTY_DIGITS = ["", "", "", "", "", ""]

function formatTime(sec: unknown) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, "0")}`
}

function codeToDigits(code: unknown) {
  const digits = [...EMPTY_DIGITS]
  const raw = String(code || "").replace(/\D/g, "").slice(0, 6)
  for (let i = 0; i < raw.length; i += 1) digits[i] = raw[i]
  return digits
}

export default function EmailVerificationFields({

  email,
  purpose,
  onSendCode,
  onVerifyCode,
  code,
  onCodeChange,
  onVerified,
  onDismissUnverified,
  codeSent = false,
  sending = false,
  sendError = "",
  verified = false,
  currentEmail = null,
  open = false,
  autoSend = false,
  dismissible = true,
  fixed = false,

}: EmailVerificationFieldsProps) {
  const [digits, setDigits] = useState(() => codeToDigits(code))
  const [resendIn, setResendIn] = useState(0)
  const [sentForEmail, setSentForEmail] = useState("")
  const [dismissed, setDismissed] = useState(false)
  const [verifyStatus, setVerifyStatus] = useState("idle")
  const [verifyError, setVerifyError] = useState("")
  const inputsRef = useRef([])
  const sendTimerRef = useRef(null)
  const lastAutoSendEmailRef = useRef("")
  const lastCheckedCodeRef = useRef("")

  useEffect(() => {
    if (open) {
      setDismissed(false)
      return
    }
    lastAutoSendEmailRef.current = ""
  }, [open])

  const trimmedEmail = (email || "").trim()
  const emailValid = isValidEmail(trimmedEmail)

  useEffect(() => {
    setDigits(codeToDigits(code))
  }, [code])

  useEffect(() => {
    lastAutoSendEmailRef.current = ""
    lastCheckedCodeRef.current = ""
    setSentForEmail("")
    setResendIn(0)
    setDigits(EMPTY_DIGITS)
    setDismissed(false)
    setVerifyStatus("idle")
    setVerifyError("")
  }, [trimmedEmail, purpose])

  useEffect(() => {
    if (resendIn <= 0) return undefined
    const timer = setInterval(() => setResendIn((value: unknown) => Math.max(0, value - 1)), 1000)
    return () => clearInterval(timer)
  }, [resendIn])

  const sendCode = useCallback(async () => {
    if (!emailValid || sending) return
    lastCheckedCodeRef.current = ""
    setVerifyStatus("idle")
    setVerifyError("")
    await onSendCode?.()
    setSentForEmail(trimmedEmail)
    setResendIn(30)
  }, [emailValid, onSendCode, sending, trimmedEmail])

  useEffect(() => {
    if (!open || !emailValid) return undefined
    if (lastAutoSendEmailRef.current === trimmedEmail) return undefined

    clearTimeout(sendTimerRef.current)
    sendTimerRef.current = setTimeout(() => {
      if (lastAutoSendEmailRef.current === trimmedEmail) return
      lastAutoSendEmailRef.current = trimmedEmail
      sendCode().catch(() => {
        lastAutoSendEmailRef.current = ""
        setSentForEmail("")
      })
    }, autoSend ? 600 : 0)

    return () => clearTimeout(sendTimerRef.current)
  }, [autoSend, emailValid, open, sendCode, trimmedEmail])

  useEffect(() => {
    if (!emailValid || code.length !== 6 || verified) return undefined
    if (lastCheckedCodeRef.current === code) return undefined

    let cancelled = false
    setVerifyStatus("verifying")
    setVerifyError("")

    onVerifyCode?.(code)
      .then(() => {
        if (cancelled) return
        lastCheckedCodeRef.current = code
        setVerifyStatus("success")
        onVerified?.()
        window.setTimeout(() => setDismissed(true), 700)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        lastCheckedCodeRef.current = ""
        setVerifyStatus("error")
        const message = getErrorMessage(err, "Неверный код. Попробуйте ещё раз.")
        setVerifyError(message)
        setDigits(EMPTY_DIGITS)
        onCodeChange?.("")
        window.setTimeout(() => {
          inputsRef.current[0]?.focus()
          setVerifyStatus("idle")
        }, 1200)
      })

    return () => {
      cancelled = true
    }
  }, [code, emailValid, onCodeChange, onVerified, onVerifyCode, verified])

  const setDigit = (index, value) => {
    if (verifyStatus === "verifying" || verifyStatus === "success") return
    const cleaned = value.replace(/[^0-9]/g, "").slice(0, 1)
    setDigits((prev: unknown) => {
      const next = [...prev]
      next[index] = cleaned
      if (cleaned && index < 5) inputsRef.current[index + 1]?.focus()
      onCodeChange?.(next.join(""))
      return next
    })
    if (verifyError) {
      setVerifyError("")
      setVerifyStatus("idle")
    }
  }

  const onKeyDown = (index: unknown) => (event: unknown) => {
    if (verifyStatus === "verifying" || verifyStatus === "success") return
    if (event.key === "Backspace" && !digits[index] && index > 0) {
      inputsRef.current[index - 1]?.focus()
      setDigits((prev: unknown) => {
        const next = [...prev]
        next[index - 1] = ""
        onCodeChange?.(next.join(""))
        return next
      })
      event.preventDefault()
      return
    }
    if (event.key === "ArrowLeft" && index > 0) {
      inputsRef.current[index - 1]?.focus()
      event.preventDefault()
      return
    }
    if (event.key === "ArrowRight" && index < 5) {
      inputsRef.current[index + 1]?.focus()
      event.preventDefault()
    }
  }

  const onPaste = (event: unknown) => {
    if (verifyStatus === "verifying" || verifyStatus === "success") return
    const text = (event.clipboardData.getData("text") || "").replace(/[^0-9]/g, "").slice(0, 6)
    if (!text) return
    event.preventDefault()
    const next = [...EMPTY_DIGITS]
    for (let i = 0; i < text.length; i += 1) next[i] = text[i]
    setDigits(next)
    onCodeChange?.(next.join(""))
    const focusIndex = Math.min(text.length, 5)
    inputsRef.current[focusIndex]?.focus()
  }

  const handleResend = async () => {
    lastAutoSendEmailRef.current = ""
    lastCheckedCodeRef.current = ""
    setSentForEmail("")
    setVerifyStatus("idle")
    setVerifyError("")
    setDigits(EMPTY_DIGITS)
    onCodeChange?.("")
    onDismissUnverified?.()
    try {
      await sendCode()
      inputsRef.current[0]?.focus()
    } catch {
      setSentForEmail("")
    }
  }

  const handleDismiss = () => {
    if (verifyStatus !== "success" && !verified) {
      onDismissUnverified?.()
    }
    setDismissed(true)
  }

  const visible = open && emailValid && !dismissed

  useEffect(() => {
    if (!fixed || !visible) return undefined
    document.body.classList.add("has-banner")
    return () => document.body.classList.remove("has-banner")
  }, [fixed, visible])

  if (!visible) return null

  const showSentHint = codeSent || sentForEmail === trimmedEmail
  const isVerified = verified || verifyStatus === "success"
  const status =
    verifyStatus === "verifying"
      ? "loading"
      : verifyStatus === "success"
        ? "success"
        : verifyStatus === "error"
          ? "error"
          : sending
            ? "loading"
            : sendError
              ? "error"
              : "idle"
  const statusMessage = verifyError || sendError
  const otpCls = status === "error" ? "err" : isVerified ? "ok" : ""
  const bannerCls = [
    status === "error" ? "err" : isVerified ? "ok" : "",
    fixed ? "verify-banner--fixed" : "",
  ]
    .filter(Boolean)
    .join(" ")

  const banner = (
    <div className={`verify-banner${bannerCls ? ` ${bannerCls}` : ""}`}>
      <div className="verify-inner">
        <div className="verify-text">
          <b>
            🔒 Подтвердите email
            {isVerified ? (
              <span style={{ color: "var(--lime)", marginLeft: 8, fontWeight: 600 }}>· подтверждено</span>
            ) : null}
          </b>
          <div className="row2">
            {currentEmail ? (
              <>
                <span>
                  Активная почта: <span className="email">{currentEmail}</span>
                </span>
                <span className="mut3">·</span>
              </>
            ) : null}
            {sending && !showSentHint ? (
              <span>Отправляем код…</span>
            ) : showSentHint ? (
              <span>
                Мы отправили код на <span className="email">{trimmedEmail}</span>
              </span>
            ) : (
              <span>Отправим код на указанный email</span>
            )}
            {showSentHint && !isVerified ? (
              <>
                <span className="mut3">·</span>
                {resendIn > 0 ? (
                  <span className="mut3">повтор через {formatTime(resendIn)}</span>
                ) : (
                  <button type="button" className="verify-resend" onClick={handleResend} disabled={sending}>
                    Отправить код повторно
                  </button>
                )}
              </>
            ) : null}
          </div>
        </div>

        <div className="verify-otp-row">
          <div className={`otp ${otpCls}`.trim()}>
            {digits.map((digit, index) => (
              <input
                key={`${purpose}-${index}`}
                ref={(element: unknown) => {
                  inputsRef.current[index] = element
                }}
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={1}
                value={digit}
                className={digit ? "filled" : ""}
                disabled={sending || verifyStatus === "verifying" || isVerified}
                aria-label={`Цифра ${index + 1} кода подтверждения`}
                onChange={(event: unknown) => setDigit(index, event.target.value)}
                onKeyDown={onKeyDown(index)}
                onPaste={onPaste}
                onFocus={(event: unknown) => event.target.select()}
              />
            ))}
          </div>

          {status !== "idle" ? (
            <div className={`otp-status ${status}`}>
              {status === "loading" ? (
                <>
                  <span className="spinner otp-spinner" />
                  {verifyStatus === "verifying" ? "Проверка…" : "Отправка…"}
                </>
              ) : null}
              {status === "error" ? (
                <>
                  <span className="otp-status-mark">!</span>
                  {statusMessage}
                </>
              ) : null}
              {status === "success" ? (
                <>
                  <span className="otp-status-mark">✓</span>
                  Email подтверждён
                </>
              ) : null}
            </div>
          ) : null}
        </div>

        {dismissible ? (
          <button
            type="button"
            className="verify-close"
            onClick={handleDismiss}
            title="Скрыть до следующей страницы"
            disabled={sending || verifyStatus === "verifying"}
          >
            ✕
          </button>
        ) : null}
      </div>
    </div>
  )

  if (fixed) return createPortal(banner, document.body)
  return banner
}
