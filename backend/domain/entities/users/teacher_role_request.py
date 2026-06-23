"""Domain entity: request to obtain teacher role."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from shared.enums import TeacherRoleRequestStatus


@dataclass
class TeacherRoleRequest:
    id: int | None
    user_id: int
    status: TeacherRoleRequestStatus
    created_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewed_by_id: int | None = None
    message: str | None = None
    user_name: str | None = None
    user_email: str | None = None

    def is_pending(self) -> bool:
        return self.status == TeacherRoleRequestStatus.PENDING
