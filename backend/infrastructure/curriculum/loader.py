"""Load and validate curriculum v2 YAML bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from domain.learning.curriculum.constants import (
    LEARNING_ACTIONS,
    SUPPORTED_CURRICULUM_LANGUAGES,
    VALID_LEGACY_ADAPTERS,
)
from domain.learning.curriculum.exceptions import (
    CurriculumNotFoundError,
    CurriculumValidationError,
)
from domain.learning.curriculum.models import (
    CurriculumBundle,
    CurriculumTrack,
    ExercisePattern,
    LearningConcept,
    MasteryRule,
    ReviewRule,
    TechnicalConcept,
    TechnicalConceptActionMask,
    TrackChapter,
)

_RESOURCES_ROOT = Path(__file__).resolve().parents[2] / "resources" / "curriculum"
_CACHE: dict[str, CurriculumBundle] = {}


def _curriculum_dir(language: str) -> Path:
    lang = language.strip().lower()
    if lang not in SUPPORTED_CURRICULUM_LANGUAGES:
        raise CurriculumNotFoundError(f"Unsupported curriculum language: {language}")
    return _RESOURCES_ROOT / lang


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CurriculumNotFoundError(f"Missing curriculum file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CurriculumValidationError([f"{path.name}: root must be a mapping"])
    return data


def _as_str_list(value: Any, *, field: str, errors: list[str]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return []
    return value


def _parse_learning_concepts(raw: dict[str, Any]) -> tuple[LearningConcept, ...]:
    items = raw.get("concepts") or []
    result: list[LearningConcept] = []
    for item in items:
        result.append(
            LearningConcept(
                id=str(item["id"]),
                name_ru=str(item.get("name_ru", "")),
                tier=str(item.get("tier", "")),
                order=int(item.get("order", 0)),
                description_ru=str(item.get("description_ru", "")),
            )
        )
    return tuple(result)


def _parse_technical_concepts(raw: dict[str, Any]) -> tuple[TechnicalConcept, ...]:
    items = raw.get("concepts") or []
    result: list[TechnicalConcept] = []
    for item in items:
        result.append(
            TechnicalConcept(
                id=str(item["id"]),
                learning_concept_id=str(item["learning_concept_id"]),
                name_ru=str(item.get("name_ru", "")),
                tier=str(item.get("tier", "")),
                notes=str(item.get("notes", "")),
                optional_in_track=bool(item.get("optional_in_track", False)),
            )
        )
    return tuple(result)


def _parse_exercise_patterns(raw: dict[str, Any]) -> tuple[ExercisePattern, ...]:
    items = raw.get("patterns") or []
    result: list[ExercisePattern] = []
    for item in items:
        legacy = item.get("legacy_adapter")
        result.append(
            ExercisePattern(
                id=str(item["id"]),
                action=str(item["action"]),
                description_ru=str(item.get("description_ru", "")),
                grading=str(item.get("grading", "")),
                legacy_adapter=str(legacy) if legacy else None,
                source=item.get("source"),
                target=item.get("target"),
                transfer=item.get("transfer"),
            )
        )
    return tuple(result)


def _parse_mastery_rules(raw: dict[str, Any]) -> MasteryRule:
    return MasteryRule(
        version=int(raw.get("version", 1)),
        action_thresholds=dict(raw.get("action_thresholds") or {}),
        min_successful_tasks_per_action=dict(raw.get("min_successful_tasks_per_action") or {}),
        score_model=dict(raw.get("score_model") or {}),
        technical_concept_mastered=dict(raw.get("technical_concept_mastered") or {}),
        learning_concept_mastered=dict(raw.get("learning_concept_mastered") or {}),
        next_chapter_unlock=dict(raw.get("next_chapter_unlock") or {}),
        required_actions_by_tier=dict(raw.get("required_actions_by_tier") or {}),
        track_certificate=dict(raw.get("track_certificate") or {}),
    )


def _parse_review_rules(raw: dict[str, Any]) -> ReviewRule:
    return ReviewRule(
        version=int(raw.get("version", 1)),
        review_unit=dict(raw.get("review_unit") or {}),
        forgetting_model=dict(raw.get("forgetting_model") or {}),
        daily_schedule=dict(raw.get("daily_schedule") or {}),
        weekly_schedule=dict(raw.get("weekly_schedule") or {}),
        pattern_rotation=dict(raw.get("pattern_rotation") or {}),
        new_chapter_with_stale_review=dict(raw.get("new_chapter_with_stale_review") or {}),
        forgotten_concept_handling=dict(raw.get("forgotten_concept_handling") or {}),
        review_queue_priority=dict(raw.get("review_queue_priority") or {}),
        interaction_with_mastery=dict(raw.get("interaction_with_mastery") or {}),
    )


def _extract_track_patterns(chapter_raw: dict[str, Any]) -> dict[str, dict[str, tuple[str, ...]]]:
    tc_map = chapter_raw.get("technical_concepts") or {}
    result: dict[str, dict[str, tuple[str, ...]]] = {}
    if not isinstance(tc_map, dict):
        return result
    for tc_id, tc_cfg in tc_map.items():
        if not isinstance(tc_cfg, dict):
            continue
        per_action: dict[str, tuple[str, ...]] = {}
        for action in LEARNING_ACTIONS:
            action_cfg = tc_cfg.get(action)
            if isinstance(action_cfg, dict):
                patterns = action_cfg.get("patterns") or []
                if isinstance(patterns, list):
                    per_action[action] = tuple(str(p) for p in patterns)
        if per_action:
            result[str(tc_id)] = per_action
    return result


def _parse_track(language: str, raw: dict[str, Any]) -> tuple[CurriculumTrack, dict[str, dict[str, tuple[str, ...]]]]:
    chapters_raw = raw.get("chapters") or []
    chapters: list[TrackChapter] = []
    all_track_patterns: dict[str, dict[str, tuple[str, ...]]] = {}
    for chapter in chapters_raw:
        lc_id = str(chapter["learning_concept_id"])
        track_patterns = _extract_track_patterns(chapter)
        for tc_id, patterns in track_patterns.items():
            merged = dict(all_track_patterns.get(tc_id, {}))
            merged.update(patterns)
            all_track_patterns[tc_id] = merged
        chapters.append(
            TrackChapter(
                learning_concept_id=lc_id,
                order=int(chapter.get("order", 0)),
                tier=str(chapter.get("tier", "")),
                prerequisites=tuple(str(p) for p in (chapter.get("prerequisites") or [])),
                study_order_tc=tuple(str(t) for t in (chapter.get("study_order_tc") or [])),
                track_patterns_by_tc=track_patterns,
            )
        )
    path_seq = raw.get("learning_path_default_sequence") or {}
    if isinstance(path_seq, dict):
        actions = path_seq.get("actions") or []
    elif isinstance(path_seq, list):
        actions = path_seq
    else:
        actions = []
    track = CurriculumTrack(
        language=language,
        version=int(raw.get("version", 1)),
        chapters=tuple(chapters),
        learning_path_default_sequence=tuple(str(a) for a in actions),
    )
    return track, all_track_patterns


def _parse_action_mask_entry(
    tc_id: str,
    raw: dict[str, Any],
) -> TechnicalConceptActionMask:
    def patterns_map(key: str) -> dict[str, tuple[str, ...]]:
        block = raw.get(key) or {}
        if not isinstance(block, dict):
            return {}
        result: dict[str, tuple[str, ...]] = {}
        for action, ids in block.items():
            if isinstance(ids, list):
                result[str(action)] = tuple(str(i) for i in ids)
        return result

    return TechnicalConceptActionMask(
        technical_concept_id=tc_id,
        required_actions=tuple(str(a) for a in (raw.get("required_actions") or [])),
        optional_actions=tuple(str(a) for a in (raw.get("optional_actions") or [])),
        disabled_actions=tuple(str(a) for a in (raw.get("disabled_actions") or [])),
        required_patterns_by_action=patterns_map("required_patterns_by_action"),
        optional_patterns_by_action=patterns_map("optional_patterns_by_action"),
        disabled_patterns_by_action=patterns_map("disabled_patterns_by_action"),
    )


def _build_default_mask(
    tc: TechnicalConcept,
    tier_defaults: dict[str, dict[str, list[str]]],
    track_patterns: dict[str, tuple[str, ...]] | None,
) -> TechnicalConceptActionMask:
    tier_cfg = tier_defaults.get(tc.tier, {})
    required_actions = tuple(tier_cfg.get("required_actions") or [])
    optional_actions = tuple(tier_cfg.get("optional_actions") or [])
    disabled_actions = tuple(tier_cfg.get("disabled_actions") or [])
    required_patterns: dict[str, tuple[str, ...]] = {}
    if track_patterns:
        disabled_set = set(disabled_actions)
        for action, pattern_ids in track_patterns.items():
            if action in disabled_set:
                continue
            required_patterns[action] = pattern_ids
    return TechnicalConceptActionMask(
        technical_concept_id=tc.id,
        required_actions=required_actions,
        optional_actions=optional_actions,
        disabled_actions=disabled_actions,
        required_patterns_by_action=required_patterns,
    )


def _merge_tier_defaults(
    matrix_raw: dict[str, Any],
    mastery_raw: dict[str, Any],
) -> dict[str, dict[str, list[str]]]:
    merged: dict[str, dict[str, list[str]]] = {}
    matrix_defaults = matrix_raw.get("tier_defaults") or {}
    mastery_tiers = mastery_raw.get("required_actions_by_tier") or {}
    for tier in {"beginner", "intermediate", "advanced"}:
        base = dict(mastery_tiers.get(tier) or {})
        override = matrix_defaults.get(tier) or {}
        merged[tier] = {
            "required_actions": list(
                override.get("required_actions") or base.get("required") or []
            ),
            "optional_actions": list(
                override.get("optional_actions") or base.get("optional") or []
            ),
            "disabled_actions": list(override.get("disabled_actions") or []),
        }
    return merged


def validate_curriculum_bundle(bundle: CurriculumBundle) -> list[str]:
    errors: list[str] = []
    pattern_ids = {p.id for p in bundle.exercise_patterns}
    pattern_by_id = {p.id: p for p in bundle.exercise_patterns}
    lc_ids = {lc.id for lc in bundle.learning_concepts}
    tc_ids = {tc.id for tc in bundle.technical_concepts}
    tc_by_id = {tc.id: tc for tc in bundle.technical_concepts}

    if len(bundle.learning_concepts) != len(lc_ids):
        errors.append("Duplicate learning concept ids")

    if len(bundle.technical_concepts) != len(tc_ids):
        errors.append("Duplicate technical concept ids")

    for tc in bundle.technical_concepts:
        if tc.learning_concept_id not in lc_ids:
            errors.append(
                f"TC {tc.id}: unknown learning_concept_id {tc.learning_concept_id}"
            )

    for chapter in bundle.track.chapters:
        if chapter.learning_concept_id not in lc_ids:
            errors.append(
                f"Track chapter unknown LC: {chapter.learning_concept_id}"
            )
        for tc_id in chapter.study_order_tc:
            if tc_id not in tc_ids:
                errors.append(f"Track study_order_tc unknown TC: {tc_id}")
            elif tc_by_id[tc_id].learning_concept_id != chapter.learning_concept_id:
                errors.append(
                    f"TC {tc_id} in chapter {chapter.learning_concept_id} "
                    f"belongs to {tc_by_id[tc_id].learning_concept_id}"
                )
        for tc_id in chapter.track_patterns_by_tc:
            if tc_id not in tc_ids:
                errors.append(f"Track patterns unknown TC: {tc_id}")

    for pattern in bundle.exercise_patterns:
        if pattern.action not in LEARNING_ACTIONS:
            errors.append(f"Pattern {pattern.id}: unknown action {pattern.action}")
        if pattern.legacy_adapter and pattern.legacy_adapter not in VALID_LEGACY_ADAPTERS:
            errors.append(
                f"Pattern {pattern.id}: invalid legacy_adapter {pattern.legacy_adapter}"
            )

    for tc_id, mask in bundle.action_masks.items():
        if tc_id not in tc_ids:
            errors.append(f"Action mask unknown TC: {tc_id}")
            continue
        if not mask.required_actions:
            errors.append(f"TC {tc_id}: required_actions must not be empty")

        disabled = set(mask.disabled_actions)
        for action in mask.required_actions:
            if action not in LEARNING_ACTIONS:
                errors.append(f"TC {tc_id}: unknown required action {action}")
            if action in disabled:
                errors.append(f"TC {tc_id}: required action {action} is disabled")

        for action in mask.optional_actions:
            if action in disabled:
                errors.append(f"TC {tc_id}: optional action {action} is disabled")

        all_actions = set(mask.required_actions) | set(mask.optional_actions) | disabled
        for action in all_actions:
            for bucket in (
                mask.required_patterns_by_action.get(action, ()),
                mask.optional_patterns_by_action.get(action, ()),
                mask.disabled_patterns_by_action.get(action, ()),
            ):
                for pid in bucket:
                    if pid not in pattern_ids:
                        errors.append(f"TC {tc_id}/{action}: unknown pattern {pid}")
                    else:
                        pat = pattern_by_id[pid]
                        if pat.action != action:
                            errors.append(
                                f"TC {tc_id}/{action}: pattern {pid} has action {pat.action}"
                            )

            for pid in mask.required_patterns_by_action.get(action, ()):
                if pid in set(mask.disabled_patterns_by_action.get(action, ())):
                    errors.append(
                        f"TC {tc_id}/{action}: required pattern {pid} is disabled"
                    )

        for action in disabled:
            if mask.required_patterns_by_action.get(action):
                errors.append(
                    f"TC {tc_id}: disabled action {action} has required patterns"
                )

    for pid, pat in pattern_by_id.items():
        if pat.legacy_adapter is None:
            continue
        if pat.legacy_adapter not in VALID_LEGACY_ADAPTERS:
            errors.append(f"Pattern {pid}: invalid legacy_adapter in catalog")

    return errors


def load_curriculum(language: str, *, force: bool = False) -> CurriculumBundle:
    lang = language.strip().lower()
    if not force and lang in _CACHE:
        return _CACHE[lang]

    base = _curriculum_dir(lang)
    lc_raw = _read_yaml(base / "learning_concepts.yaml")
    tc_raw = _read_yaml(base / "technical_concepts.yaml")
    patterns_raw = _read_yaml(base / "exercise_pattern_catalog.yaml")
    mastery_raw = _read_yaml(base / "mastery_rules.yaml")
    review_raw = _read_yaml(base / "review_rules.yaml")
    track_raw = _read_yaml(base / "pascal_curriculum_track.yaml")
    matrix_raw = _read_yaml(base / "pascal_tc_action_matrix.yaml")

    learning_concepts = _parse_learning_concepts(lc_raw)
    technical_concepts = _parse_technical_concepts(tc_raw)
    exercise_patterns = _parse_exercise_patterns(patterns_raw)
    mastery_rules = _parse_mastery_rules(mastery_raw)
    review_rules = _parse_review_rules(review_raw)
    track, all_track_patterns = _parse_track(lang, track_raw)
    tier_defaults = _merge_tier_defaults(matrix_raw, mastery_raw)
    track_templates = dict(track_raw.get("templates") or {})

    explicit_masks_raw = matrix_raw.get("action_masks") or {}
    tc_by_id = {tc.id: tc for tc in technical_concepts}
    action_masks: dict[str, TechnicalConceptActionMask] = {}

    for tc in technical_concepts:
        if tc.id in explicit_masks_raw and isinstance(explicit_masks_raw[tc.id], dict):
            action_masks[tc.id] = _parse_action_mask_entry(tc.id, explicit_masks_raw[tc.id])
        else:
            action_masks[tc.id] = _build_default_mask(
                tc,
                tier_defaults,
                all_track_patterns.get(tc.id),
            )

    bundle = CurriculumBundle(
        language=lang,
        version=int(lc_raw.get("version", 1)),
        learning_concepts=learning_concepts,
        technical_concepts=technical_concepts,
        exercise_patterns=exercise_patterns,
        mastery_rules=mastery_rules,
        review_rules=review_rules,
        track=track,
        action_masks=action_masks,
        tier_defaults=tier_defaults,
        track_templates=track_templates,
    )

    errors = validate_curriculum_bundle(bundle)
    if errors:
        raise CurriculumValidationError(errors)

    _CACHE[lang] = bundle
    return bundle


def clear_curriculum_cache() -> None:
    _CACHE.clear()
