/** Минимальный JWT для демо-режима (роль читается через decodeJwtPayload). */
export function createMockAccessToken(role = "STUDENT") {
  const header = btoa(JSON.stringify({ alg: "none", typ: "JWT" }))
  const payload = btoa(
    JSON.stringify({
      roles: [role],
      role,
      sub: "9001",
      exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 30,
      mock: true,
    }),
  )
  return `${header}.${payload}.mock-signature`
}

export function createMockRefreshToken() {
  return createMockAccessToken("STUDENT")
}

export function isMockAccessToken(token) {
  if (!token || typeof token !== "string") return false
  return token.endsWith(".mock-signature")
}
