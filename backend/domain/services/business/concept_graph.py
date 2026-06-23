"""
ConceptGraph -- graff slozhnosti kontseptov.

Istochniki:
  - resources/hints/structures.yml   -> difficulty (1-3) per subtype
  - _CROSS_CORE_PREREQUISITES        -> yavnye zavisimosti mezhdu kontseptami

Vnutri kazhdoy core-struktury podtipy upora-dovany po difficulty:
  for_loop(1) -> foreach(2) -> nested_loop(3)
  function(1)  -> method(2)  -> lambda(3)
  direct_call(1) -> method_call(2) -> chained_call(3)

Dopolnitelno yavnye cross-core zavisimosti:
  lambda        trebuet function + foreach
  method        trebuet function
  chained_call  trebuet method_call + method
  method_call   trebuet direct_call + function
  nested_loops  trebuet for_loop + foreach

Publichny API:
  get_difficulty(skill_id)
  get_concept_prerequisites(skill_id)
  student_skill_level(skill_mastery)
  zpd_score(task_skills, skill_mastery)
  skill_learning_state(...)
  prerequisites_for_struggling(...)
  task_has_struggling_skill(...)
  task_covers_weak_prerequisites(...)
  needs_review(...)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

_STRUCTURES_PATH = (
    Path(__file__).resolve().parents[3] / "resources" / "hints" / "structures.yml"
)

_CROSS_CORE_PREREQUISITES: dict[str, list[str]] = {
    "lambda":       ["function", "foreach"],
    "method":       ["function"],
    "method_call":  ["direct_call", "function"],
    "chained_call": ["method_call", "method"],
    "nested_loop":  ["for_loop", "foreach"],
    "nested_loops": ["for_loop", "foreach"],
}

_SKILL_ALIASES: dict[str, str] = {
    "nested_loops": "nested_loop",
    "for_loop": "for_loop",
    "while_loop": "while_loop",
    "foreach": "foreach",
    "function_definition": "function",
    "function": "function",
    "method": "method",
    "lambda": "lambda",
    "if_statement": "if",
    "condition": "if",
    "return_statement": "return",
    "return": "return",
    "binary_expression": "assignment",
    "assignment": "assignment",
    "direct_call": "direct_call",
    "method_call": "method_call",
    "chained_call": "chained_call",
}

_MASTERED_THRESHOLD = 0.65
_STRUGGLING_STREAK = 3


@dataclass(frozen=True)
class ConceptNode:
    id: str
    core: str
    difficulty: int
    title: str
    prerequisites: tuple[str, ...] = field(default_factory=tuple)


@lru_cache(maxsize=1)
def load_concept_graph() -> dict[str, ConceptNode]:
    try:
        with _STRUCTURES_PATH.open(encoding="utf-8") as f:
            raw: dict = yaml.safe_load(f) or {}
    except OSError:
        return {}

    nodes: dict[str, ConceptNode] = {}

    for core_name, subtypes in raw.items():
        if not isinstance(subtypes, dict):
            continue

        ordered = sorted(
            subtypes.items(),
            key=lambda kv: kv[1].get("difficulty", 1) if isinstance(kv[1], dict) else 1,
        )

        prev_id: str | None = None
        for subtype_id, data in ordered:
            if not isinstance(data, dict):
                continue

            difficulty = int(data.get("difficulty", 1))
            title = str(data.get("title", subtype_id))
            prereqs: tuple[str, ...] = (prev_id,) if prev_id is not None else ()

            nodes[subtype_id] = ConceptNode(
                id=subtype_id,
                core=core_name,
                difficulty=difficulty,
                title=title,
                prerequisites=prereqs,
            )
            prev_id = subtype_id

    return nodes


def _resolve(skill_id: str) -> str:
    return _SKILL_ALIASES.get(skill_id, skill_id)


def get_difficulty(skill_id: str) -> int:
    graph = load_concept_graph()
    canonical = _resolve(skill_id)
    node = graph.get(canonical)
    if node:
        return node.difficulty
    stripped = skill_id.rstrip("s") if skill_id.endswith("s") else None
    if stripped and stripped != skill_id:
        node = graph.get(stripped)
        if node:
            return node.difficulty
    return 1


def get_concept_prerequisites(skill_id: str) -> list[str]:
    graph = load_concept_graph()
    canonical = _resolve(skill_id)

    seen: set[str] = set()
    result: list[str] = []

    node = graph.get(canonical)
    if node:
        for p in node.prerequisites:
            if p not in seen:
                seen.add(p)
                result.append(p)

    for cross_prereq in _CROSS_CORE_PREREQUISITES.get(canonical, []):
        resolved = _resolve(cross_prereq)
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)

    return result


def student_skill_level(skill_mastery: dict[str, float]) -> float:
    if not skill_mastery:
        return 1.0

    total_weight = 0.0
    weighted_sum = 0.0

    for skill_id, mastery in skill_mastery.items():
        if mastery < 0.4:
            continue
        difficulty = get_difficulty(skill_id)
        weight = 1.0 if mastery >= 0.7 else 0.5
        weighted_sum += difficulty * weight
        total_weight += weight

    if total_weight == 0.0:
        return 1.0

    return weighted_sum / total_weight


def zpd_score(task_skills: tuple[str, ...], skill_mastery: dict[str, float]) -> float:
    if not task_skills:
        return 0.5

    student_level = student_skill_level(skill_mastery)
    task_difficulty = max(get_difficulty(s) for s in task_skills)
    gap = task_difficulty - student_level

    if gap > 1.0:
        return -0.5
    elif gap > 0.3:
        return 1.0
    elif gap > -0.3:
        return 0.7
    elif gap > -1.0:
        return 0.3
    else:
        return 0.0


def needs_review(
    task_id: int,
    task_skills: tuple[str, ...],
    skill_mastery: dict[str, float],
    solved_task_ids: set[int],
) -> bool:
    if task_id not in solved_task_ids:
        return False
    if not task_skills:
        return False
    avg_mastery = sum(skill_mastery.get(s, 0.0) for s in task_skills) / len(task_skills)
    return avg_mastery < 0.55


def skill_learning_state(
    skill_id: str,
    skill_mastery: dict[str, float],
    skill_attempt_count: dict[str, int],
    skill_fail_streak: dict[str, int],
) -> str:
    """
    Vozvraschaet tekushchee sostoyanie studenta po navyku.

    Sostoyaniya:
      never_learned  -- nol popytok
      learning       -- v protsesse, progress est
      struggling     -- > =3 failov podryad: shag nazad k prerequisites
      forgotten      -- byli popytki, mastery upal nizhe 0.3
      mastered       -- mastery >= 0.65
    """
    mastery = skill_mastery.get(skill_id, 0.0)
    attempts = skill_attempt_count.get(skill_id, 0)
    streak = skill_fail_streak.get(skill_id, 0)

    if attempts == 0:
        return "never_learned"
    if mastery >= _MASTERED_THRESHOLD:
        return "mastered"
    if streak >= _STRUGGLING_STREAK:
        return "struggling"
    if attempts > 0 and mastery < 0.3:
        return "forgotten"
    return "learning"


def prerequisites_for_struggling(
    skill_id: str,
    skill_mastery: dict[str, float],
) -> list[str]:
    """
    Vozvraschaet prerequisites dannogo navyka kotorye eshche ne osvoeny.
    Ispolzuetsya kogda student zastrial.
    """
    prereqs = get_concept_prerequisites(skill_id)
    return [
        p for p in prereqs
        if skill_mastery.get(p, 0.0) < _MASTERED_THRESHOLD
    ]


def task_has_struggling_skill(
    task_skills: tuple[str, ...],
    skill_mastery: dict[str, float],
    skill_attempt_count: dict[str, int],
    skill_fail_streak: dict[str, int],
) -> bool:
    return any(
        skill_learning_state(s, skill_mastery, skill_attempt_count, skill_fail_streak) == "struggling"
        for s in task_skills
    )


def task_covers_weak_prerequisites(
    task_skills: tuple[str, ...],
    struggling_skills: set[str],
    skill_mastery: dict[str, float],
) -> bool:
    """
    True esli zadanie treniruet prerequisites dlya navykov gde student zastrial.
    Ispolzuetsya dlya busta zadaniy kotorye pomogut razblokirovat zastrevshie kontsepty.
    """
    for struggling in struggling_skills:
        weak_prereqs = set(prerequisites_for_struggling(struggling, skill_mastery))
        if weak_prereqs & set(task_skills):
            return True
    return False
