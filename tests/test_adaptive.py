from __future__ import annotations

from datetime import datetime, timezone

from validator.adaptive import (
    assemble_quiz_plan,
    initialize_progress,
    mock_domain_counts,
    recommend_objectives,
    update_progress_from_attempt,
)


def pack() -> dict:
    return {
        "certification": {"id": "SAA-C03"},
        "question_types": ["multiple_choice", "multiple_response"],
        "domains": [
            {"id": "secure", "weight": 30},
            {"id": "resilient", "weight": 26},
            {"id": "performance", "weight": 24},
            {"id": "cost", "weight": 20},
        ],
    }


def curriculum() -> dict:
    return {
        "certification_id": "SAA-C03",
        "curriculum_version": "0.2",
        "stages": [
            {"id": "stage-one", "order": 1, "module_ids": ["foundations"]},
            {"id": "stage-two", "order": 2, "module_ids": ["advanced"]},
        ],
        "modules": [
            {"id": "foundations", "objective_ids": ["network", "resilience"]},
            {"id": "advanced", "objective_ids": ["integrated"]},
        ],
        "objectives": [
            {"id": "network", "title": "Network security", "domain_ids": ["secure"], "importance": "core", "mastery_evidence": ["compare", "apply"], "prerequisite_objective_ids": []},
            {"id": "resilience", "title": "Resilient data", "domain_ids": ["resilient"], "importance": "core", "mastery_evidence": ["apply"], "prerequisite_objective_ids": []},
            {"id": "integrated", "title": "Integrated architecture", "domain_ids": ["secure", "resilient"], "importance": "core", "mastery_evidence": ["integrated_scenario"], "prerequisite_objective_ids": ["network", "resilience"]},
        ],
    }


def test_weak_objective_is_prioritized() -> None:
    progress = initialize_progress(curriculum())
    progress["objective_status"]["network"].update(
        {"status": "needs_review", "attempts": 3, "correct": 1, "confidence": 0.3, "evidence_count": 1}
    )
    progress["weak_objectives"] = ["network"]
    recommendations = recommend_objectives(
        curriculum(),
        pack(),
        progress,
        now=datetime(2026, 7, 30, tzinfo=timezone.utc),
    )
    assert recommendations[0]["objective_id"] == "network"
    assert recommendations[0]["activity_type"] == "comparison"


def test_mock_distribution_uses_domain_weights() -> None:
    assert mock_domain_counts(pack(), 65) == {
        "secure": 19,
        "resilient": 17,
        "performance": 16,
        "cost": 13,
    }


def test_quiz_plan_creates_authoring_slots_when_bank_is_empty() -> None:
    progress = initialize_progress(curriculum())
    plan = assemble_quiz_plan(
        certification_id="SAA-C03",
        curriculum=curriculum(),
        pack=pack(),
        progress=progress,
        question_bank=[],
        count=4,
        mode="adaptive",
        generated_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
    )
    assert len(plan["slots"]) == 4
    assert sum(plan["domain_distribution"].values()) == 4
    assert all(slot["source"]["kind"] == "generate" for slot in plan["slots"])


def test_record_attempt_updates_weakness_and_review_date() -> None:
    progress = initialize_progress(curriculum())
    attempt = {
        "schema_version": 1,
        "id": "attempt-one",
        "certification_id": "SAA-C03",
        "occurred_at": "2026-07-30T10:00:00+00:00",
        "activity_type": "question",
        "result": "incorrect",
        "objective_ids": ["network"],
        "domain_ids": ["secure"],
    }
    updated = update_progress_from_attempt(progress, attempt, curriculum(), pack())
    state = updated["objective_status"]["network"]
    assert state["attempts"] == 1
    assert state["incorrect_streak"] == 1
    assert state["next_review_at"].startswith("2026-07-31")
    assert updated["quiz_summary"]["total_attempts"] == 1
