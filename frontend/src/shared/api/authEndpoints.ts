import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import { api } from "@/shared/api/client"

export const register = async (payload: Record<string, unknown>) => {
  const res = await api.post("/auth/register", payload)
  return {
    status: res.status,
    data: res.data,
  }
}

export const sendRegisterEmailCode = async (email: string) => {
  await api.post("/auth/email/send-code", { email, purpose: "register" })
}

export const verifyEmailCode = async ({
  email,
  purpose,
  code,
}: {
  email: string
  purpose: string
  code: string
}) => {
  await api.post("/auth/email/verify-code", { email, purpose, code })
}

export const login = async (payload: Record<string, unknown>) => {
  if (isMockApiEnabled()) return mockHandlers.login(payload)
  const res = await api.post("/auth/login", payload)
  return res.data
}

export const requestPasswordReset = async (email: string) => {
  await api.post("/auth/forgot-password", { email })
}

export const resetPasswordWithCode = async ({
  email,
  code,
  newPassword,
}: {
  email: string
  code: string
  newPassword: string
}) => {
  await api.post("/auth/reset-password", {
    email,
    code,
    new_password: newPassword,
  })
}

export const getMe = async () => {
  if (isMockApiEnabled()) return mockHandlers.getMe()
  const res = await api.get("/auth/me")
  return res.data
}
