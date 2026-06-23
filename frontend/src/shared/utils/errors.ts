interface ApiErrorDetailItem {
  msg?: string
  message?: string
  [key: string]: unknown
}

interface ApiErrorShape {
  response?: {
    data?: {
      detail?: string | ApiErrorDetailItem[] | Record<string, unknown>
    }
  }
  message?: string
}

function asApiError(error: unknown): ApiErrorShape {
  if (typeof error === "object" && error !== null) {
    return error as ApiErrorShape
  }
  return {}
}

export function getErrorMessage(error: unknown, fallback = "Произошла ошибка"): string {
  const { response, message } = asApiError(error)
  const detail = response?.data?.detail
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const msg = item?.msg || item?.message
        if (typeof msg === "string") return msg.replace(/^Value error,\s*/i, "")
        return JSON.stringify(item)
      })
      .join("; ")
  }
  if (detail && typeof detail === "object") {
    return JSON.stringify(detail)
  }
  return message || fallback
}

export function isEmailFormatError(message: unknown): boolean {
  return /корректн(ый|ого)\s+email/i.test(String(message || ""))
}
