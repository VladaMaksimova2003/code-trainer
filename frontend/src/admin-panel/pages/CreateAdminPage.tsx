import { useState } from "react"
import { Navigate } from "react-router-dom"
import { createAdminAccount } from "@/admin-panel/api/admin"
import { ApAlert } from "@/admin-panel/components/ui/ApFeedback"
import { ApFormField } from "@/admin-panel/components/ui/ApPrimitives"
import { isSuperUser } from "@/shared/utils/superUser"
import { toast } from "@/shared/ui/toast"

export default function CreateAdminPage({ user }) {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState("")

  if (user && !isSuperUser(user)) {
    return <Navigate to="/admin" replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setErrorMessage("")
    setIsSubmitting(true)

    try {
      const admin = await createAdminAccount({
        name: name.trim(),
        email: email.trim(),
        password,
      })
      toast.success("Администратор создан", admin.email)
      setName("")
      setEmail("")
      setPassword("")
    } catch (error) {
      setErrorMessage(error?.response?.data?.detail || error?.message || "Не удалось создать администратора")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <ApAlert message={errorMessage} />

      <form
        className="ap-card ap-card-pad"
        style={{ maxWidth: 480 }}
        onSubmit={handleSubmit}
        autoComplete="off"
      >
        <ApFormField label="Имя" htmlFor="admin-name">
          <input
            id="admin-name"
            type="text"
            className="ap-input"
            placeholder="Введите имя администратора"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </ApFormField>

        <ApFormField label="Почта" htmlFor="admin-email">
          <input
            id="admin-email"
            type="email"
            className="ap-input"
            name="create-admin-email"
            autoComplete="off"
            placeholder="example@mail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </ApFormField>

        <ApFormField label="Пароль" htmlFor="admin-password">
          <input
            id="admin-password"
            type="password"
            className="ap-input"
            name="create-admin-password"
            autoComplete="new-password"
            placeholder="Минимум 8 символов"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </ApFormField>

        <button type="submit" className="ap-btn ap-btn-primary" style={{ width: "100%", marginTop: 8 }} disabled={isSubmitting}>
          {isSubmitting ? "Создание…" : "Создать"}
        </button>
      </form>
    </>
  )
}
