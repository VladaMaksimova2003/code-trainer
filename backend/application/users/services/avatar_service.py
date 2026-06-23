from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedAvatar:
    initial: str
    color: str


# Bright neon palette — deterministic index from user_id
NEON_AVATAR_COLORS: tuple[str, ...] = (
    "#39ff14",
    "#00ffff",
    "#ff00ff",
    "#ff3864",
    "#fcee09",
    "#7df9ff",
    "#ff6ec7",
    "#bf00ff",
    "#0ff0fc",
    "#ff3131",
    "#ccff00",
    "#ff5f1f",
)


STUDENT_AVATAR_COLOR = "#8eff01"
TEACHER_AVATAR_COLOR = "#8b53fe"


class AvatarService:
    """Generated letter avatars — no image storage."""

    @staticmethod
    def generate_avatar_initial(name: str) -> str:
        cleaned = (name or "").strip()
        if not cleaned:
            return "?"
        return cleaned[0].upper()

    @staticmethod
    def generate_avatar_color(user_id: int) -> str:
        if user_id is None or user_id < 0:
            user_id = 0
        return NEON_AVATAR_COLORS[user_id % len(NEON_AVATAR_COLORS)]

    @classmethod
    def get_avatar(cls, user_id: int, name: str) -> GeneratedAvatar:
        return GeneratedAvatar(
            initial=cls.generate_avatar_initial(name),
            color=cls.generate_avatar_color(user_id),
        )

    @classmethod
    def color_for_role(cls, role: str | None) -> str | None:
        if role == "teacher":
            return TEACHER_AVATAR_COLOR
        if role == "student":
            return STUDENT_AVATAR_COLOR
        return None

    @classmethod
    def to_dict(cls, user_id: int, name: str, *, role: str | None = None) -> dict[str, str]:
        avatar = cls.get_avatar(user_id, name)
        color = cls.color_for_role(role) or avatar.color
        return {"initial": avatar.initial, "color": color}
