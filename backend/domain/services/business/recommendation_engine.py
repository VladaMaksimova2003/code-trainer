from __future__ import annotations

from domain.entities.learning.recommendation import (
    HistoryEntry,
    RecTask,
    StudentState,
    TaskType,
    Topic,
)
from domain.services.business.concept_graph import (
    needs_review,
    prerequisites_for_struggling,
    skill_learning_state,
    task_covers_weak_prerequisites,
    task_has_struggling_skill,
    zpd_score,
)
from domain.services.business.recommendation_metadata import (
    infer_topic_id,
    load_skill_to_topic,
    load_skills,
    load_task_types,
    load_topics,
)

PREREQUISITE_THRESHOLD = 0.6
TYPE_READINESS_THRESHOLD = 0.7
MASTERED_SKILL_THRESHOLD = 0.7


def update_student_state(
    state: StudentState,
    task: RecTask,
    *,
    success: bool,
) -> None:
    """Update mastery maps after a task attempt."""
    result = 1.0 if success else 0.0
    alpha = 0.35

    for skill in task.skills_required:
        prev = state.skill_mastery.get(skill, 0.0)
        state.skill_mastery[skill] = prev * (1 - alpha) + result * alpha

        # Отслеживаем количество попыток и серию провалов per skill.
        state.skill_attempt_count[skill] = state.skill_attempt_count.get(skill, 0) + 1
        if success:
            state.skill_fail_streak[skill] = 0        # Успех сбрасывает серию
        else:
            streak = state.skill_fail_streak.get(skill, 0)
            state.skill_fail_streak[skill] = streak + 1

    topic_id = task.topic_id
    topic_skills = _topic_skill_ids(topic_id)
    if topic_skills:
        values = [state.skill_mastery.get(s, 0.0) for s in topic_skills]
        state.topic_mastery[topic_id] = sum(values) / len(values)
    else:
        prev = state.topic_mastery.get(topic_id, 0.0)
        state.topic_mastery[topic_id] = prev * (1 - alpha) + result * alpha

    state.history.append(
        HistoryEntry(
            task_id=task.id,
            topic_id=task.topic_id,
            skills=task.skills_required,
            type_id=task.type_id,
            success=success,
        )
    )
    if len(state.history) > 30:
        state.history = state.history[-30:]

    if success:
        state.solved_task_ids.add(task.id)
    state.last_type_id = task.type_id


def _topic_skill_ids(topic_id: int) -> list[str]:
    topics = load_topics()
    topic = topics.get(topic_id)
    return list(topic.skills) if topic else []


def _mastery(state: StudentState, key: str | int, store: dict) -> float:
    return float(store.get(key, 0.0))


def available_topics(state: StudentState) -> list[Topic]:
    topics = load_topics()
    result: list[Topic] = []
    for topic in topics.values():
        if not topic.prerequisites:
            result.append(topic)
            continue
        prereq_levels = [
            _mastery(state, pid, state.topic_mastery) for pid in topic.prerequisites
        ]
        if prereq_levels and min(prereq_levels) >= PREREQUISITE_THRESHOLD:
            result.append(topic)
    return result


def topic_readiness(state: StudentState, topic: Topic) -> float:
    if not topic.skills:
        return _mastery(state, topic.id, state.topic_mastery)
    return min(_mastery(state, s, state.skill_mastery) for s in topic.skills)


def type_readiness(state: StudentState, task_type: TaskType) -> float:
    if not task_type.required_skills:
        return 1.0
    return min(
        _mastery(state, s, state.skill_mastery) for s in task_type.required_skills
    )


def type_is_available(state: StudentState, task_type: TaskType) -> bool:
    return type_readiness(state, task_type) > TYPE_READINESS_THRESHOLD


def _type_transition_weight(
    state: StudentState,
    current_type: str | None,
    candidate_type: str,
) -> float:
    """Blend probability between current and candidate task type."""
    if current_type is None or current_type == candidate_type:
        return 1.0

    task_types = load_task_types()
    current = task_types.get(current_type)
    candidate = task_types.get(candidate_type)
    if candidate is None:
        return 0.0
    if current is None:
        return 1.0 if type_is_available(state, candidate) else 0.0

    readiness = type_readiness(state, candidate)
    if readiness <= TYPE_READINESS_THRESHOLD:
        return 1.0 if candidate_type == current_type else 0.0
    if readiness < 0.85:
        return 0.7 if candidate_type == current_type else 0.3
    if readiness < 0.95:
        return 0.5
    if readiness < 1.0:
        return 0.3 if candidate_type == current_type else 0.7
    return 1.0


