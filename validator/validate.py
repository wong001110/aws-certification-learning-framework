from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOST_SUFFIXES = ("aws.amazon.com", "docs.aws.amazon.com")


class ValidationFailure(Exception):
    """Raised when repository content violates a deterministic rule."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path}: expected a JSON object")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path}: expected a YAML mapping")
    return value


def validate_schema(
    instance: dict[str, Any],
    schema_path: Path,
    instance_path: Path,
) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{instance_path}: {'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in sorted(
            validator.iter_errors(instance),
            key=lambda item: list(item.absolute_path),
        )
    ]


def load_registry() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    registry = load_yaml(ROOT / "certifications" / "registry.yaml")
    entries = registry.get("certifications", [])
    certifications = {entry["id"]: entry for entry in entries}
    if len(certifications) != len(entries):
        raise ValidationFailure("certifications/registry.yaml: duplicate certification id")
    return registry, certifications


def is_official_aws_url(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except (AttributeError, ValueError):
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in OFFICIAL_HOST_SUFFIXES)


def validate_source_list(
    sources: list[dict[str, Any]],
    path: Path,
    label: str,
) -> list[str]:
    if not sources:
        return [f"{path}: {label} requires at least one source"]
    if not all(is_official_aws_url(source.get("url", "")) for source in sources):
        return [f"{path}: all {label} sources must use official AWS hosts"]
    return []


def duplicate_values(values: list[str | None]) -> set[str | None]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def validate_lesson(
    lesson: dict[str, Any],
    path: Path,
    certification_id: str,
    curriculum_version: str,
    objective_ids: set[str],
) -> list[str]:
    errors = validate_schema(lesson, ROOT / "schemas" / "lesson.schema.json", path)

    if lesson.get("certification_id") != certification_id:
        errors.append(f"{path}: lesson certification_id does not match curriculum")
    if lesson.get("curriculum_version") != curriculum_version:
        errors.append(f"{path}: lesson curriculum_version does not match curriculum")

    unknown_objectives = set(lesson.get("objective_ids", [])) - objective_ids
    if unknown_objectives:
        errors.append(f"{path}: lesson references unknown objectives {sorted(unknown_objectives)}")

    check_ids = [check.get("id") for check in lesson.get("knowledge_checks", [])]
    duplicates = duplicate_values(check_ids)
    if duplicates:
        errors.append(f"{path}: duplicate knowledge check ids {sorted(duplicates)}")

    errors.extend(validate_source_list(lesson.get("sources", []), path, "lesson"))

    review = lesson.get("review", {})
    if review.get("status") == "approved" and not review.get("verified_at"):
        errors.append(f"{path}: approved lessons require verified_at")
    return errors


def validate_curriculum(
    curriculum: dict[str, Any],
    path: Path,
    certification_id: str,
    expected_version: str,
    allowed_domains: set[str],
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors = validate_schema(
        curriculum,
        ROOT / "schemas" / "curriculum.schema.json",
        path,
    )
    lessons: dict[str, dict[str, Any]] = {}

    if curriculum.get("certification_id") != certification_id:
        errors.append(f"{path}: curriculum certification_id does not match pack")
    if curriculum.get("curriculum_version") != expected_version:
        errors.append(f"{path}: curriculum version does not match pack")

    stages = curriculum.get("stages", [])
    modules = curriculum.get("modules", [])
    objectives = curriculum.get("objectives", [])

    stage_ids = [stage.get("id") for stage in stages]
    module_ids = [module.get("id") for module in modules]
    objective_id_list = [objective.get("id") for objective in objectives]

    for label, values in (
        ("stage", stage_ids),
        ("module", module_ids),
        ("objective", objective_id_list),
    ):
        duplicates = duplicate_values(values)
        if duplicates:
            errors.append(f"{path}: duplicate {label} ids {sorted(duplicates)}")

    stage_orders = [stage.get("order") for stage in stages]
    if len(stage_orders) == len(set(stage_orders)) and sorted(stage_orders) != list(
        range(1, len(stage_orders) + 1)
    ):
        errors.append(f"{path}: stage order values must form a continuous sequence from 1")
    elif len(stage_orders) != len(set(stage_orders)):
        errors.append(f"{path}: duplicate stage order")

    known_modules = set(module_ids)
    known_objectives = set(objective_id_list)

    for stage in stages:
        unknown = set(stage.get("module_ids", [])) - known_modules
        if unknown:
            errors.append(
                f"{path}: stage {stage.get('id')} references unknown modules {sorted(unknown)}"
            )

    for objective in objectives:
        unknown_domains = set(objective.get("domain_ids", [])) - allowed_domains
        if unknown_domains:
            errors.append(
                f"{path}: objective {objective.get('id')} uses unknown domains "
                f"{sorted(unknown_domains)}"
            )
        unknown_prerequisites = (
            set(objective.get("prerequisite_objective_ids", [])) - known_objectives
        )
        if unknown_prerequisites:
            errors.append(
                f"{path}: objective {objective.get('id')} references unknown prerequisite "
                f"objectives {sorted(unknown_prerequisites)}"
            )
        if objective.get("id") in set(objective.get("prerequisite_objective_ids", [])):
            errors.append(f"{path}: objective {objective.get('id')} cannot require itself")

    for module in modules:
        unknown_domains = set(module.get("domain_ids", [])) - allowed_domains
        if unknown_domains:
            errors.append(
                f"{path}: module {module.get('id')} uses unknown domains "
                f"{sorted(unknown_domains)}"
            )
        unknown_objectives = set(module.get("objective_ids", [])) - known_objectives
        if unknown_objectives:
            errors.append(
                f"{path}: module {module.get('id')} references unknown objectives "
                f"{sorted(unknown_objectives)}"
            )
        unknown_prerequisites = (
            set(module.get("prerequisite_module_ids", [])) - known_modules
        )
        if unknown_prerequisites:
            errors.append(
                f"{path}: module {module.get('id')} references unknown prerequisite "
                f"modules {sorted(unknown_prerequisites)}"
            )
        if module.get("id") in set(module.get("prerequisite_module_ids", [])):
            errors.append(f"{path}: module {module.get('id')} cannot require itself")

        for lesson_path_value in module.get("lesson_paths", []):
            lesson_path = ROOT / lesson_path_value
            if not lesson_path.exists():
                errors.append(
                    f"{path}: module {module.get('id')} references missing lesson "
                    f"{lesson_path_value}"
                )
                continue
            lesson = load_yaml(lesson_path)
            lesson_id = lesson.get("id")
            if lesson_id in lessons:
                errors.append(f"{path}: duplicate referenced lesson id {lesson_id}")
            lessons[lesson_id] = lesson
            errors.extend(
                validate_lesson(
                    lesson,
                    lesson_path,
                    certification_id,
                    expected_version,
                    known_objectives,
                )
            )

    errors.extend(validate_source_list(curriculum.get("sources", []), path, "curriculum"))
    return errors, lessons


def validate_certification_packs(
    certifications: dict[str, dict[str, Any]],
) -> tuple[
    list[str],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, dict[str, Any]]],
]:
    errors: list[str] = []
    packs: dict[str, dict[str, Any]] = {}
    curricula: dict[str, dict[str, Any]] = {}
    lessons: dict[str, dict[str, dict[str, Any]]] = {}
    schema_path = ROOT / "schemas" / "certification.schema.json"

    for certification_id, registry_entry in certifications.items():
        pack_path_value = registry_entry.get("pack_path")
        if not pack_path_value:
            continue

        pack_path = ROOT / pack_path_value
        if not pack_path.exists():
            errors.append(f"{pack_path}: registry points to a missing certification pack")
            continue

        pack = load_yaml(pack_path)
        packs[certification_id] = pack
        errors.extend(validate_schema(pack, schema_path, pack_path))

        if pack.get("certification", {}).get("id") != certification_id:
            errors.append(f"{pack_path}: certification id does not match registry")

        domains = pack.get("domains", [])
        if sum(domain.get("weight", 0) for domain in domains) != 100:
            errors.append(f"{pack_path}: domain weights must total 100")

        domain_ids = [domain.get("id") for domain in domains]
        duplicates = duplicate_values(domain_ids)
        if duplicates:
            errors.append(f"{pack_path}: duplicate domain ids {sorted(duplicates)}")

        source = pack.get("source", {}).get("exam_guide", "")
        if not is_official_aws_url(source):
            errors.append(f"{pack_path}: exam guide must use an official AWS URL")

        curriculum_config = pack.get("curriculum", {})
        curriculum_path_value = curriculum_config.get("path")
        expected_version = curriculum_config.get("version")
        if not curriculum_path_value:
            errors.append(f"{pack_path}: certification pack requires a curriculum path")
            continue

        curriculum_path = ROOT / curriculum_path_value
        if not curriculum_path.exists():
            errors.append(f"{pack_path}: curriculum path does not exist")
            continue

        curriculum = load_yaml(curriculum_path)
        curricula[certification_id] = curriculum
        curriculum_errors, lesson_map = validate_curriculum(
            curriculum,
            curriculum_path,
            certification_id,
            expected_version,
            set(domain_ids),
        )
        errors.extend(curriculum_errors)
        lessons[certification_id] = lesson_map

    return errors, packs, curricula, lessons


def validate_question(
    question: dict[str, Any],
    path: Path,
    certifications: dict[str, dict[str, Any]],
    packs: dict[str, dict[str, Any]],
) -> list[str]:
    errors = validate_schema(
        question,
        ROOT / "schemas" / "question.schema.json",
        path,
    )
    certification_id = question.get("certification_id")
    if certification_id not in certifications:
        errors.append(f"{path}: unknown certification_id {certification_id!r}")
        return errors

    pack = packs.get(certification_id)
    if pack:
        allowed_domains = {domain["id"] for domain in pack.get("domains", [])}
        if question.get("domain_id") not in allowed_domains:
            errors.append(f"{path}: domain_id is not present in the certification pack")
        if question.get("question_type") not in pack.get("question_types", []):
            errors.append(f"{path}: question_type is not supported by the certification pack")

    question_type = question.get("question_type")
    correct_answers = question.get("correct_answers", [])
    options = question.get("options", [])
    option_ids = [option.get("id") for option in options]

    duplicates = duplicate_values(option_ids)
    if duplicates:
        errors.append(f"{path}: duplicate option ids {sorted(duplicates)}")

    if question_type == "multiple_choice" and len(correct_answers) != 1:
        errors.append(f"{path}: multiple_choice requires exactly one correct answer")
    if question_type == "multiple_response" and len(correct_answers) < 2:
        errors.append(f"{path}: multiple_response requires at least two correct answers")

    if question_type in {"multiple_choice", "multiple_response"}:
        unknown = set(correct_answers) - set(option_ids)
        if unknown:
            errors.append(
                f"{path}: correct_answers references unknown options {sorted(unknown)}"
            )

        declared_correct = {
            option["id"]
            for option in options
            if option.get("classification") in {"best_answer", "correct_component"}
        }
        if set(correct_answers) != declared_correct:
            errors.append(f"{path}: option classifications do not match correct_answers")

        analysis_keys = set(question.get("explanation", {}).get("option_analysis", {}))
        if analysis_keys != set(option_ids):
            errors.append(f"{path}: option_analysis must cover every option exactly once")

    errors.extend(validate_source_list(question.get("sources", []), path, "question"))

    review = question.get("review", {})
    if review.get("status") == "approved":
        if review.get("technical_accuracy") != 5 or review.get("answer_uniqueness") != 5:
            errors.append(
                f"{path}: approved questions require technical_accuracy and "
                "answer_uniqueness of 5"
            )
        if review.get("originality") != 5:
            errors.append(f"{path}: approved questions require originality of 5")
        if review.get("distractor_quality", 0) < 4 or review.get("depth_alignment", 0) < 4:
            errors.append(
                f"{path}: approved questions require distractor_quality and "
                "depth_alignment >= 4"
            )
    return errors


def validate_progress(
    progress: dict[str, Any],
    path: Path,
    curricula: dict[str, dict[str, Any]],
    lessons: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    errors = validate_schema(
        progress,
        ROOT / "schemas" / "progress.schema.json",
        path,
    )
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
        errors.append(
            f"{path}: completed_lesson_ids contains unknown ids {sorted(unknown_lessons)}"
        )

    recommendation = progress.get("next_recommendation")
    if recommendation:
        unknown_recommendations = (
            set(recommendation.get("objective_ids", [])) - objective_ids
        )
        if unknown_recommendations:
            errors.append(
                f"{path}: next_recommendation contains unknown objectives "
                f"{sorted(unknown_recommendations)}"
            )

    for objective_id, status in progress.get("objective_status", {}).items():
        if status.get("correct", 0) > status.get("attempts", 0):
            errors.append(
                f"{path}: objective {objective_id} has more correct responses than attempts"
            )
        if status.get("evidence_count", 0) == 0 and status.get("status") == "proficient":
            errors.append(
                f"{path}: objective {objective_id} cannot be proficient without evidence"
            )
    return errors


def validate_all() -> list[str]:
    errors: list[str] = []
    try:
        _, certifications = load_registry()
    except ValidationFailure as exc:
        return [str(exc)]

    pack_errors, packs, curricula, lessons = validate_certification_packs(certifications)
    errors.extend(pack_errors)

    question_paths = sorted((ROOT / "examples" / "questions").glob("*.json"))
    if not question_paths:
        errors.append("examples/questions: at least one example question is required")

    answer_positions: Counter[str] = Counter()
    for path in question_paths:
        question = load_json(path)
        errors.extend(validate_question(question, path, certifications, packs))
        if question.get("question_type") == "multiple_choice" and question.get(
            "correct_answers"
        ):
            answer_positions[question["correct_answers"][0]] += 1

    if len(question_paths) >= 8 and answer_positions:
        most_common = answer_positions.most_common(1)[0][1]
        if most_common / sum(answer_positions.values()) > 0.5:
            errors.append(
                "examples/questions: correct answer positions are excessively concentrated"
            )

    progress_paths = sorted((ROOT / "examples" / "progress").glob("*.yaml"))
    if not progress_paths:
        errors.append("examples/progress: at least one progress example is required")
    for path in progress_paths:
        progress = load_yaml(path)
        errors.extend(validate_progress(progress, path, curricula, lessons))

    return errors


def main() -> int:
    errors = validate_all()
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
