"""
Analytics aggregation from Submission, Task, and Group models.

Structure progress uses task `constructions` (legacy JSON + DB association names).
Error breakdown heuristic: COMPILER/LINTER -> syntax; pattern/test WA -> logic; INTERNAL_ERROR -> runtime.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from application.learning.submission_analytics import (
    classify_submission_errors as _classify_submission_errors,
    compute_level as _compute_level,
    load_task_map as _load_task_map,
    task_constructions as _task_constructions,
    teacher_group_student_ids as _teacher_group_student_ids,
)
from application.tasks.services.catalog.task_display import display_title_for_task_model
from application.tasks.services.content_access_service import ContentAccessService
from application.auth.dto import CurrentUserResult
from domain.policies.rbac.rbac import normalize_role
from infrastructure.db.models.learning.group import Group, group_member_association_table
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.user import User
from application.learning.recommendations.student_recommendations_service import (
    get_student_recommendations,
    recommendations_to_legacy_list,
)
from application.learning.display_tc_progress_service import (
    build_display_tc_progress,
    build_display_tc_progress_by_language,
    build_display_tc_group_progress,
    build_display_tc_group_progress_by_language,
    pick_default_tc_skills_language,
)
from application.learning.tc_task_recommendations_service import build_tc_task_recommendations
from application.learning.skill_progress_service import (
    CURRICULUM_LANGUAGE_LABELS,
    build_skill_progress,
    curriculum_languages_for_task,
    solved_task_ids_by_language,
)
from application.learning.use_cases.groups.dashboard import _catalog_task_ids

_DEFAULT_TS = datetime(1970, 1, 1, tzinfo=timezone.utc)

STRUCTURE_BUCKETS: dict[str, dict[str, Any]] = {
    "if": {
        "keys": {"if_statement"},
        "label": "Условия (if)",
        "hint": "Ветвление: if / else и проверка условий",
    },
    "loops": {
        "keys": {"for_loop", "while_loop", "nested_loops"},
        "label": "Циклы",
        "hint": "for, while и вложенные циклы",
    },
    "functions": {
        "keys": {"function_definition", "return_statement"},
        "label": "Функции",
        "hint": "Определение функций и return",
    },
    "arrays": {
        "keys": set(),
        "label": "Массивы",
        "hint": "Списки, индексы (по ключевым словам в задаче, если нет тега)",
        "title_keywords": ("массив", "список", "array", "list", "vector"),
    },
}

ARRAY_TITLE_KEYWORDS = STRUCTURE_BUCKETS["arrays"]["title_keywords"]


def _task_display_title(task: TaskModel | None, task_id: int) -> str:
    if task is None:
        return f"Задача #{task_id}"
    return display_title_for_task_model(task)


def _normalize_language(lang: str | None) -> str:
    raw = (lang or "").strip().lower()
    if not raw:
        return "Другое"
    if "python" in raw or raw in {"py"}:
        return "Python"
    if "c++" in raw or "cpp" in raw or raw == "c":
        return "C++"
    if "javascript" in raw or raw in {"js"}:
        return "JavaScript"
    return lang.strip() if lang else "Другое"


def _public_task_type(raw: str) -> str:
    if raw == "diagram":
        return "blocks"
    return raw


def _structure_keys_for_task(task: TaskModel, constructions: list[str]) -> set[str]:
    keys: set[str] = set()
    construction_set = set(constructions)
    title_blob = f"{task.title} {task.description}".lower()
    for bucket_id, meta in STRUCTURE_BUCKETS.items():
        if construction_set & meta["keys"]:
            keys.add(bucket_id)
        elif bucket_id == "arrays" and any(kw in title_blob for kw in ARRAY_TITLE_KEYWORDS):
            keys.add(bucket_id)
    return keys


def _error_breakdown(submissions: list[Submission]) -> dict[str, Any]:
    counts = {"syntax": 0, "logic": 0, "runtime": 0}
    failed = [s for s in submissions if s.success is False]
    for sub in failed:
        cat = _classify_submission_errors(sub)
        if cat in counts:
            counts[cat] += 1
    total = sum(counts.values()) or 1
    return {
        "counts": counts,
        "percent": {
            k: round(100.0 * v / total, 1) for k, v in counts.items()
        },
        "total_failed": len(failed),
    }


def _teacher_task_ids(db: Session, teacher_id: int) -> set[int]:
    return set(
        db.execute(
            select(TaskModel.id).where(
                TaskModel.teacher_id == teacher_id,
                TaskModel.is_delete.is_(False),
            )
        ).scalars().all()
    )


def build_student_analytics(db: Session, viewer: CurrentUserResult) -> dict[str, Any]:
    uid = viewer.id
    roles = frozenset(normalize_role(r) for r in viewer.roles)
    access = ContentAccessService(db)
    accessible_ids = access.list_accessible_task_ids(uid, roles)
    total_tasks = len(accessible_ids)

    subs = (
        db.query(Submission)
        .options(
            joinedload(Submission.linter_errors),
            joinedload(Submission.pattern_errors),
            joinedload(Submission.test_results),
        )
        .filter(Submission.user_id == uid)
        .order_by(Submission.created_at.desc())
        .all()
    )

    task_attempts: dict[int, list[Submission]] = defaultdict(list)
    for s in subs:
        task_attempts[s.task_id].append(s)

    solved_ids = {
        tid
        for tid, lst in task_attempts.items()
        if any(x.success is True for x in lst)
    }
    solved_count = len(solved_ids)
    completion_pct = (
        round(100.0 * solved_count / total_tasks, 1) if total_tasks else 0.0
    )
    level = _compute_level(solved_count / total_tasks if total_tasks else 0.0)

    successful = sum(1 for s in subs if s.success is True)
    total_submissions = len(subs)
    success_rate = (
        round(100.0 * successful / total_submissions, 1) if total_submissions else 0.0
    )

    task_ids_needed = set(task_attempts.keys())
    task_map = _load_task_map(db, task_ids_needed)

    by_language: dict[str, dict[str, int]] = defaultdict(
        lambda: {"solved": 0, "total": 0}
    )
    for tid in accessible_ids:
        tm = task_map.get(tid)
        lang = "Python"
        if tm and getattr(tm, "block_reorder_task", None):
            lang = _normalize_language(tm.block_reorder_task.language)
        elif subs:
            for s in subs:
                if s.task_id == tid:
                    lang = _normalize_language(s.language)
                    break
        by_language[lang]["total"] += 1
        if tid in solved_ids:
            by_language[lang]["solved"] += 1

    for tid in solved_ids:
        if tid not in accessible_ids:
            lang = _normalize_language(
                next((s.language for s in task_attempts[tid]), None)
            )
            by_language[lang]["total"] += 0
            by_language[lang]["solved"] += 1

    language_progress = [
        {
            "language": lang,
            "solved": data["solved"],
            "total": data["total"],
            "percent": round(100.0 * data["solved"] / data["total"], 1)
            if data["total"]
            else 0.0,
        }
        for lang, data in sorted(by_language.items())
        if data["total"] > 0 or data["solved"] > 0
    ]

    accessible_task_map = _load_task_map(db, set(accessible_ids) | solved_ids)
    tc_progress_task_ids = set(accessible_ids) | solved_ids
    solved_by_language = solved_task_ids_by_language(subs)

    def _code_examples_for_task(task_id: int) -> dict[str, Any] | None:
        task_model = accessible_task_map.get(task_id)
        return task_model.code_examples if task_model is not None else None

    def _task_languages(task_id: int) -> list[str]:
        return curriculum_languages_for_task(_code_examples_for_task(task_id))

    tc_skills_by_language = build_display_tc_progress_by_language(
        accessible_task_ids=tc_progress_task_ids,
        solved_task_ids_by_language=solved_by_language,
        task_languages=_task_languages,
        get_code_examples=_code_examples_for_task,
    )
    tc_skill_groups_by_language = build_display_tc_group_progress_by_language(
        accessible_task_ids=tc_progress_task_ids,
        solved_task_ids_by_language=solved_by_language,
        task_languages=_task_languages,
        get_code_examples=_code_examples_for_task,
    )
    default_tc_language = pick_default_tc_skills_language(
        tc_skills_by_language,
        solved_by_language,
    )
    tc_skills = tc_skills_by_language.get(default_tc_language) or build_display_tc_progress(
        accessible_task_ids=tc_progress_task_ids,
        solved_task_ids=solved_ids,
        get_code_examples=_code_examples_for_task,
        language=default_tc_language,
        solved_task_ids_by_language=solved_by_language,
    )
    tc_skill_groups = tc_skill_groups_by_language.get(default_tc_language) or build_display_tc_group_progress(
        accessible_task_ids=tc_progress_task_ids,
        solved_task_ids=solved_ids,
        get_code_examples=_code_examples_for_task,
        language=default_tc_language,
        solved_task_ids_by_language=solved_by_language,
    )
    tc_skill_languages = [
        {
            "code": lang,
            "label": CURRICULUM_LANGUAGE_LABELS.get(lang, lang),
        }
        for lang in tc_skills_by_language
        if any(int(row.get("total") or 0) > 0 for row in tc_skills_by_language.get(lang, []))
    ]

    def _constructions_for_task(task_id: int) -> list[str]:
        task_model = accessible_task_map.get(task_id)
        if task_model is None:
            return []
        return _task_constructions(db, task_model)

    skill_progress = build_skill_progress(
        accessible_task_ids=accessible_ids,
        solved_task_ids=solved_ids,
        get_constructions=_constructions_for_task,
    )

    tc_task_recommendations_by_language: dict[str, list[dict[str, Any]]] = {}
    for lang_row in tc_skill_languages:
        lang_code = str(lang_row.get("code") or "")
        if not lang_code:
            continue
        lang_skills = tc_skills_by_language.get(lang_code, [])
        tc_task_recommendations_by_language[lang_code] = build_tc_task_recommendations(
            tc_skills=lang_skills,
            accessible_task_ids=tc_progress_task_ids,
            solved_task_ids=solved_ids,
            get_task=lambda task_id: accessible_task_map.get(task_id),
            get_code_examples=_code_examples_for_task,
            language=lang_code,
            solved_task_ids_by_language=solved_by_language,
        )

    tc_task_recommendations = tc_task_recommendations_by_language.get(default_tc_language) or build_tc_task_recommendations(
        tc_skills=tc_skills,
        accessible_task_ids=tc_progress_task_ids,
        solved_task_ids=solved_ids,
        get_task=lambda task_id: accessible_task_map.get(task_id),
        get_code_examples=_code_examples_for_task,
        language=default_tc_language,
        solved_task_ids_by_language=solved_by_language,
    )

    recent_activity = []
    for s in subs[:15]:
        tm = task_map.get(s.task_id)
        recent_activity.append(
            {
                "submission_id": s.id,
                "task_id": s.task_id,
                "task_title": _task_display_title(tm, s.task_id),
                "success": s.success,
                "status": s.status,
                "language": _normalize_language(s.language),
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
        )

    per_task = []
    for tid in sorted(task_attempts.keys()):
        lst = sorted(
            task_attempts[tid], key=lambda x: x.created_at or _DEFAULT_TS
        )
        attempts = len(lst)
        wins = sum(1 for x in lst if x.success is True)
        tm = task_map.get(tid)
        per_task.append(
            {
                "task_id": tid,
                "title": _task_display_title(tm, tid),
                "task_type": _public_task_type(tm.task_type) if tm else "unknown",
                "attempts": attempts,
                "success_rate": round(100.0 * wins / attempts, 1) if attempts else 0.0,
                "solved": any(x.success is True for x in lst),
            }
        )

    by_type: dict[str, dict[str, int]] = defaultdict(
        lambda: {"attempts": 0, "successes": 0}
    )
    for tid, lst in task_attempts.items():
        tm = task_map.get(tid)
        ttype = _public_task_type(tm.task_type) if tm else "unknown"
        by_type[ttype]["attempts"] += len(lst)
        by_type[ttype]["successes"] += sum(1 for x in lst if x.success is True)

    task_type_stats = [
        {
            "task_type": ttype,
            "attempts": data["attempts"],
            "success_rate": round(
                100.0 * data["successes"] / data["attempts"], 1
            )
            if data["attempts"]
            else 0.0,
        }
        for ttype, data in sorted(by_type.items())
    ]

    errors = _error_breakdown(subs)
    student_recommendations = get_student_recommendations(db, uid)
    recommendations = recommendations_to_legacy_list(student_recommendations)

    return {
        "overview": {
            "total_tasks": total_tasks,
            "solved_count": solved_count,
            "completion_percent": completion_pct,
            "level": level,
            "success_rate": success_rate,
            "total_submissions": total_submissions,
        },
        "by_language": language_progress,
        "by_structure": skill_progress,
        "recent_activity": recent_activity,
        "per_task": per_task,
        "by_task_type": task_type_stats,
        "error_breakdown": errors,
        "student_recommendations": student_recommendations,
        "recommendations": recommendations,
        "languages_progress": student_recommendations.get("by_language") or {},
        "tc_skills": tc_skills,
        "tc_skills_by_language": tc_skills_by_language,
        "tc_skill_groups": tc_skill_groups,
        "tc_skill_groups_by_language": tc_skill_groups_by_language,
        "tc_skill_languages": tc_skill_languages,
        "tc_skills_default_language": default_tc_language,
        "tc_task_recommendations": tc_task_recommendations,
        "tc_task_recommendations_by_language": tc_task_recommendations_by_language,
        "streak_days": student_recommendations.get("streak", {}).get("days", 0),
        "assumptions": [
            "Прогресс по навыкам (tc_skills): display TC из tc_display_registry по выбранному языку курса; "
            "процент = решённые слоты с TC / все слоты курса с TC для этого языка.",
            "tc_skills_by_language: тот же расчёт отдельно для каждого трека (pascal, python, cpp, …).",
            "Рекомендации (tc_task_recommendations): нерешённые задачи по слабым display TC (total≥3, percent<40).",
            "Прогресс по структурам (by_structure): группы концепций из constructions.",
            "Категории ошибок: синтаксис (компилятор/линтер), логика (тесты/паттерны), runtime (INTERNAL_ERROR или текст исключения).",
        ],
    }


def _teacher_task_catalog_map(db: Session, teacher_id: int) -> dict[int, list[dict[str, Any]]]:
    rows = (
        db.query(Collection)
        .filter(
            Collection.teacher_id == teacher_id,
            Collection.is_archived.is_(False),
        )
        .all()
    )
    out: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for cat in rows:
        deadline_at = cat.deadline_at
        if deadline_at is not None and deadline_at.tzinfo is None:
            deadline_at = deadline_at.replace(tzinfo=timezone.utc)
        for tid in _catalog_task_ids(db, cat.id):
            out[tid].append(
                {
                    "catalog_id": cat.id,
                    "catalog_title": cat.name,
                    "deadline_at": deadline_at,
                    "group_id": cat.group_id,
                }
            )
    return out


def _submission_catalog_meta(
    submission: Submission,
    catalogs_for_task: list[dict[str, Any]],
    *,
    catalog_id: int | None = None,
) -> tuple[int | None, str | None, bool]:
    if not catalogs_for_task:
        return None, None, False
    chosen = catalogs_for_task
    if catalog_id is not None:
        chosen = [c for c in catalogs_for_task if c["catalog_id"] == catalog_id]
        if not chosen:
            return None, None, False
    cat = chosen[0]
    is_late = False
    if submission.created_at and cat.get("deadline_at"):
        created = submission.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        is_late = created > cat["deadline_at"]
    return cat["catalog_id"], cat["catalog_title"], is_late


def list_teacher_submissions(
    db: Session,
    teacher_id: int,
    *,
    task_id: int | None = None,
    student_id: int | None = None,
    group_id: int | None = None,
    catalog_id: int | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    teacher_task_ids = _teacher_task_ids(db, teacher_id)
    if not teacher_task_ids:
        return []

    group_student_ids = _teacher_group_student_ids(db, teacher_id)
    if not group_student_ids:
        return []

    student_filter: set[int] | None = group_student_ids
    if group_id is not None:
        group = db.get(Group, group_id)
        if group is None or group.teacher_id != teacher_id:
            return []
        group_members = set(
            db.execute(
                select(group_member_association_table.c.student_id).where(
                    group_member_association_table.c.group_id == group_id
                )
            ).scalars().all()
        )
        student_filter = group_student_ids & group_members
    if student_id is not None:
        if student_id not in group_student_ids:
            return []
        student_filter = (
            {student_id}
            if student_filter is None
            else student_filter & {student_id}
        )

    q = db.query(Submission).filter(Submission.task_id.in_(teacher_task_ids))
    if task_id is not None:
        q = q.filter(Submission.task_id == task_id)
    if student_id is not None:
        q = q.filter(Submission.user_id == student_id)
    if student_filter is not None:
        if not student_filter:
            return []
        q = q.filter(Submission.user_id.in_(student_filter))

    rows = (
        q.order_by(Submission.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )

    user_ids = {r.user_id for r in rows if r.user_id}
    task_ids = {r.task_id for r in rows}
    users = {
        u.id: u
        for u in db.query(User).filter(User.id.in_(user_ids)).all()
    } if user_ids else {}
    from application.users.services.study_identity import load_study_identity_by_user_ids

    study_by_user = load_study_identity_by_user_ids(db, list(user_ids)) if user_ids else {}
    tasks = _load_task_map(db, task_ids)
    task_catalog_map = _teacher_task_catalog_map(db, teacher_id)

    out: list[dict[str, Any]] = []
    for s in rows:
        tm = tasks.get(s.task_id)
        user = users.get(s.user_id) if s.user_id else None
        study = study_by_user.get(
            s.user_id or 0,
            {"study_place": None, "study_group": None, "study_identity": None},
        )
        cat_id, cat_title, is_late = _submission_catalog_meta(
            s,
            task_catalog_map.get(s.task_id, []),
            catalog_id=catalog_id,
        )
        if catalog_id is not None and cat_id is None:
            continue
        out.append(
            {
                "id": s.id,
                "task_id": s.task_id,
                "task_title": _task_display_title(tm, s.task_id),
                "task_type": _public_task_type(tm.task_type) if tm else None,
                "student_id": s.user_id,
                "student_name": user.name if user else "—",
                "study_place": study["study_place"],
                "study_group": study["study_group"],
                "study_identity": study["study_identity"],
                "language": _normalize_language(s.language),
                "status": s.status,
                "success": s.success,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "catalog_id": cat_id,
                "catalog_title": cat_title,
                "is_late": is_late,
            }
        )
    return out


def build_teacher_analytics(db: Session, teacher_id: int) -> dict[str, Any]:
    teacher_task_ids = _teacher_task_ids(db, teacher_id)
    group_student_ids = _teacher_group_student_ids(db, teacher_id)

    subs: list[Submission] = []
    if teacher_task_ids:
        subs = (
            db.query(Submission)
            .options(
                joinedload(Submission.linter_errors),
                joinedload(Submission.pattern_errors),
                joinedload(Submission.test_results),
            )
            .filter(Submission.task_id.in_(teacher_task_ids))
            .all()
        )

    task_map = _load_task_map(db, teacher_task_ids)
    by_task_subs: dict[int, list[Submission]] = defaultdict(list)
    for s in subs:
        by_task_subs[s.task_id].append(s)

    per_assignment = []
    for tid in sorted(teacher_task_ids):
        tm = task_map.get(tid)
        lst = by_task_subs.get(tid, [])
        if not lst:
            continue
        students = {s.user_id for s in lst if s.user_id}
        attempts = len(lst)
        successes = sum(1 for s in lst if s.success is True)
        per_assignment.append(
            {
                "task_id": tid,
                "title": _task_display_title(tm, tid),
                "difficulty": tm.difficulty if tm else "unknown",
                "task_type": _public_task_type(tm.task_type) if tm else "unknown",
                "success_percent": round(100.0 * successes / attempts, 1),
                "avg_attempts": round(attempts / max(len(students), 1), 1),
                "student_count": len(students),
                "total_submissions": attempts,
                "error_breakdown": _error_breakdown(lst),
            }
        )

    by_type: dict[str, dict[str, int]] = defaultdict(
        lambda: {"submissions": 0, "successes": 0}
    )
    for s in subs:
        tm = task_map.get(s.task_id)
        ttype = _public_task_type(tm.task_type) if tm else "unknown"
        by_type[ttype]["submissions"] += 1
        if s.success is True:
            by_type[ttype]["successes"] += 1

    task_type_success = [
        {
            "task_type": ttype,
            "submissions": data["submissions"],
            "success_rate": round(
                100.0 * data["successes"] / data["submissions"], 1
            )
            if data["submissions"]
            else 0.0,
        }
        for ttype, data in sorted(by_type.items())
    ]

    groups = db.query(Group).filter(Group.teacher_id == teacher_id).all()
    group_stats = []
    for group in groups:
        member_ids = set(
            db.execute(
                select(group_member_association_table.c.student_id).where(
                    group_member_association_table.c.group_id == group.id
                )
            ).scalars().all()
        )
        member_subs = [s for s in subs if s.user_id in member_ids]
        if not member_subs and not member_ids:
            group_stats.append(
                {
                    "group_id": group.id,
                    "name": group.name,
                    "member_count": 0,
                    "avg_progress_percent": 0.0,
                    "weak_topics": [],
                }
            )
            continue
        solved_tasks = {
            s.task_id
            for s in member_subs
            if s.success is True and s.user_id in member_ids
        }
        progress_pct = (
            round(100.0 * len(solved_tasks) / len(teacher_task_ids), 1)
            if teacher_task_ids
            else 0.0
        )
        weak: dict[str, int] = defaultdict(int)
        for s in member_subs:
            if s.success is True:
                continue
            tm = task_map.get(s.task_id)
            if not tm:
                continue
            for bid in _structure_keys_for_task(
                tm, _task_constructions(db, tm)
            ):
                weak[bid] += 1
        weak_topics = [
            STRUCTURE_BUCKETS[b]["label"]
            for b, _ in sorted(weak.items(), key=lambda x: -x[1])[:3]
        ]
        group_stats.append(
            {
                "group_id": group.id,
                "name": group.name,
                "member_count": len(member_ids),
                "avg_progress_percent": progress_pct,
                "weak_topics": weak_topics,
            }
        )

    student_rows = []
    if group_student_ids:
        users = {
            u.id: u
            for u in db.query(User).filter(User.id.in_(group_student_ids)).all()
        }
        for sid in sorted(group_student_ids):
            student_subs = [s for s in subs if s.user_id == sid]
            solved = {
                s.task_id for s in student_subs if s.success is True
            }
            progress_pct = (
                round(100.0 * len(solved) / len(teacher_task_ids), 1)
                if teacher_task_ids
                else 0.0
            )
            weak: dict[str, int] = defaultdict(int)
            for s in student_subs:
                if s.success is True:
                    continue
                tm = task_map.get(s.task_id)
                if not tm:
                    continue
                for bid in _structure_keys_for_task(
                    tm, _task_constructions(db, tm)
                ):
                    weak[bid] += 1
            last_at = max(
                (s.created_at for s in student_subs if s.created_at),
                default=None,
            )
            student_rows.append(
                {
                    "student_id": sid,
                    "name": users[sid].name if sid in users else f"Студент #{sid}",
                    "progress_percent": progress_pct,
                    "solved_count": len(solved),
                    "submissions_count": len(student_subs),
                    "weak_topics": [
                        STRUCTURE_BUCKETS[b]["label"]
                        for b, _ in sorted(weak.items(), key=lambda x: -x[1])[:3]
                    ],
                    "last_activity_at": last_at.isoformat() if last_at else None,
                }
            )

    now = datetime.now(timezone.utc)
    cut7 = now - timedelta(days=7)
    cut14 = now - timedelta(days=14)
    cut30 = now - timedelta(days=30)
    cut60 = now - timedelta(days=60)

    def _success_rate(sub_list: list[Submission]) -> float:
        if not sub_list:
            return 0.0
        wins = sum(1 for s in sub_list if s.success is True)
        return round(100.0 * wins / len(sub_list), 1)

    subs_last30 = [s for s in subs if s.created_at and s.created_at >= cut30]
    subs_prev30 = [s for s in subs if s.created_at and cut60 <= s.created_at < cut30]

    submissions_by_date: dict[str, int] = {}
    for s in subs:
        if not s.created_at:
            continue
        key = s.created_at.astimezone(timezone.utc).date().isoformat()
        submissions_by_date[key] = submissions_by_date.get(key, 0) + 1

    active_last7 = {
        s.user_id
        for s in subs
        if s.user_id in group_student_ids and s.created_at and s.created_at >= cut7
    }
    active_prev7 = {
        s.user_id
        for s in subs
        if s.user_id in group_student_ids and s.created_at and cut14 <= s.created_at < cut7
    }

    summary = {
        "student_count": len(student_rows),
        "students_active_last_7": len(active_last7),
        "students_weekly_delta": len(active_last7) - len(active_prev7),
        "active_tasks": len(per_assignment),
        "avg_success_rate": _success_rate(subs),
        "avg_success_rate_delta_month": round(
            _success_rate(subs_last30) - _success_rate(subs_prev30), 1
        )
        if subs_prev30
        else 0.0,
    }

    return {
        "summary": summary,
        "submissions_by_date": submissions_by_date,
        "per_assignment": per_assignment,
        "task_type_success": task_type_success,
        "groups": group_stats,
        "students": student_rows,
        "error_breakdown_overall": _error_breakdown(subs),
        "assumptions": [
            "Аналитика только по задачам с teacher_id текущего преподавателя.",
            "Студенты в отчёте — участники групп преподавателя.",
        ],
    }
