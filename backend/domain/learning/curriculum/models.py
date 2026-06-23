"""Curriculum v2 domain models (YAML-backed, no DB)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LearningConcept:
    id: str
    name_ru: str
    tier: str
    order: int
    description_ru: str = ""


@dataclass(frozen=True)
class TechnicalConcept:
    id: str
    learning_concept_id: str
    name_ru: str
    tier: str
    notes: str = ""
    optional_in_track: bool = False


@dataclass(frozen=True)
class ExercisePattern:
    id: str
    action: str
    description_ru: str = ""
    grading: str = ""
    legacy_adapter: str | None = None
    source: dict | None = None
    target: dict | None = None
    transfer: dict | None = None


@dataclass(frozen=True)
class TechnicalConceptActionMask:
    technical_concept_id: str
    required_actions: tuple[str, ...]
    optional_actions: tuple[str, ...] = ()
    disabled_actions: tuple[str, ...] = ()
    required_patterns_by_action: dict[str, tuple[str, ...]] = field(default_factory=dict)
    optional_patterns_by_action: dict[str, tuple[str, ...]] = field(default_factory=dict)
    disabled_patterns_by_action: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def active_actions(self) -> tuple[str, ...]:
        disabled = set(self.disabled_actions)
        ordered = [*self.required_actions, *self.optional_actions]
        seen: set[str] = set()
        result: list[str] = []
        for action in ordered:
            if action in disabled or action in seen:
                continue
            seen.add(action)
            result.append(action)
        return tuple(result)

    def patterns_for_action(self, action: str, *, required_only: bool = False) -> tuple[str, ...]:
        disabled = set(self.disabled_patterns_by_action.get(action, ()))
        required = [
            pid for pid in self.required_patterns_by_action.get(action, ()) if pid not in disabled
        ]
        if required_only:
            return tuple(required)
        optional = [
            pid
            for pid in self.optional_patterns_by_action.get(action, ())
            if pid not in disabled and pid not in required
        ]
        return tuple([*required, *optional])


@dataclass(frozen=True)
class TrackChapter:
    learning_concept_id: str
    order: int
    tier: str
    prerequisites: tuple[str, ...]
    study_order_tc: tuple[str, ...]
    track_patterns_by_tc: dict[str, dict[str, tuple[str, ...]]] = field(default_factory=dict)


@dataclass(frozen=True)
class CurriculumTrack:
    language: str
    version: int
    chapters: tuple[TrackChapter, ...]
    learning_path_default_sequence: tuple[str, ...] = ()


@dataclass(frozen=True)
class MasteryRule:
    version: int
    action_thresholds: dict[str, int]
    min_successful_tasks_per_action: dict[str, int]
    score_model: dict
    technical_concept_mastered: dict
    learning_concept_mastered: dict
    next_chapter_unlock: dict
    required_actions_by_tier: dict[str, dict[str, list[str]]]
    track_certificate: dict


@dataclass(frozen=True)
class ReviewRule:
    version: int
    review_unit: dict
    forgetting_model: dict
    daily_schedule: dict
    weekly_schedule: dict
    pattern_rotation: dict
    new_chapter_with_stale_review: dict
    forgotten_concept_handling: dict
    review_queue_priority: dict
    interaction_with_mastery: dict


@dataclass(frozen=True)
class CurriculumBundle:
    language: str
    version: int
    learning_concepts: tuple[LearningConcept, ...]
    technical_concepts: tuple[TechnicalConcept, ...]
    exercise_patterns: tuple[ExercisePattern, ...]
    mastery_rules: MasteryRule
    review_rules: ReviewRule
    track: CurriculumTrack
    action_masks: dict[str, TechnicalConceptActionMask]
    tier_defaults: dict[str, dict[str, list[str]]]
    track_templates: dict[str, dict]

    def learning_concept_by_id(self, lc_id: str) -> LearningConcept | None:
        return next((lc for lc in self.learning_concepts if lc.id == lc_id), None)

    def technical_concept_by_id(self, tc_id: str) -> TechnicalConcept | None:
        return next((tc for tc in self.technical_concepts if tc.id == tc_id), None)

    def pattern_by_id(self, pattern_id: str) -> ExercisePattern | None:
        return next((p for p in self.exercise_patterns if p.id == pattern_id), None)

    def action_mask(self, tc_id: str) -> TechnicalConceptActionMask | None:
        return self.action_masks.get(tc_id)

    def technical_concepts_for_lc(self, lc_id: str) -> tuple[TechnicalConcept, ...]:
        return tuple(tc for tc in self.technical_concepts if tc.learning_concept_id == lc_id)

    def mastery_required_actions(self, tc_id: str) -> tuple[str, ...]:
        mask = self.action_masks.get(tc_id)
        if mask is not None:
            return mask.required_actions
        tc = self.technical_concept_by_id(tc_id)
        if tc is None:
            return ()
        tier_cfg = self.tier_defaults.get(tc.tier, {})
        return tuple(tier_cfg.get("required_actions", ()))
