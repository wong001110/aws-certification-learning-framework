from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOST_SUFFIXES = ("aws.amazon.com", "docs.aws.amazon.com")


class ValidationFailure(Exception):
    """Raised when repository content violates a deterministic rule."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path}: expected a YAML mapping")
    return value


def validate_schema(instance: dict[str, Any], schema_path: Path, instance_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{instance_path}: {'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    ]


def load_registry() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    registry = load_yaml(ROOT / "certifications" / "registry.yaml")
    certifications = {entry["id"]: entry for entry in registry.get("certifications", [])}
    if len(certifications) != len(registry.get("certifications", [])):
        raise ValidationFailure("certifications/registry.yaml: duplicate certification id")
    return registry, certifications


def validate_certification_packs(certifications: dict[str, dict[str, Any]]) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    packs: dict[str, dict[str, Any]] = {}
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
        if len(domain_ids) != len(set(domain_ids)):
            errors.append(f"{pack_path}: duplicate domain id")
        source = pack.get("source", {}).get("exam_guide", "")
        if not is_official_aws_url(source):
            errors.append(f"{pack_path}: exam guide must use an official AWS URL")
    return errors, packs


def is_official_aws_url(url: str) -> bool:
    try:
        host = url.split("//", 1)[1].split("/", 1)[0].lower()
    except (IndexError, AttributeError):
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in OFFICIAL_HOST_SUFFIXES)


def validate_question(question: dict[str, Any], path: Path, certifications: dict[str, dict[str, Any]], packs: dict[str, dict[str, Any]]) -> list[str]:
    errors = validate_schema(question, ROOT / "schemas" / "question.schema.json", path)
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
    if len(option_ids) != len(set(option_ids)):
        errors.append(f"{path}: duplicate option id")
    if question_type == "multiple_choice" and len(correct_answers) != 1:
        errors.append(f"{path}: multiple_choice requires exactly one correct answer")
    if question_type == "multiple_response" and len(correct_answers) < 2:
        errors.append(f"{path}: multiple_response requires at least two correct answers")
    if question_type in {"multiple_choice", "multiple_response"}:
        unknown = set(correct_answers) - set(option_ids)
        if unknown:
            errors.append(f"{path}: correct_answers references unknown options {sorted(unknown)}")
        declared_correct = {option["id"] for option in options if option.get("classification") in {"best_answer", "correct_component"}}
        if set(correct_answers) != declared_correct:
            errors.append(f"{path}: option classifications do not match correct_answers")
        analysis_keys = set(question.get("explanation", {}).get("option_analysis", {}))
        if analysis_keys != set(option_ids):
            errors.append(f"{path}: option_analysis must cover every option exactly once")
    if not all(is_official_aws_url(source.get("url", "")) for source in question.get("sources", [])):
        errors.append(f"{path}: all sources must use official AWS hosts")
    review = question.get("review", {})
    if review.get("status") == "approved":
        if review.get("technical_accuracy") != 5 or review.get("answer_uniqueness") != 5:
            errors.append(f"{path}: approved questions require technical_accuracy and answer_uniqueness of 5")
        if review.get("originality") != 5:
            errors.append(f"{path}: approved questions require originality of 5")
        if review.get("distractor_quality", 0) < 4 or review.get("depth_alignment", 0) < 4:
            errors.append(f"{path}: approved questions require distractor_quality and depth_alignment >= 4")
    return errors


def validate_all() -> list[str]:
    errors: list[str] = []
    try:
        _, certifications = load_registry()
    except ValidationFailure as exc:
        return [str(exc)]
    pack_errors, packs = validate_certification_packs(certifications)
    errors.extend(pack_errors)
    question_paths = sorted((ROOT / "examples" / "questions").glob("*.json"))
    if not question_paths:
        return ["examples/questions: at least one example question is required"]
    answer_positions: Counter[str] = Counter()
    for path in question_paths:
        question = load_json(path)
        errors.extend(validate_question(question, path, certifications, packs))
        if question.get("question_type") == "multiple_choice" and question.get("correct_answers"):
            answer_positions[question["correct_answers"][0]] += 1
    if len(question_paths) >= 8 and answer_positions:
        most_common = answer_positions.most_common(1)[0][1]
        if most_common / sum(answer_positions.values()) > 0.5:
            errors.append("examples/questions: correct answer positions are excessively concentrated")
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
