import { z } from "zod"
import { DifficultyLevel, TaskType } from "@/features/task-editor/domain/enums"

export const taskDraftSchema = z.object({
  title: z.string().min(1, "Укажите название").max(255),
  description: z.string().min(1, "Укажите описание"),
  type: z.nativeEnum(TaskType),
  difficulty: z.nativeEnum(DifficultyLevel),
  languages: z.array(z.string()).min(1, "Выберите хотя бы один язык"),
  code: z.string().min(1, "Укажите эталонный код"),
})

export type TaskDraftFormValues = z.infer<typeof taskDraftSchema>
