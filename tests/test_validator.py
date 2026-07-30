from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import yaml

from validator.validate import (
    ROOT,
    load_registry,
    validate_all,
    validate_certification_packs,
    validate_curriculum,
    validate_lesson,
    validate_progress,
    validate_question,
)


def load_example(name: str) -> dict:
    path = ROOT / "examples" / "questions" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_repository_content_is_valid() -> None:
    assert validate_all() == []


def test_multiple_choice_requires_one_answer() -> None:
    _, certifications = load_registry()
    _, packs, _, _ = validate_certification_packs(certifications)
    question = deepcopy(load_example("saa-c03-resilient-database.json"))
    question["correct_answers"] = ["A", "C"]
    errors = validate_question(question, Path("memory.json"), certifications, packs)
    assert any("exactly one correct answer" in error for error in errors)


def test_question_domain_must_exist_in_pack() -> None:
    _, certifications = load_registry()
    _, packs, _, _ = validate_certification_packs(certifications)
    question = deepcopy(load_example("aif-c01-responsible-ai.json"))
    question["domain_id"] = "unknown_domain"
    errors = validate_question(question, Path("memory.json"), certifications, packs)
    assert any("domain_id is not present" in error for error in errors)


def test_approved_question_requires_full_accuracy() -> None:
    _, certifications = load_registry()
    _, packs, _, _ = validate_certification_packs(certifications)
    question = deepcopy(load_example("clf-c02-cloud-value.json"))
    question["review"]["technical_accuracy"] = 4
    errors = validate_question(question, Path("memory.json"), certifications, packs)
    assert any("technical_accuracy" in error for error in errors)


def test_curriculum_rejects_unknown_module_reference() -> None:
    _, certifications = load_registry()
    _, packs, curricula, _ = validate_certification_packs(certifications)
    curriculum = deepcopy(curricula["SAA-C03"])
    curriculum["stages"][0]["module_ids"] = ["missing-module"]
    pack = packs["SAA-C03"]
    errors, _ = validate_curriculum(
        curriculum,
        Path("memory.yaml"),
        "SAA-C03",
        "0.2",
        {domain["id"] for domain in pack["domains"]},
    )
    assert any("unknown modules" in error for error in errors)


def test_lesson_rejects_unknown_objective() -> None:
    _, certifications = load_registry()
    _, _, curricula, lessons = validate_certification_packs(certifications)
    lesson = deepcopy(lessons["SAA-C03"]["architecture-decision-foundations"])
    lesson["objective_ids"] = ["missing-objective"]
    objective_ids = {objective["id"] for objective in curricula["SAA-C03"]["objectives"]}
    errors = validate_lesson(
        lesson,
        Path("memory.yaml"),
        "SAA-C03",
        "0.2",
        objective_ids,
    )
    assert any("unknown objectives" in error for error in errors)


def test_progress_requires_every_curriculum_objective() -> None:
    _, certifications = load_registry()
    _, _, curricula, lessons = validate_certification_packs(certifications)
    progress_path = ROOT / "examples" / "progress" / "saa-c03-example.yaml"
    progress = yaml.safe_load(progress_path.read_text(encoding="utf-8"))
    progress["objective_status"].pop("saa-global-infrastructure")
    errors = validate_progress(progress, Path("memory.yaml"), curricula, lessons)
    assert any("missing objective status" in error for error in errors)
