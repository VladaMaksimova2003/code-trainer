import { isMockApiEnabled } from "@/mocks/config"
import { mockHandlers } from "@/mocks/mockHandlers"
import { api } from "@/shared/api/client"

export const getServerLanguages = async () => {
  if (isMockApiEnabled()) return mockHandlers.getServerLanguages()
  const res = await api.get("/languages/")
  return Array.isArray(res.data) ? res.data : []
}
