"""Export MPLT pitfall catalog entries into the Construction hint library (§2.5.2 VKR)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.curriculum.display.pitfall_catalog import (
    PITFALLS,
    PitfallSpec,
    list_pitfall_ids,
)
from infrastructure.db.models.task.construction import CategoryConstruction, Construction

MPLT_CATEGORY_NAME = "Перенос MPLT"
MPLT_NAME_PREFIX = "MPLT:"
EXPORT_MARKER = "mplt-export:v1"

_TRANSFER_LABELS: dict[str, str] = {
    "TCC": "Истинный перенос (TCC)",
    "FCC": "Ложный перенос (FCC)",
    "ATCC": "Абстрактный перенос (ATCC)",
    "AFCC": "Абстрактно-ложный перенос (AFCC)",
}


@dataclass
class PitfallConstructionSyncReport:
    category_id: int | None = None
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    linked_tasks: list[int] = field(default_factory=list)
    dry_run: bool = False

    @property
    def totals(self) -> dict[str, int]:
        return {
            "created": len(self.created),
            "updated": len(self.updated),
            "skipped": len(self.skipped),
            "linked_tasks": len(self.linked_tasks),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "category_id": self.category_id,
            "category_name": MPLT_CATEGORY_NAME,
            "totals": self.totals,
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "linked_tasks": self.linked_tasks,
        }


def construction_stable_name(pitfall_id: str) -> str:
    return f"{MPLT_NAME_PREFIX}{pitfall_id}"


def parse_export_pitfall_id(description: str) -> str | None:
    match = re.search(rf"{re.escape(EXPORT_MARKER)}[\s\S]*?pitfall_id=([A-Za-z0-9_]+)", description)
    if match:
        return match.group(1)
    return None


def _transfer_label(transfer_type: str | None) -> str:
    key = str(transfer_type or "").strip().upper()
    return _TRANSFER_LABELS.get(key, key or "Перенос")


def _lang_pair(spec: PitfallSpec) -> str:
    sources = ", ".join(spec.get("source_langs") or []) or "—"
    targets = ", ".join(spec.get("target_langs") or []) or "—"
    return f"{sources} → {targets}"


def build_construction_description(spec: PitfallSpec) -> str:
    pitfall_id = str(spec.get("id") or "").strip()
    transfer_type = str(spec.get("transfer_type") or "").strip().upper()
    concepts = ", ".join(spec.get("concept_ids") or []) or "—"
    title = build_construction_display_title(spec)
    lines = [
        f"{_transfer_label(transfer_type)}: {title}",
        f"Идентификатор: {pitfall_id}",
        f"Языки: {_lang_pair(spec)}",
        f"Конструкции: {concepts}",
        "",
    ]
    if spec.get("hint_ru"):
        lines.extend(["Проактивная подсказка:", str(spec["hint_ru"]).strip(), ""])
    contrast = spec.get("contrast_note_ru") or spec.get("pedagogy_note_ru")
    if contrast:
        lines.extend(["Contrast / предупреждение:", str(contrast).strip(), ""])
    if spec.get("feedback_ru"):
        lines.extend(["Реактивная обратная связь:", str(spec["feedback_ru"]).strip(), ""])
    lines.extend(
        [
            "---",
            EXPORT_MARKER,
            f"pitfall_id={pitfall_id}",
            f"transfer_type={transfer_type}",
        ]
    )
    return "\n".join(lines).strip()


def build_construction_display_title(spec: PitfallSpec) -> str:
    hint = str(spec.get("hint_ru") or "").strip()
    if hint:
        short = hint.split(".")[0].split(";")[0].strip()
        if len(short) > 72:
            short = short[:69].rstrip() + "…"
        return short
    return str(spec.get("id") or "pitfall")


def ensure_mplt_category(session: Session, *, dry_run: bool = False) -> CategoryConstruction:
    row = session.scalar(
        select(CategoryConstruction).where(CategoryConstruction.name == MPLT_CATEGORY_NAME)
    )
    if row is not None:
        return row
    if dry_run:
        placeholder = CategoryConstruction(name=MPLT_CATEGORY_NAME)
        placeholder.id = 0
        return placeholder
    row = CategoryConstruction(name=MPLT_CATEGORY_NAME)
    session.add(row)
    session.flush()
    return row


def _find_construction_by_pitfall(
    session: Session,
    pitfall_id: str,
    *,
    category_id: int | None,
) -> Construction | None:
    stable = construction_stable_name(pitfall_id)
    if category_id is not None:
        by_name = session.scalar(
            select(Construction).where(
                Construction.category_id == category_id,
                Construction.name == stable,
            )
        )
        if by_name is not None:
            return by_name
    rows = session.scalars(select(Construction)).all()
    for row in rows:
        if parse_export_pitfall_id(row.description or "") == pitfall_id:
            return row
        if row.name == stable:
            return row
    return None


def upsert_pitfall_construction(
    session: Session,
    spec: PitfallSpec,
    *,
    category_id: int,
    dry_run: bool = False,
) -> tuple[str, Construction | None]:
    pitfall_id = str(spec.get("id") or "").strip()
    if not pitfall_id:
        return "skipped", None

    description = build_construction_description(spec)
    stable_name = construction_stable_name(pitfall_id)
    existing = _find_construction_by_pitfall(session, pitfall_id, category_id=category_id)

    if existing is None:
        if dry_run:
            return "created", None
        row = Construction(
            name=stable_name,
            description=description,
            category_id=category_id,
        )
        session.add(row)
        session.flush()
        return "created", row

    changed = (existing.description or "") != description or existing.category_id != category_id
    if existing.name != stable_name:
        changed = True

    if not changed:
        return "skipped", existing

    if dry_run:
        return "updated", existing

    existing.description = description
    existing.category_id = category_id
    existing.name = stable_name
    session.flush()
    return "updated", existing


def sync_pitfall_constructions(
    session: Session,
    *,
    dry_run: bool = False,
    link_showcase_tasks: bool = False,
) -> PitfallConstructionSyncReport:
    report = PitfallConstructionSyncReport(dry_run=dry_run)
    category = ensure_mplt_category(session, dry_run=dry_run)
    report.category_id = category.id

    constructions_by_pitfall: dict[str, Construction] = {}
    for pitfall_id in list_pitfall_ids():
        spec = PITFALLS[pitfall_id]
        action, row = upsert_pitfall_construction(
            session,
            spec,
            category_id=int(category.id or 0),
            dry_run=dry_run,
        )
        if action == "created":
            report.created.append(pitfall_id)
        elif action == "updated":
            report.updated.append(pitfall_id)
        else:
            report.skipped.append(pitfall_id)
        if row is not None:
            constructions_by_pitfall[pitfall_id] = row

    if link_showcase_tasks and not dry_run:
        report.linked_tasks = _link_showcase_tasks(session, constructions_by_pitfall)

    return report


def _link_showcase_tasks(
    session: Session,
    constructions_by_pitfall: dict[str, Construction],
) -> list[int]:
    from infrastructure.db.models.task.task import Task as TaskModel
    from application.tasks.services.catalog.task_catalog_orchestrator import (
        get_task_pitfall_meta,
    )

    linked: list[int] = []
    tasks = session.scalars(select(TaskModel).where(TaskModel.is_delete.is_(False))).all()
    for task in tasks:
        meta = get_task_pitfall_meta(session, task.id)
        pitfall_id = str(meta.get("pitfall_id") or "").strip()
        if not pitfall_id:
            continue
        construction = constructions_by_pitfall.get(pitfall_id)
        if construction is None:
            continue
        existing_ids = {row.id for row in (task.constructions or [])}
        if construction.id in existing_ids:
            continue
        task.constructions.append(construction)
        linked.append(int(task.id))
    if linked:
        session.flush()
    return linked


def list_mplt_constructions(session: Session) -> list[dict[str, Any]]:
    category = session.scalar(
        select(CategoryConstruction).where(CategoryConstruction.name == MPLT_CATEGORY_NAME)
    )
    if category is None:
        return []

    rows = session.scalars(
        select(Construction)
        .where(Construction.category_id == category.id)
        .order_by(Construction.name)
    ).all()
    items: list[dict[str, Any]] = []
    for row in rows:
        pitfall_id = parse_export_pitfall_id(row.description or "") or ""
        if pitfall_id.startswith(MPLT_NAME_PREFIX):
            pitfall_id = pitfall_id.removeprefix(MPLT_NAME_PREFIX)
        if not pitfall_id and row.name.startswith(MPLT_NAME_PREFIX):
            pitfall_id = row.name.removeprefix(MPLT_NAME_PREFIX)
        spec = PITFALLS.get(pitfall_id) if pitfall_id else None
        items.append(
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "category_id": row.category_id,
                "category_name": MPLT_CATEGORY_NAME,
                "pitfall_id": pitfall_id or None,
                "transfer_type": (spec or {}).get("transfer_type"),
                "hint_ru": (spec or {}).get("hint_ru"),
            }
        )
    return items
