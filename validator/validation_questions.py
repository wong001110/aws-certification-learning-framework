from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from validator.sources import catalog_source_map, freshness_report, is_official_aws_url
from validator.validation_common import (
    ROOT,
    _load_catalog_if_available,
    duplicate_values,
    validate_catalog_references,
    validate_schema,
)


def validate_source_catalog(
    catalog: dict[str, Any],
    path: Path,
    certifications: dict[str, dict[str, Any]],
    curricula: dict[str, dict[str, Any]] | None = None,
    *,
    as_of: date | None = None,
    strict_freshness: bool = False,
) -> list[str]:
    errors = validate_schema(catalog, ROOT / "schemas" / "source-catalog.schema.json", path)
    sources = catalog.get("sources", [])
    source_ids = [source.get("id") for source in sources]
    urls = [source.get("url") for source in sources]
    duplicate_ids = duplicate_values(source_ids)
    duplicate_urls = duplicate_values(urls)
    if duplicate_ids:
        errors.append(f"{path}: duplicate source ids {sorted(duplicate_ids)}")
    if duplicate_urls:
        errors.append(f"{path}: duplicate source URLs {sorted(duplicate_urls)}")

    known_objectives = {
        objective["id"]
        for curriculum in (curricula or {}).values()
        for objective in curriculum.get("objectives", [])
    }
    for source in sources:
        source_id = source.get("id")
        if not is_official_aws_url(source.get("url", "")):
            errors.append(f"{path}: source {source_id} must use an official AWS URL")
        unknown_certifications = set(source.get("certification_ids", [])) - set(certifications)
        if unknown_certifications:
            errors.append(
                f"{path}: source {source_id} references unknown certifications "
                f"{sorted(unknown_certifications)}"
            )
        if curricula is not None:
            unknown_objectives = set(source.get("objective_ids", [])) - known_objectives
            if unknown_objectives:
                errors.append(
                    f"{path}: source {source_id} references unknown objectives "
                    f"{sorted(unknown_objectives)}"
                )
    if strict_freshness:
        for item in freshness_report(catalog, as_of=as_of):
            if item["status"] in {"stale", "future"}:
                errors.append(
                    f"{path}: source {item['source_id']} freshness status is {item['status']} "
                    f"(verified {item['verified_at']}, expires {item['expires_at']})"
                )
    return errors


def validate_question(
    question: dict[str, Any],
    path: Path,
    certifications: dict[str, dict[str, Any]],
    packs: dict[str, dict[str, Any]],
    curricula: dict[str, dict[str, Any]] | None = None,
    source_catalog: dict[str, Any] | None = None,
) -> list[str]:
    errors = validate_schema(question, ROOT / "schemas" / "question.schema.json", path)
    source_catalog = source_catalog if source_catalog is not None else _load_catalog_if_available()
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

    curriculum = (curricula or {}).get(certification_id)
    if curriculum:
        known_objectives = {objective["id"] for objective in curriculum.get("objectives", [])}
        objective_ids = set(question.get("objective_ids", []))
        if not objective_ids and question.get("review", {}).get("status") == "approved":
            errors.append(f"{path}: approved questions require objective_ids")
        unknown_objectives = objective_ids - known_objectives
        if unknown_objectives:
            errors.append(f"{path}: question references unknown objectives {sorted(unknown_objectives)}")

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
            errors.append(f"{path}: correct_answers references unknown options {sorted(unknown)}")
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

    review = question.get("review", {})
    approved = review.get("status") == "approved"
    errors.extend(
        validate_catalog_references(
            sources=question.get("sources", []),
            source_ids=question.get("source_ids", []),
            path=path,
            label="question",
            source_catalog=source_catalog,
            require_ids=approved,
        )
    )
    if approved:
        if review.get("technical_accuracy") != 5 or review.get("answer_uniqueness") != 5:
            errors.append(
                f"{path}: approved questions require technical_accuracy and answer_uniqueness of 5"
            )
        if review.get("originality") != 5:
            errors.append(f"{path}: approved questions require originality of 5")
        if review.get("distractor_quality", 0) < 4 or review.get("depth_alignment", 0) < 4:
            errors.append(
                f"{path}: approved questions require distractor_quality and depth_alignment >= 4"
            )
    return errors
