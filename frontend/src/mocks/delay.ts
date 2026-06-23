import { MOCK_DELAY_MS } from "@/mocks/config"

export function mockDelay(ms = MOCK_DELAY_MS) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}