def select_target_topic(
    state: StudentState,
    *,
    last_task: RecTask | None,
) -> Topic | None:
    candidates = available_topics(state)
    if not candidates:
        return None

    failed_topics: set[int] = set()
    for entry in reversed(state.history[-5:]):
        if not entry.success:
            failed_topics.add(entry.topic_id)

    def score(topic: Topic) -> tuple[float, float, float]:
        mastery = _mastery(state, topic.id, state.topic_mastery)
        weak_bonus = 1.0 - mastery
        recent_fail = 1.0 if topic.id in failed_topics else 0.0
        related = (
            1.0
            if last_task and topic.id == last_task.topic_id
            else 0.0
        )
        return (weak_bonus, recent_fail, related)

    return max(candidates, key=score)


def select_task_type(
    state: StudentState,
    target_topic: Topic,
    *,
    last_task: RecTask | None,
) -> str | None:
    task_types = load_task_types()
    topic_skills = set(target_topic.skills)
    last_type = last_task.type_id if last_task else state.last_type_id

    scored: list[tuple[float, str]] = []
    for task_type in task_types.values():
        if not type_is_available(state, task_type):
            continue
        overlap = len(topic_skills & set(task_type.required_skills))
        diversity = 0.0 if task_type.id == last_type else 0.5
        transition = _type_transition_weight(state, last_type, task_type.id)
        if transition <= 0:
            continue
        scored.append(
            (overlap * 0.4 + diversity * 0.3 + transition * 0.3, task_type.id)
        )

    if not scored:
        for task_type in task_types.values():
            readiness = type_readiness(state, task_type)
            if readiness >= 0.3:
                scored.append((readiness, task_type.id))
    if not scored:
        return last_type or "algorithm"
    return max(scored, key=lambda item: item[0])[1]


def _progressive_skill_match(
    state: StudentState,
    task: RecTask,
    last_skills: set[str],
) -> bool:
    task_skills = set(task.skills_required)
    if not last_skills:
        return True
    overlap = task_skills & last_skills
    if not overlap:
        return False
    new_skills = task_skills - last_skills
    if len(new_skills) > 1:
        return False
    known = task_skills & {
        s for s, m in state.skill_mastery.items() if m >= MASTERED_SKILL_THRESHOLD
    }
    if len(known) >= 2 and len(new_skills) == 0:
        return True
    if len(known) >= 1 and len(new_skills) <= 1:
        return True
    return len(new_skills) <= 1


def score_task(
    state: StudentState,
    task: RecTask,
    *,
    target_topic: Topic,
    last_task: RecTask | None,
    selected_type: str | None,
) -> float:
    last_skills = set(last_task.skills_required) if last_task else set()
    task_skills = set(task.skills_required)

    skill_match = 0.0
    for skill in task_skills:
        skill_match += _mastery(state, skill, state.skill_mastery)
    skill_match = skill_match / max(len(task_skills), 1)

    topic_need = 1.0 - _mastery(state, target_topic.id, state.topic_mastery)

    overlap = len(task_skills & last_skills) / max(len(last_skills), 1) if last_skills else 0.5
    previous_context_overlap = overlap

    type_diversity_bonus = 0.5 if task.type_id != (last_task.type_id if last_task else state.last_type_id) else 0.0

    # --- Learning state: различаем «застрял», «забыл», «ещё не учил» ---
    #
    # Для каждого навыка в задании определяем состояние студента.
    # Это меняет логику scoring:
    #
    #  struggling (серия >= 3 провалов):
    #    - само задание получает штраф — давить на застрявший концепт бесполезно
    #    - если задание покрывает weak prerequisites застрявшего навыка → большой буст
    #
    #  forgotten (были попытки, mastery упал < 0.3):
    #    - задание получает буст как у spaced repetition (приоритет выше чем "learning")
    #
    #  never_learned (ноль попыток):
    #    - чистое ZPD без дополнительных модификаторов

    struggling_skills: set[str] = {
        s for s in task_skills
        if skill_learning_state(
            s, state.skill_mastery, state.skill_attempt_count, state.skill_fail_streak
        ) == "struggling"
    }

    forgotten_skills: set[str] = {
        s for s in task_skills
        if skill_learning_state(
            s, state.skill_mastery, state.skill_attempt_count, state.skill_fail_streak
        ) == "forgotten"
    }

    # Штраф если задание содержит навыки где студент застрял
    struggling_penalty = -0.9 * len(struggling_skills) / max(len(task_skills), 1)

    # Буст если задание тренирует prerequisites для застрявших навыков
    # (т.е. помогает «разблокировать» застрявший концепт)
    all_struggling: set[str] = {
        s for s in state.skill_fail_streak
        if state.skill_fail_streak.get(s, 0) >= 3
    }
    prerequisite_boost = (
        0.8
        if all_struggling and task_covers_weak_prerequisites(
            task.skills_required, all_struggling, state.skill_mastery
        )
        else 0.0
    )

    # Буст для забытых навыков (активное повторение)
    forgotten_boost = 0.6 * len(forgotten_skills) / max(len(task_skills), 1)

    # --- Spaced repetition (улучшенный) ---
    repetition_score = 0.0
    if task.id in state.solved_task_ids:
        if needs_review(task.id, task.skills_required, state.skill_mastery, state.solved_task_ids):
            repetition_score = 0.5
        else:
            repetition_score = -0.8

    recent_ids = {h.task_id for h in state.history[-3:]}
    if task.id in recent_ids:
        repetition_score -= 0.5

    type_bonus = 0.3 if selected_type and task.type_id == selected_type else 0.0

    # --- ZPD (Zone of Proximal Development) ---
    difficulty_bonus = zpd_score(task.skills_required, state.skill_mastery)

    if not _progressive_skill_match(state, task, last_skills):
        return -1.0

    return (
        skill_match * 1.0
        + topic_need * 1.2
        + previous_context_overlap * 0.8
        + type_diversity_bonus * 0.4
        + type_bonus
        + difficulty_bonus * 0.9
        + repetition_score
        + struggling_penalty
        + prerequisite_boost
        + forgotten_boost
    )


