"""Merge duplicate Pascal/Python showcase rows into one pedagogical task id."""



from __future__ import annotations



import argparse

import sys

from copy import deepcopy

from pathlib import Path

from sqlalchemy.orm.attributes import flag_modified



BACKEND_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BACKEND_ROOT))



from application.curriculum.mirror.curriculum_slot_mirror_map import all_mirrored_pairs

from application.curriculum.mirror.pedagogical_task_model import (

    copy_language_code_examples,

    merge_showcase_pair,

    neutral_title_for_showcase,

    normalize_unified_showcase,

)

from application.curriculum.mirror.pedagogical_task_store import (

    canonical_pedagogical_slot_id,

    find_task_by_pedagogical_slot,

    find_showcase_task_by_track_slug,

)

from application.curriculum.mirror.universal_core_validation import (

    collect_universal_core_stats,

    run_all_validations,

)

from application.curriculum.pascal.showcase.pascal_showcase_core import find_showcase_task_by_slug as find_pascal

from application.curriculum.python.showcase.python_showcase_core import find_showcase_task_by_slug as find_python

from application.curriculum.task_curriculum_link_service import TaskCurriculumLinkService

from infrastructure.db.models.task.registry import load_models

from infrastructure.db.models.task.task import Task as TaskModel

from infrastructure.db.session import SessionLocal



load_models()





def _apply_neutral_title(row: TaskModel, showcase: dict) -> None:

    neutral = neutral_title_for_showcase(showcase)

    if not neutral:

        return

    prefix = ""

    if row.title.startswith("[Pascal v3.1.1:"):

        prefix = "[Pascal v3.1.1: "

    elif row.title.startswith("[Python v1:"):

        prefix = "[Python v1: "

    if prefix:

        row.title = f"{prefix}{neutral}]"

    else:

        row.title = neutral





def merge_pair(session, pascal_slot: str, python_slot: str, *, dry_run: bool) -> str | None:

    pascal_row = find_pascal(session, pascal_slot) or find_showcase_task_by_track_slug(
        session, pascal_slot, language="pascal"
    )

    python_row = find_python(session, python_slot) or find_showcase_task_by_track_slug(
        session, python_slot, language="python"
    )

    if pascal_row is None or python_row is None:

        return f"skip:{pascal_slot}:missing"



    ped_id = canonical_pedagogical_slot_id(slot_id=pascal_slot, slug=pascal_slot, language="pascal")

    existing = find_task_by_pedagogical_slot(session, ped_id)

    if existing is not None:

        showcase = dict((existing.code_examples or {}).get("curriculum_showcase") or {})

        tracks = (showcase.get("language_tracks") or {})

        if (

            isinstance(tracks, dict)

            and "pascal" in tracks

            and "python" in tracks

            and pascal_row.id == existing.id

            and (python_row.is_delete or python_row.id == existing.id)

        ):

            return f"skip:{pascal_slot}:already-unified"

        if existing.id not in {pascal_row.id, python_row.id}:

            return f"skip:{pascal_slot}:ped-id-owned-by-{existing.id}"



    if pascal_row.id == python_row.id:

        showcase = dict((pascal_row.code_examples or {}).get("curriculum_showcase") or {})

        merged = normalize_unified_showcase(

            merge_showcase_pair(showcase, showcase, pedagogical_slot_id=ped_id)

        )

        if dry_run:

            return f"would-normalize:{pascal_slot}:{pascal_row.id}"

        examples = deepcopy(pascal_row.code_examples or {})

        examples["curriculum_showcase"] = merged

        pascal_row.code_examples = examples

        flag_modified(pascal_row, "code_examples")

        _apply_neutral_title(pascal_row, merged)

        session.flush()

        return f"normalized:{pascal_slot}:{pascal_row.id}"



    keep = pascal_row

    drop = python_row



    pascal_showcase = dict((pascal_row.code_examples or {}).get("curriculum_showcase") or {})

    python_showcase = dict((python_row.code_examples or {}).get("curriculum_showcase") or {})

    merged_showcase = merge_showcase_pair(

        pascal_showcase,

        python_showcase,

        pedagogical_slot_id=ped_id,

    )



    if dry_run:

        return f"would-merge:{pascal_slot}:{keep.id}<-{drop.id}"



    keep_examples = copy_language_code_examples(python_row.code_examples or {}, deepcopy(pascal_row.code_examples or {}))

    keep_examples = copy_language_code_examples(deepcopy(pascal_row.code_examples or {}), keep_examples)

    keep_examples["curriculum_showcase"] = merged_showcase

    keep.code_examples = keep_examples

    flag_modified(keep, "code_examples")

    _apply_neutral_title(keep, merged_showcase)



    link_service = TaskCurriculumLinkService(session)

    for link in link_service.get_task_curriculum_links(drop.id):

        existing_patterns = {

            item.exercise_pattern_id

            for item in link_service.get_task_curriculum_links(keep.id)

        }

        if link.exercise_pattern_id in existing_patterns:

            continue

        try:

            link_service.link_task_to_curriculum(

                keep.id,

                link.language,

                link.technical_concept_id,

                link.exercise_pattern_id,

                is_primary=link.is_primary,

            )

        except Exception:

            pass



    drop.is_delete = True

    flag_modified(drop, "is_delete")

    session.flush()

    return f"merged:{pascal_slot}:{keep.id}<-{drop.id}"





def main() -> None:

    parser = argparse.ArgumentParser(description="Merge mirrored Pascal/Python showcase tasks")

    parser.add_argument("--dry-run", action="store_true")

    parser.add_argument("--validate", action="store_true", help="Run validations after merge")

    parser.add_argument("--report", action="store_true", help="Print Universal Core stats")

    args = parser.parse_args()



    session = SessionLocal()

    try:

        stats_before = collect_universal_core_stats(session) if args.report else None

        results: list[str] = []

        for pascal_slot, python_slot in sorted(all_mirrored_pairs().items()):

            result = merge_pair(session, pascal_slot, python_slot, dry_run=args.dry_run)

            if result:

                results.append(result)

        if not args.dry_run:

            session.commit()

        for line in results:

            print(line)

        merged_count = sum(1 for line in results if line.startswith("merged:") or line.startswith("normalized:"))

        print(f"processed: {len(results)} merged_or_normalized: {merged_count}")



        if args.validate and not args.dry_run:

            validation = run_all_validations(session)

            for name, issues in validation.items():

                print(f"validation:{name}:{len(issues)}")

                for issue in issues[:20]:

                    print(f"  - {issue}")

                if len(issues) > 20:

                    print(f"  ... and {len(issues) - 20} more")



        if args.report:

            stats_after = collect_universal_core_stats(session)

            print("--- report ---")

            if stats_before:

                print(f"before_active: {stats_before['active_showcase_tasks']}")

            print(f"after_active: {stats_after['active_showcase_tasks']}")

            print(f"unified_tasks: {stats_after['unified_tasks']}")

            print(f"both_tracks: {stats_after['both_tracks_tasks']}")

            print(f"pascal_only: {stats_after['pascal_only_tasks']}")

            print(f"python_only: {stats_after['python_only_tasks']}")

            print(f"unmerged_pairs: {len(stats_after['unmerged_pairs'])}")

            if stats_after["unmerged_pairs"]:

                for pair in stats_after["unmerged_pairs"][:15]:

                    print(f"  unmerged: {pair}")

            if stats_after["manual_review"]:

                print(f"manual_review: {len(stats_after['manual_review'])}")

    finally:

        session.close()





if __name__ == "__main__":

    main()

