import type { AssignedCatalogCardModel } from "@/features/curriculum/components/AssignedCatalogCard"
import type { GroupWorkspaceDto } from "@/shared/types/groups"

export function mapGroupWorkspaceCatalogs(
  workspace: GroupWorkspaceDto | null | undefined,
  groupId: number | string,
): AssignedCatalogCardModel[] {
  const catalogs = workspace?.catalogs
  if (!Array.isArray(catalogs) || catalogs.length === 0) return []

  const groupName = workspace?.group?.name ?? ""
  const teacherName = workspace?.teacher?.name ?? ""

  return catalogs.map((catalog) => {
    const tasks = Array.isArray(catalog.tasks) ? catalog.tasks : []
    const solvedCount = tasks.filter((task) => task.status === "solved").length
    return {
      catalog_id: catalog.catalog_id,
      catalog_title: catalog.catalog_title,
      catalog_description: catalog.catalog_description ?? "",
      group_id: Number(groupId),
      group_name: groupName,
      teacher_name: teacherName,
      deadline_at: catalog.deadline_at ?? null,
      solved_count: solvedCount,
      total_tasks: tasks.length,
    }
  })
}
