import { api } from "@/shared/api"

import type { UserProfileDto } from "@/shared/types/user"



export async function getUserProfile(

  userId: number | string,

  { teacherId = null }: { teacherId?: number | string | null } = {},

): Promise<UserProfileDto> {

  const params: Record<string, number | string> = {}

  if (teacherId != null) {

    params.teacher_id = teacherId

  }

  const res = await api.get(`/users/${userId}`, { params })

  return res.data as UserProfileDto

}


