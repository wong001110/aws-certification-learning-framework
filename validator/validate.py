from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

from validator.sources import DEFAULT_CACHE_DIR, catalog_source_map, load_source_catalog
from validator.validation_common import (
    ROOT,
    ValidationFailure,
    duplicate_values,
    load_json,
    load_registry,
    load_structured,
    load_yaml,
    validate_catalog_references,
    validate_schema,
    validate_source_list,
)
from validator.validation_curriculum import (
    validate_certification_packs,
    validate_curriculum,
    validate_lesson,
)
from validator.validation_learning import (
    validate_adaptive_policy,
    validate_attempt,
    validate_progress,
    validate_quiz_plan,
)
from validator.validation_questions import validate_question, validate_source_catalog

__all__ = [
    "ROOT",
    "ValidationFailure",
    "duplicate_values",
    "load_json",
    "load_registry",
    "load_structured",
    "load_yaml",
    "main",
    "validate_adaptive_policy",
    "validate_all",
    "validate_attempt",
    "validate_catalog_references",
    "validate_certification_packs",
    "validate_curriculum",
    "validate_lesson",
    "validate_progress",
    "validate_question",
    "validate_quiz_plan",
    "validate_schema",
    "validate_source_catalog",
    "validate_source_list",
]


def _structured_paths(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted([*directory.glob("*.json"), *directory.glob("*.yaml"), *directory.glob("*.yml")])


def validate_all(
    *,
    as_of: date | None = None,
    strict_freshness: bool = False,
) -> list[str]:
    errors: list[str] = []
    try:
        _, certifications = load_registry()
    except ValidationFailure as exc:
        return [str(exc)]

    catalog_path = ROOT / "sources" / "catalog.yaml"
    if not catalog_path.exists():
        return ["sources/catalog.yaml: official source catalog is required"]
    source_catalog = load_source_catalog(catalog_path)

    pack_errors, packs, curricula, lessons = validate_certification_packs(
        certifications,
        source_catalog,
    )
    errors.extend(pack_errors)
    errors.extend(
        validate_source_catalog(
            source_catalog,
            catalog_path,
            certifications,
            curricula,
            as_of=as_of,
            strict_freshness=strict_freshness,
        )
    )

    question_paths = sorted((ROOT / "examples" / "questions").glob("*.json"))
    if not question_paths:
        errors.append("examples/questions: at least one example question is required")
    answer_positions: Counter[str] = Counter()
    question_ids: set[str] = set()
    for path in question_paths:
        question = load_json(path)
        question_ids.add(str(question.get("id")))
        errors.extend(
            validate_question(
                question,
                path,
                certifications,
                packs,
                curricula,
                source_catalog,
            )
        )
        if question.get("question_type") == "multiple_choice" and question.get("correct_answers"):
            answer_positions[question["correct_answers"][0]] += 1
    if len(question_paths) >= 8 and answer_positions:
        most_common = answer_positions.most_common(1)[0][1]
        if most_common / sum(answer_positions.values()) > 0.5:
            errors.append("examples/questions: correct answer positions are excessively concentrated")

    progress_paths = _structured_paths(ROOT / "examples" / "progress")
    if not progress_paths:
        errors.append("examples/progress: at least one progress example is required")
    for path in progress_paths:
        errors.extend(validate_progress(load_structured(path), path, curricula, lessons))

    policy_path = ROOT / "policies" / "adaptive-default.yaml"
    if not policy_path.exists():
        errors.append("policies/adaptive-default.yaml: adaptive policy is required")
    else:
        errors.extend(validate_adaptive_policy(load_yaml(policy_path), policy_path))

    for path in _structured_paths(ROOT / "examples" / "quiz-plans"):
        errors.extend(validate_quiz_plan(load_structured(path), path, packs, curricula, question_ids))
    for path in _structured_paths(ROOT / "examples" / "attempts"):
        errors.extend(validate_attempt(load_structured(path), path, packs, curricula))

    cache_schema = ROOT / "schemas" / "source-cache.schema.json"
    if DEFAULT_CACHE_DIR.exists():
        source_map = catalog_source_map(source_catalog)
        for path in sorted(DEFAULT_CACHE_DIR.glob("*.json")):
            cache = load_json(path)
            errors.extend(validate_schema(cache, cache_schema, path))
            source = source_map.get(cache.get("source_id"))
            if source is None:
                errors.append(f"{path}: cache references an unknown source_id")
            elif cache.get("url") != source.get("url"):
                errors.append(f"{path}: cached URL does not match the source catalog")
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
