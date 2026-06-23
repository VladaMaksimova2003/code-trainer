import { useState } from "react"
import { createAdminTeacher } from "@/admin-panel/api/admin"
import { ApAlert } from "@/admin-panel/components/ui/ApFeedback"
import { ApFormField } from "@/admin-panel/components/ui/ApPrimitives"
import { toast } from "@/shared/ui/toast"

export default function CreateTeacherPage() {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState("")

  const handleSubmit = async (event) => {
    event.preventDefault()
    setErrorMessage("")
    setIsSubmitting(true)

    try {
      const teacher = await createAdminTeacher({
        name: name.trim(),
        email: email.trim(),
        password,
      })
      toast.success("Преподаватель создан", teacher.email)
      setName("")
      setEmail("")
      setPassword("")
    } catch (error) {
      setErrorMessage(error?.response?.data?.detail || error?.message || "Не удалось создать преподавателя")
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
        <ApFormField label="Имя" htmlFor="teacher-name">
          <input
            id="teacher-name"
            type="text"
            className="ap-input"
            placeholder="Введите имя преподавателя"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </ApFormField>

        <ApFormField label="Почта" htmlFor="teacher-email">
          <input
            id="teacher-email"
            type="email"
            className="ap-input"
            name="create-teacher-email"
            autoComplete="off"
            placeholder="example@mail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </ApFormField>

        <ApFormField label="Пароль" htmlFor="teacher-password">
          <input
            id="teacher-password"
            type="password"
            className="ap-input"
            name="create-teacher-password"
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
