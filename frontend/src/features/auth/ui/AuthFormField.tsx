import type { ReactNode } from "react"

interface AuthFormFieldProps {
  label?: ReactNode
  error?: ReactNode
  help?: ReactNode
  children?: ReactNode
}

export default function AuthFormField({ label, error, help, children }: AuthFormFieldProps) {
  return (
    <div className="field">
      {label ? <label className="label">{label}</label> : null}
      {children}
      {error ? <div className="help err">{error}</div> : null}
      {!error && help ? <div className="help">{help}</div> : null}
    </div>
  )
}