def recommend_next_task(
    state: StudentState,
    tasks: list[RecTask],
    *,
    current_task_id: int | None = None,
    exclude_collection_tasks: bool = True,
) -> RecTask | None:
    """Pick the best next task in adaptive mode."""
    pool = [
        t
        for t in tasks
        if not exclude_collection_tasks or t.collection_id is None
    ]
    if not pool and tasks:
        pool = list(tasks)

    last_task = None
    if current_task_id is not None:
        last_task = next((t for t in tasks if t.id == current_task_id), None)
    if last_task is None and state.history:
        last_id = state.history[-1].task_id
        last_task = next((t for t in tasks if t.id == last_id), None)

    target = select_target_topic(state, last_task=last_task)
    if target is None:
        unsolved = [t for t in pool if t.id not in state.solved_task_ids]
        return unsolved[0] if unsolved else (pool[0] if pool else None)

    selected_type = select_task_type(state, target, last_task=last_task)

    candidates = [
        t
        for t in pool
        if t.topic_id == target.id or t.id not in state.solved_task_ids
    ]
    if not candidates:
        candidates = pool

    scored: list[tuple[float, RecTask]] = []
    for task in candidates:
        if task.id == current_task_id:
            continue
        value = score_task(
            state,
            task,
            target_topic=target,
            last_task=last_task,
            selected_type=selected_type,
        )
        if value >= 0:
            scored.append((value, task))

    if not scored:
        fallback = [t for t in pool if t.id != current_task_id]
        return fallback[0] if fallback else None

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def build_rec_task(
    *,
    task_id: int,
    topic_id: int | None,
    type_id: str,
    skills: list[str],
    created_by_teacher: bool,
    collection_id: int | None,
) -> RecTask:
    skill_to_topic = load_skill_to_topic()
    resolved_topic = infer_topic_id(topic_id, skills, skill_to_topic)
    normalized_type = _normalize_type_id(type_id)
    known_skills = set(load_skills())
    filtered = tuple(s for s in skills if s in known_skills) or tuple(skills)
    return RecTask(
        id=task_id,
        topic_id=resolved_topic,
        type_id=normalized_type,
        skills_required=filtered,
        created_by_teacher=created_by_teacher,
        collection_id=collection_id,
    )


def _normalize_type_id(raw: str) -> str:
    aliases = {
        "diagram": "blocks",
        "code_assembly": "block_reorder",
        "task_build_from_blocks": "block_reorder",
    }
    return aliases.get(raw, raw)


def manual_next_task(
    ordered_task_ids: list[int],
    current_task_id: int,
) -> int | None:
    try:
        index = ordered_task_ids.index(current_task_id)
    except ValueError:
        return ordered_task_ids[0] if ordered_task_ids else None
    if index + 1 < len(ordered_task_ids):
        return ordered_task_ids[index + 1]
    return None


def manual_prev_task(
    ordered_task_ids: list[int],
    current_task_id: int,
) -> int | None:
    try:
        index = ordered_task_ids.index(current_task_id)
    except ValueError:
        return None
    if index > 0:
        return ordered_task_ids[index - 1]
    return None
