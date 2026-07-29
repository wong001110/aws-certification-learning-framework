from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from validator.validate import ROOT, load_registry, validate_all, validate_certification_packs, validate_question


def load_example(name: str) -> dict:
    path = ROOT / "examples" / "questions" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_repository_content_is_valid() -> None:
    assert validate_all() == []


def test_multiple_choice_requires_one_answer() -> None:
    _, certifications = load_registry()
    _, packs = validate_certification_packs(certifications)
    question = deepcopy(load_example("saa-c03-resilient-database.json"))
    question["correct_answers"] = ["A", "C"]
    errors = validate_question(question, Path("memory.json"), certifications, packs)
    assert any("exactly one correct answer" in error for error in errors)


def test_question_domain_must_exist_in_pack() -> None:
    _, certifications = load_registry()
    _, packs = validate_certification_packs(certifications)
    question = deepcopy(load_example("aif-c01-responsible-ai.json"))
    question["domain_id"] = "unknown_domain"
    errors = validate_question(question, Path("memory.json"), certifications, packs)
    assert any("domain_id is not present" in error for error in errors)


def test_approved_question_requires_full_accuracy() -> None:
    _, certifications = load_registry()
    _, packs = validate_certification_packs(certifications)
    question = deepcopy(load_example("clf-c02-cloud-value.json"))
    question["review"]["technical_accuracy"] = 4
    errors = validate_question(question, Path("memory.json"), certifications, packs)
    assert any("technical_accuracy" in error for error in errors)
