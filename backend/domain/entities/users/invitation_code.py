from dataclasses import dataclass
from datetime import datetime


@dataclass
class InvitationCode:
    id: int | None
    code: str
    group_id: int
    teacher_id: int
    max_uses: int | None = None
    use_count: int = 0
    expires_at: datetime | None = None
    is_active: bool = True
    created_at: datetime | None = None

    def is_expired(self, now: datetime) -> bool:
        if self.expires_at is None:
            return False
        return now >= self.expires_at

    def has_uses_left(self) -> bool:
        if self.max_uses is None:
            return True
        return self.use_count < self.max_uses
