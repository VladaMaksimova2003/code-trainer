# Re-export shim — moved to api.users.schemas.*
from api.users.schemas.requests import (  # noqa: F401
    UpdateAccountSettingsRequest,
    ChangePasswordRequest,
    UpdateLearningPreferencesRequest,
    UpdateTeacherSettingsRequest,
)
from api.users.schemas.responses import (  # noqa: F401
    AccountSettingsResponse,
    LearningPreferencesResponse,
    TeacherSettingsResponse,
    TeacherOverviewItemResponse,
    TeacherOverviewResponse,
)
