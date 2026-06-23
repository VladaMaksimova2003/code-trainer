from dataclasses import dataclass, field
from datetime import datetime

from shared.enums import AssignmentSetVisibility


@dataclass
class AssignmentSetItem:
    assignment_set_id: int
    task_id: int
    sort_order: int = 0
    topic: str | None = None


@dataclass
class AssignmentSet:
    id: int | None
    name: str
    description: str
    teacher_id: int
    visibility: AssignmentSetVisibility = AssignmentSetVisibility.PRIVATE
    group_id: int | None = None
    is_archived: bool = False
    items: list[AssignmentSetItem] = field(default_factory=list)
    created_at: datetime | None = None
    deadline_at: datetime | None = None
