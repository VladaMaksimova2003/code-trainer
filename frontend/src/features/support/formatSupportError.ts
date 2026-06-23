import { formatApiErrorDetail } from "@/shared/utils/formatApiErrorDetail"

interface AxiosLikeError {
  response?: {
    data?: {
      detail?: unknown
    }
  }
}

export function formatSupportError(
  err: AxiosLikeError | null | undefined,
  fallback = "Не удалось отправить обращение. Попробуйте позже.",
): string {
  const detail = formatApiErrorDetail(err?.response?.data?.detail)
  if (detail) return detail
  if (!err?.response) {
    return "Не удалось связаться с сервером. Проверьте, что API запущен."
  }
  return fallback
}
