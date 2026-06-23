/**
 * Groups API DTO shapes — aliases to OpenAPI component schemas.
 */

import type { ApiSchema } from "./openapi"

export type GroupDto = ApiSchema["GroupResponse"]
export type GroupInvitationDto = ApiSchema["InvitationCodeResponse"]
export type GroupDashboardDto = ApiSchema["GroupDashboardResponse"]
export type GroupWorkspaceDto = ApiSchema["StudentGroupWorkspaceResponse"]
export type StudentTasksProgressDto = ApiSchema["StudentGroupTaskProgressResponse"]
export type StudentJoinedGroupOverviewDto = ApiSchema["StudentJoinedGroupOverviewResponse"]
export type StudentAssignedCatalogSummaryDto = ApiSchema["StudentAssignedCatalogSummaryResponse"]

export type GroupDashboardMember = ApiSchema["GroupMemberResponse"]
export type GroupDashboardCatalogRow = ApiSchema["GroupCatalogSummaryResponse"]
export type StudentCatalogProgressRow = ApiSchema["GroupCatalogProgressResponse"]
export type GroupWorkspaceCatalog = ApiSchema["StudentCatalogTasksProgress"]
export type GroupWorkspaceTask = ApiSchema["StudentCatalogTaskProgressItem"]
