"""Student study place / academic group labels for teacher-facing UI."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.db.models.user.user_preferences import UserPreferences

_STUDY_PLACE_MAX = 255
_STUDY_GROUP_MAX = 128


def normalize_study_field(value: str | None, *, max_len: int) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned:
        return None
    return cleaned[:max_len]


def format_study_identity(
    study_place: str | None,
    study_group: str | None,
) -> str | None:
    parts = [part for part in (study_place, study_group) if part]
    return " · ".join(parts) if parts else None


def load_study_identity_by_user_ids(
    session: Session,
    user_ids: list[int],
) -> dict[int, dict[str, str | None]]:
    if not user_ids:
        return {}
    rows = session.execute(
        select(UserPreferences).where(UserPreferences.user_id.in_(user_ids))
    ).scalars().all()
    result: dict[int, dict[str, str | None]] = {}
    for row in rows:
        place = normalize_study_field(row.study_place, max_len=_STUDY_PLACE_MAX)
        group = normalize_study_field(row.study_group, max_len=_STUDY_GROUP_MAX)
        result[int(row.user_id)] = {
            "study_place": place,
            "study_group": group,
            "study_identity": format_study_identity(place, group),
        }
    return result


def get_study_identity(session: Session, user_id: int) -> dict[str, str | None]:
    return load_study_identity_by_user_ids(session, [user_id]).get(
        user_id,
        {"study_place": None, "study_group": None, "study_identity": None},
    )
