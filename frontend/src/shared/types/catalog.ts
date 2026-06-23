/**
 * Task catalog API DTO shapes — aliases to OpenAPI component schemas.
 */

import type { ApiSchema } from "./openapi"

export type CatalogDto = ApiSchema["CatalogResponse"]
export type CatalogTaskListItem = ApiSchema["TaskResponse"]
export type CatalogTaskDto = ApiSchema["TaskResponse"]
