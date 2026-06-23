/**
 * Helpers for OpenAPI-generated types (`shared/api/generated/schema.ts`).
 * Regenerate schema: `npm run codegen:api` (see frontend/package.json).
 */

import type { components, operations } from "@/shared/api/generated/schema"

export type ApiSchema = components["schemas"]

/** JSON body of a successful (200) response for an OpenAPI operation. */
export type OpJson200<Op extends keyof operations> = operations[Op] extends {
  responses: { 200: { content: { "application/json": infer T } } }
}
  ? T
  : never

export type Schema<K extends keyof ApiSchema> = ApiSchema[K]
