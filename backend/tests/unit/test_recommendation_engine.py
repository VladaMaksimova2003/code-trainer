from __future__ import annotations

import pytest

from domain.services.business.recommendation_engine import (
    available_topics,
    build_rec_task,
    manual_next_task,
    manual_prev_task,
    recommend_next_task,
    update_student_state,
)
from domain.entities.learning.recommendation import RecTask, StudentState


def _task(
    task_id: int,
    topic_id: int,
    type_id: str = "algorithm",
    skills: tuple[str, ...] = ("for_loop", "binary_expression"),
    collection_id: int | None = None,
) -> RecTask:
    return RecTask(
        id=task_id,
        topic_id=topic_id,
        type_id=type_id,
        skills_required=skills,
        created_by_teacher=False,
        collection_id=collection_id,
    )


def test_manual_navigation_order():
    order = [10, 20, 30]
    assert manual_next_task(order, 10) == 20
    assert manual_next_task(order, 30) is None
    assert manual_prev_task(order, 20) == 10
    assert manual_prev_task(order, 10) is None


def test_update_student_state_tracks_mastery():
    state = StudentState()
    task = _task(1, topic_id=1, skills=("binary_expression",))
    update_student_state(state, task, success=True)
    assert state.skill_mastery["binary_expression"] > 0
    assert 1 in state.topic_mastery
    assert state.solved_task_ids == {1}


def test_available_topics_respects_prerequisites():
    state = StudentState()
    state.topic_mastery[1] = 0.8
    topics = available_topics(state)
    topic_ids = {t.id for t in topics}
    assert 1 in topic_ids
    assert 2 in topic_ids
    assert 5 not in topic_ids


def test_recommend_skips_collection_tasks():
    state = StudentState()
    tasks = [
        _task(1, 1, collection_id=99),
        _task(2, 1, collection_id=None),
        _task(3, 1, collection_id=None),
    ]
    picked = recommend_next_task(state, tasks, current_task_id=None)
    assert picked is not None
    assert picked.collection_id is None


def test_recommend_prefers_unsolved_with_skill_overlap():
    state = StudentState()
    first = _task(1, 1, skills=("binary_expression",))
    update_student_state(state, first, success=True)

    tasks = [
        first,
        _task(2, 1, skills=("binary_expression", "for_loop")),
        _task(3, 3, skills=("nested_loops",)),
    ]
    picked = recommend_next_task(state, tasks, current_task_id=1)
    assert picked is not None
    assert picked.id == 2


def test_recommend_avoids_recent_repetition():
    state = StudentState()
    task = _task(5, 1)
    update_student_state(state, task, success=False)
    picked = recommend_next_task(state, [task], current_task_id=5)
    assert picked is None


def test_build_rec_task_infers_topic_from_skills():
    rec = build_rec_task(
        task_id=7,
        topic_id=None,
        type_id="algorithm",
        skills=["if_statement"],
        created_by_teacher=True,
        collection_id=None,
    )
    assert rec.topic_id == 2
