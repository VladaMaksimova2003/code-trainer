/**
 * Settings API DTO shapes — aliases to OpenAPI component schemas.
 */

import type { ApiSchema } from "./openapi"

export type AccountSettingsDto = ApiSchema["AccountSettingsResponse"]
export type LearningPreferencesDto = ApiSchema["LearningPreferencesResponse"]
export type TeacherSettingsDto = ApiSchema["TeacherSettingsResponse"]
export type TeacherOverviewDto = ApiSchema["TeacherOverviewResponse"]
