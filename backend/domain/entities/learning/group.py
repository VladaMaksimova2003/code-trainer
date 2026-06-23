from dataclasses import dataclass
from datetime import datetime


@dataclass
class Group:
    id: int | None
    name: str
    teacher_id: int
    created_at: datetime | None = None


@dataclass
class GroupMember:
    group_id: int
    student_id: int
    joined_at: datetime | None = None
