export function userProfilePath(
  userId: number | string,
  { teacherId = null }: { teacherId?: number | string | null } = {},
): string {
  const base = `/users/${userId}`
  if (teacherId != null) {
    return `${base}?teacherId=${teacherId}`
  }
  return base
}
