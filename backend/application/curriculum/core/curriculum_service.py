"""Curriculum v2 read service (YAML source of truth)."""

from __future__ import annotations

from domain.learning.curriculum.constants import LEARNING_ACTIONS
from domain.learning.curriculum.exceptions import CurriculumNotFoundError
from domain.learning.curriculum.models import (
    CurriculumBundle,
    ExercisePattern,
    LearningConcept,
    TechnicalConcept,
    TechnicalConceptActionMask,
)
from infrastructure.curriculum.loader import load_curriculum, validate_curriculum_bundle


class CurriculumService:
    def __init__(self, language: str = "pascal") -> None:
        self._language = language.strip().lower()

    def _bundle(self) -> CurriculumBundle:
        return load_curriculum(self._language)

    def get_bundle(self) -> CurriculumBundle:
        return self._bundle()

    def get_learning_concepts(self, language: str | None = None) -> list[LearningConcept]:
        bundle = load_curriculum(language or self._language)
        return sorted(bundle.learning_concepts, key=lambda lc: lc.order)

    def get_technical_concepts(
        self,
        language: str | None = None,
        learning_concept_id: str | None = None,
    ) -> list[TechnicalConcept]:
        bundle = load_curriculum(language or self._language)
        items = list(bundle.technical_concepts)
        if learning_concept_id:
            items = [tc for tc in items if tc.learning_concept_id == learning_concept_id]
        chapter = next(
            (
                ch
                for ch in bundle.track.chapters
                if ch.learning_concept_id == learning_concept_id
            ),
            None,
        ) if learning_concept_id else None
        if chapter and chapter.study_order_tc:
            order = {tc_id: idx for idx, tc_id in enumerate(chapter.study_order_tc)}
            items.sort(key=lambda tc: order.get(tc.id, 999))
        else:
            items.sort(key=lambda tc: tc.id)
        return items

    def get_action_mask(
        self,
        language: str | None,
        technical_concept_id: str,
    ) -> TechnicalConceptActionMask:
        bundle = load_curriculum(language or self._language)
        mask = bundle.action_masks.get(technical_concept_id)
        if mask is None:
            raise CurriculumNotFoundError(f"Unknown technical concept: {technical_concept_id}")
        return mask

    def get_required_patterns(
        self,
        language: str | None,
        technical_concept_id: str,
        action: str,
    ) -> list[str]:
        mask = self.get_action_mask(language, technical_concept_id)
        return list(mask.patterns_for_action(action, required_only=True))

    def get_exercise_patterns(
        self,
        language: str | None,
        technical_concept_id: str,
        action: str | None = None,
    ) -> list[ExercisePattern]:
        bundle = load_curriculum(language or self._language)
        mask = bundle.action_masks.get(technical_concept_id)
        if mask is None:
            raise CurriculumNotFoundError(f"Unknown technical concept: {technical_concept_id}")

        if action is None:
            pattern_ids: list[str] = []
            for act in mask.active_actions():
                pattern_ids.extend(mask.patterns_for_action(act))
            seen: set[str] = set()
            ordered: list[str] = []
            for pid in pattern_ids:
                if pid not in seen:
                    seen.add(pid)
                    ordered.append(pid)
        else:
            if action not in LEARNING_ACTIONS:
                raise CurriculumNotFoundError(f"Unknown action: {action}")
            ordered = list(mask.patterns_for_action(action))

        result: list[ExercisePattern] = []
        for pid in ordered:
            pattern = bundle.pattern_by_id(pid)
            if pattern is not None:
                result.append(pattern)
        return result

    def validate_curriculum(self, language: str | None = None) -> dict:
        lang = (language or self._language).strip().lower()
        bundle = load_curriculum(lang, force=True)
        errors = validate_curriculum_bundle(bundle)
        return {
            "language": lang,
            "valid": not errors,
            "errors": errors,
            "stats": {
                "learning_concepts": len(bundle.learning_concepts),
                "technical_concepts": len(bundle.technical_concepts),
                "exercise_patterns": len(bundle.exercise_patterns),
                "track_chapters": len(bundle.track.chapters),
                "action_masks": len(bundle.action_masks),
            },
        }

    def get_learning_concept_detail(
        self,
        language: str | None,
        learning_concept_id: str,
    ) -> dict:
        bundle = load_curriculum(language or self._language)
        lc = bundle.learning_concept_by_id(learning_concept_id)
        if lc is None:
            raise CurriculumNotFoundError(f"Unknown learning concept: {learning_concept_id}")

        chapter = next(
            (ch for ch in bundle.track.chapters if ch.learning_concept_id == learning_concept_id),
            None,
        )
        tcs = self.get_technical_concepts(language, learning_concept_id)
        tc_payload = []
        for tc in tcs:
            mask = bundle.action_masks[tc.id]
            tc_payload.append(
                {
                    "id": tc.id,
                    "name_ru": tc.name_ru,
                    "tier": tc.tier,
                    "optional_in_track": tc.optional_in_track,
                    "required_actions": list(mask.required_actions),
                    "optional_actions": list(mask.optional_actions),
                    "disabled_actions": list(mask.disabled_actions),
                    "active_actions": list(mask.active_actions()),
                    "required_patterns_by_action": {
                        action: list(mask.patterns_for_action(action, required_only=True))
                        for action in mask.active_actions()
                    },
                }
            )

        return {
            "learning_concept": {
                "id": lc.id,
                "name_ru": lc.name_ru,
                "tier": lc.tier,
                "order": lc.order,
                "description_ru": lc.description_ru,
            },
            "prerequisites": list(chapter.prerequisites) if chapter else [],
            "study_order_tc": list(chapter.study_order_tc) if chapter else [],
            "technical_concepts": tc_payload,
        }

    def get_curriculum_summary(self, language: str | None = None) -> dict:
        bundle = load_curriculum(language or self._language)
        return {
            "language": bundle.language,
            "version": bundle.version,
            "target_language": bundle.language,
            "learning_concepts_count": len(bundle.learning_concepts),
            "technical_concepts_count": len(bundle.technical_concepts),
            "exercise_patterns_count": len(bundle.exercise_patterns),
            "mastery_rules_version": bundle.mastery_rules.version,
            "review_rules_version": bundle.review_rules.version,
            "learning_path_default_sequence": list(bundle.track.learning_path_default_sequence),
        }

    def get_debug_view(self, language: str | None = None) -> dict:
        bundle = load_curriculum(language or self._language)
        chapters = []
        for lc in sorted(bundle.learning_concepts, key=lambda x: x.order):
            detail = self.get_learning_concept_detail(language, lc.id)
            chapters.append(detail)
        validation = self.validate_curriculum(language)
        return {
            "summary": self.get_curriculum_summary(language),
            "validation": validation,
            "chapters": chapters,
        }
