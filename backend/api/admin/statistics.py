from fastapi import APIRouter, Depends

from api.dependencies.admin import get_statistics_uc
from api.dependencies.authorization import require_permission
from api.mappers.admin import to_statistics
from api.admin.schemas import SystemStatisticsResponse
from application.admin.statistics import GetSystemStatisticsUseCase
from application.auth.dto import CurrentUserResult
from domain.policies.permissions.permissions import Permission

router = APIRouter(prefix="/statistics", tags=["admin-statistics"])


@router.get("", response_model=SystemStatisticsResponse)
def get_statistics(
    _: CurrentUserResult = Depends(require_permission(Permission.VIEW_SYSTEM_STATISTICS)),
    use_case: GetSystemStatisticsUseCase = Depends(get_statistics_uc),
):
    return to_statistics(use_case.execute())
