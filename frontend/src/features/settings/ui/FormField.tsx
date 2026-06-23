import type { ReactNode } from "react"

interface FormFieldProps {
  label?: ReactNode
  hint?: ReactNode
  help?: ReactNode
  error?: ReactNode
  children?: ReactNode
  htmlFor?: string
}

export default function FormField({ label, hint, help, error, children, htmlFor }: FormFieldProps) {
  return (
    <div className="field">
      {label ? (
        <label htmlFor={htmlFor} className="label">
          {label}
        </label>
      ) : null}
      {children}
      {error ? <p className="help err">{error}</p> : null}
      {!error && (help || hint) ? <p className="help">{help || hint}</p> : null}
    </div>
  )
}
