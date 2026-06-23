#!/usr/bin/env python3
"""Inspect how curriculum tasks are stored in DB vs catalog."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "scripts"))

from algo_v128_catalog import V128_CHAPTER_TITLES, _TASK_INDEX  # noqa: E402
from application.curriculum.mirror.pedagogical_task_store import (  # noqa: E402
    pedagogical_slot_id_from_showcase,
)
from infrastructure.db.models.task import Task as TaskModel  # noqa: E402
from infrastructure.db.models.task.registry import load_models  # noqa: E402
from infrastructure.db.session import SessionLocal  # noqa: E402
from sqlalchemy import select  # noqa: E402


def main() -> int:
    load_models()
    session = SessionLocal()
    try:
        rows = session.scalars(
            select(TaskModel).where(TaskModel.is_delete.is_(False)).order_by(TaskModel.id)
        ).all()

        expected_by_num = {int(x["task_num"]): x for x in _TASK_INDEX}
        expected_by_title = {x["title"].strip().lower(): x for x in _TASK_INDEX}
        expected_slots = {f"pas_{n:03d}" for n in expected_by_num}

        found_slots: set[str] = set()
        found_nums: list[int] = []
        by_chapter = Counter()
        unmatched: list[tuple[int, str, str]] = []
        matched_ids: list[tuple[int, int, str]] = []

        for row in rows:
            examples = dict(row.code_examples or {})
            showcase = dict(examples.get("curriculum_showcase") or {})
            slot = (
                str(showcase.get("pedagogical_slot_id") or "").strip()
                or pedagogical_slot_id_from_showcase(showcase)
                or ""
            )
            slug = str(showcase.get("slug") or "")
            chapter = str(showcase.get("chapter_key") or showcase.get("group") or "")
            title = (row.title or "").strip()

            matched = False
            matched_num: int | None = None
            if slot in expected_slots:
                matched_num = int(slot.split("_")[1])
                found_slots.add(slot)
                found_nums.append(matched_num)
                matched = True
            else:
                for prefix in ("pas_", "py_", "cpp_", "cs_", "java_"):
                    if slug.startswith(prefix):
                        num = int(slug.split("_")[1])
                        pas_slot = f"pas_{num:03d}"
                        if pas_slot in expected_slots:
                            found_slots.add(pas_slot)
                            found_nums.append(num)
                            matched_num = num
                            matched = True
                        break
                if not matched:
                    low = title.lower()
                    if low in expected_by_title:
                        matched_num = int(expected_by_title[low]["task_num"])
                        found_nums.append(matched_num)
                        found_slots.add(f"pas_{matched_num:03d}")
                        matched = True
                    elif title.startswith("[") and "]" in title:
                        inner = title.split("]", 1)[-1].strip().lower()
                        if inner in expected_by_title:
                            matched_num = int(expected_by_title[inner]["task_num"])
                            found_nums.append(matched_num)
                            found_slots.add(f"pas_{matched_num:03d}")
                            matched = True

            if matched and matched_num is not None:
                matched_ids.append((row.id, matched_num, title[:60]))

            if chapter:
                by_chapter[chapter] += 1
            if not matched:
                unmatched.append((row.id, title[:80], slot or slug or "—"))

        missing_nums = sorted(set(expected_by_num) - set(found_nums))
        dup_nums = sorted(n for n, c in Counter(found_nums).items() if c > 1)
        print(f"DB tasks (non-deleted): {len(rows)}")
        print(f"Catalog slots matched (unique): {len(found_slots)} / 128")
        print(f"Matched rows: {len(matched_ids)}")
        print(f"Missing task numbers: {len(missing_nums)}")
        if dup_nums:
            print(f"Duplicate catalog numbers in DB: {dup_nums}")
            for num in dup_nums:
                print(f"  #{num}:")
                for tid, n, t in matched_ids:
                    if n == num:
                        print(f"    id={tid}  {t}")
        print()
        if missing_nums:
            print("Missing from catalog match:")
            for num in missing_nums:
                item = expected_by_num[num]
                ch = V128_CHAPTER_TITLES.get(item["chapter_key"], item["chapter_key"])
                print(
                    f"  #{num:3d}  pas_{num:03d}  [{ch}]  "
                    f"{item['title']}  ({item['format_ru']})"
                )
        print()
        print("Tasks per chapter_key in DB showcase:")
        for ch, cnt in sorted(by_chapter.items()):
            print(f"  {ch}: {cnt}")
        if unmatched:
            print()
            print(f"Non-catalog / unmatched DB rows ({len(unmatched)}):")
            for tid, title, hint in unmatched:
                print(f"  id={tid}  {hint}  {title}")
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
