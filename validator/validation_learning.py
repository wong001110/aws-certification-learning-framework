from __future__ import annotations

from pathlib import Path
from typing import Any

from validator.validation_common import ROOT, validate_schema


def validate_progress(
    progress: dict[str, Any],
    path: Path,
    curricula: dict[str, dict[str, Any]],
    lessons: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    errors = validate_schema(progress, ROOT / "schemas" / "progress.schema.json", path)
    certification_id = progress.get("certification_id")
    curriculum = curricula.get(certification_id)
    if not curriculum:
        errors.append(f"{path}: progress references a certification without a curriculum")
        return errors
    if progress.get("curriculum_version") != curriculum.get("curriculum_version"):
        errors.append(f"{path}: progress curriculum_version does not match curriculum")

    stage_ids = {stage["id"] for stage in curriculum.get("stages", [])}
    objective_ids = {objective["id"] for objective in curriculum.get("objectives", [])}
    lesson_ids = set(lessons.get(certification_id, {}))
    if progress.get("current_stage_id") not in stage_ids:
        errors.append(f"{path}: current_stage_id is not present in the curriculum")
    current_lesson_id = progress.get("current_lesson_id")
    if current_lesson_id is not None and current_lesson_id not in lesson_ids:
        errors.append(f"{path}: current_lesson_id is not a referenced lesson")

    progress_objectives = set(progress.get("objective_status", {}))
    if progress_objectives != objective_ids:
        missing = sorted(objective_ids - progress_objectives)
        unknown = sorted(progress_objectives - objective_ids)
        if missing:
            errors.append(f"{path}: progress is missing objective status entries {missing}")
        if unknown:
            errors.append(f"{path}: progress contains unknown objective entries {unknown}")

    weak_objectives = set(progress.get("weak_objectives", []))
    unknown_weak = weak_objectives - objective_ids
    if unknown_weak:
        errors.append(f"{path}: weak_objectives contains unknown ids {sorted(unknown_weak)}")
    completed_lessons = set(progress.get("completed_lesson_ids", []))
    unknown_lessons = completed_lessons - lesson_ids
    if unknown_lessons:
        errors.append(f"{path}: completed_lesson_ids contains unknown ids {sorted(unknown_lessons)}")

    recommendation = progress.get("next_recommendation")
    if recommendation:
        unknown_recommendations = set(recommendation.get("objective_ids", [])) - objective_ids
        if unknown_recommendations:
            errors.append(
                f"{path}: next_recommendation contains unknown objectives "
                f"{sorted(unknown_recommendations)}"
            )

    for objective_id, status in progress.get("objective_status", {}).items():
        attempts = int(status.get("attempts", 0))
        correct = int(status.get("correct", 0))
        if correct > attempts:
            errors.append(f"{path}: objective {objective_id} has more correct responses than attempts")
        if status.get("evidence_count", 0) == 0 and status.get("status") == "proficient":
            errors.append(f"{path}: objective {objective_id} cannot be proficient without evidence")
        if int(status.get("correct_streak", 0)) > attempts:
            errors.append(f"{path}: objective {objective_id} correct_streak exceeds attempts")
        if int(status.get("incorrect_streak", 0)) > attempts:
            errors.append(f"{path}: objective {objective_id} incorrect_streak exceeds attempts")

    summary = progress.get("quiz_summary")
    if summary and summary.get("total_correct", 0) > summary.get("total_attempts", 0):
        errors.append(f"{path}: quiz_summary has more correct responses than attempts")
    return errors


def validate_adaptive_policy(policy: dict[str, Any], path: Path) -> list[str]:
    errors = validate_schema(policy, ROOT / "schemas" / "adaptive-policy.schema.json", path)
    weights = policy.get("weights", {})
    if weights and abs(sum(float(value) for value in weights.values()) - 1.0) > 0.000001:
        errors.append(f"{path}: adaptive policy weights must total 1.0")
    if sum(float(value) for value in policy.get("question_type_mix", {}).values()) <= 0:
        errors.append(f"{path}: question_type_mix must contain a positive weight")
    return errors


def validate_quiz_plan(
    plan: dict[str, Any],
    path: Path,
    packs: dict[str, dict[str, Any]],
    curricula: dict[str, dict[str, Any]],
    question_ids: set[str] | None = None,
) -> list[str]:
    errors = validate_schema(plan, ROOT / "schemas" / "quiz-plan.schema.json", path)
    certification_id = plan.get("certification_id")
    pack = packs.get(certification_id)
    curriculum = curricula.get(certification_id)
    if not pack or not curriculum:
        errors.append(f"{path}: quiz plan references an unsupported certification")
        return errors

    count = int(plan.get("question_count", 0))
    if sum(plan.get("domain_distribution", {}).values()) != count:
        errors.append(f"{path}: domain_distribution must total question_count")
    if sum(plan.get("question_type_distribution", {}).values()) != count:
        errors.append(f"{path}: question_type_distribution must total question_count")
    slots = plan.get("slots", [])
    if len(slots) != count:
        errors.append(f"{path}: slot count must equal question_count")
    positions = [slot.get("position") for slot in slots]
    if sorted(positions) != list(range(1, count + 1)):
        errors.append(f"{path}: slot positions must form a continuous sequence")

    allowed_domains = {domain["id"] for domain in pack.get("domains", [])}
    allowed_types = set(pack.get("question_types", []))
    objective_ids = {objective["id"] for objective in curriculum.get("objectives", [])}
    for slot in slots:
        if slot.get("domain_id") not in allowed_domains:
            errors.append(f"{path}: slot {slot.get('position')} has an unknown domain")
        if slot.get("question_type") not in allowed_types:
            errors.append(f"{path}: slot {slot.get('position')} has an unsupported question type")
        unknown_objectives = set(slot.get("objective_ids", [])) - objective_ids
        if unknown_objectives:
            errors.append(
                f"{path}: slot {slot.get('position')} references unknown objectives "
                f"{sorted(unknown_objectives)}"
            )
        source = slot.get("source", {})
        if source.get("kind") == "existing" and question_ids is not None:
            if source.get("question_id") not in question_ids:
                errors.append(
                    f"{path}: slot {slot.get('position')} references an unknown question_id"
                )
    return errors


def validate_attempt(
    attempt: dict[str, Any],
    path: Path,
    packs: dict[str, dict[str, Any]],
    curricula: dict[str, dict[str, Any]],
) -> list[str]:
    errors = validate_schema(attempt, ROOT / "schemas" / "attempt.schema.json", path)
    certification_id = attempt.get("certification_id")
    pack = packs.get(certification_id)
    curriculum = curricula.get(certification_id)
    if not pack or not curriculum:
        errors.append(f"{path}: attempt references an unsupported certification")
        return errors
    known_objectives = {objective["id"] for objective in curriculum.get("objectives", [])}
    unknown_objectives = set(attempt.get("objective_ids", [])) - known_objectives
    if unknown_objectives:
        errors.append(f"{path}: attempt references unknown objectives {sorted(unknown_objectives)}")
    known_domains = {domain["id"] for domain in pack.get("domains", [])}
    unknown_domains = set(attempt.get("domain_ids", [])) - known_domains
    if unknown_domains:
        errors.append(f"{path}: attempt references unknown domains {sorted(unknown_domains)}")
    return errors
