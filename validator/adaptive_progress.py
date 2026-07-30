from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from validator.adaptive_base import DEFAULT_POLICY, clamp, parse_datetime, recommend_objectives

def update_progress_from_attempt(
    progress: dict[str, Any],
    attempt: dict[str, Any],
    curriculum: dict[str, Any],
    pack: dict[str, Any],
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or DEFAULT_POLICY
    updated = deepcopy(progress)
    occurred_at = parse_datetime(attempt["occurred_at"]) or datetime.now(timezone.utc)
    result = attempt["result"]
    objective_ids = attempt.get("objective_ids", [])

    for objective_id in objective_ids:
        state = updated["objective_status"][objective_id]
        if result != "skipped":
            state["attempts"] = int(state.get("attempts", 0)) + 1
        if result == "correct":
            state["correct"] = int(state.get("correct", 0)) + 1
        if result in {"correct", "partial"}:
            state["evidence_count"] = int(state.get("evidence_count", 0)) + 1

        correct_streak = int(state.get("correct_streak", 0))
        incorrect_streak = int(state.get("incorrect_streak", 0))
        if result == "correct":
            correct_streak += 1
            incorrect_streak = 0
        elif result == "incorrect":
            incorrect_streak += 1
            correct_streak = 0
        elif result == "partial":
            correct_streak = 0
            incorrect_streak = 0
        state["correct_streak"] = correct_streak
        state["incorrect_streak"] = incorrect_streak
        state["last_seen_at"] = occurred_at.isoformat()
        state["last_updated"] = occurred_at.isoformat()

        if attempt.get("confidence_after") is not None:
            state["confidence"] = clamp(float(attempt["confidence_after"]))
        else:
            delta = {"correct": 0.12, "partial": 0.03, "incorrect": -0.16, "skipped": -0.02}[result]
            state["confidence"] = round(clamp(float(state.get("confidence", 0.0)) + delta), 4)

        intervals = [2, 5, 12, 30]
        if result == "correct":
            interval = intervals[min(max(correct_streak, 1), len(intervals)) - 1]
        elif result == "partial":
            interval = 2
        else:
            interval = 1
        state["next_review_at"] = (occurred_at + timedelta(days=interval)).isoformat()

        attempts = int(state.get("attempts", 0))
        correct = int(state.get("correct", 0))
        evidence_count = int(state.get("evidence_count", 0))
        accuracy = correct / attempts if attempts else 0.0
        previous_status = state.get("status", "not_started")
        if result == "incorrect" and previous_status == "proficient":
            state["status"] = "needs_review"
        elif evidence_count >= 3 and attempts >= 3 and accuracy >= 0.8:
            state["status"] = "proficient"
        elif attempts >= 1 or evidence_count >= 1:
            state["status"] = "practicing"
        elif previous_status == "not_started":
            state["status"] = "introduced"

        weak = set(updated.get("weak_objectives", []))
        if (attempts >= 2 and accuracy < 0.6) or state["status"] == "needs_review":
            weak.add(objective_id)
        elif state["status"] == "proficient" and accuracy >= 0.8:
            weak.discard(objective_id)
        updated["weak_objectives"] = sorted(weak)

    history_result = result
    updated.setdefault("history", []).append(
        {
            "occurred_at": occurred_at.isoformat(),
            "activity_type": "question" if attempt.get("session_id") is None else "quiz",
            "reference_id": attempt.get("question_id") or attempt["id"],
            "result": history_result,
            "objective_ids": objective_ids,
            "notes": attempt.get("notes", ""),
        }
    )

    summary = updated.setdefault(
        "quiz_summary",
        {
            "total_attempts": 0,
            "total_correct": 0,
            "recent_results": [],
            "last_session_at": None,
        },
    )
    if result != "skipped":
        summary["total_attempts"] = int(summary.get("total_attempts", 0)) + 1
    if result == "correct":
        summary["total_correct"] = int(summary.get("total_correct", 0)) + 1
    recent = list(summary.get("recent_results", []))
    recent.append(result)
    summary["recent_results"] = recent[-20:]
    summary["last_session_at"] = occurred_at.isoformat()

    recommendations = recommend_objectives(
        curriculum,
        pack,
        updated,
        policy,
        limit=1,
        now=occurred_at,
    )
    if recommendations:
        recommendation = recommendations[0]
        updated["next_recommendation"] = {
            "activity_type": recommendation["activity_type"],
            "objective_ids": [recommendation["objective_id"]],
            "reason": recommendation["reason"],
        }
    adaptive_state = updated.setdefault("adaptive_state", {})
    adaptive_state["last_policy_version"] = str(policy.get("policy_version", "0.4"))
    adaptive_state["last_recommendation_at"] = occurred_at.isoformat()
    seen = set(adaptive_state.get("seen_question_ids", []))
    if attempt.get("question_id"):
        seen.add(attempt["question_id"])
    adaptive_state["seen_question_ids"] = sorted(seen)
    return updated


def initialize_progress(
    curriculum: dict[str, Any],
    *,
    certification_id: str | None = None,
) -> dict[str, Any]:
    stages = sorted(curriculum.get("stages", []), key=lambda item: item.get("order", 0))
    if not stages:
        raise ValueError("curriculum requires at least one stage")
    objective_status = {
        objective["id"]: {
            "status": "not_started",
            "confidence": 0.0,
            "evidence_count": 0,
            "attempts": 0,
            "correct": 0,
            "last_updated": None,
            "last_seen_at": None,
            "next_review_at": None,
            "correct_streak": 0,
            "incorrect_streak": 0,
            "evidence_types": [],
        }
        for objective in curriculum.get("objectives", [])
    }
    return {
        "schema_version": 1,
        "certification_id": certification_id or curriculum["certification_id"],
        "curriculum_version": curriculum["curriculum_version"],
        "current_stage_id": stages[0]["id"],
        "current_lesson_id": None,
        "objective_status": objective_status,
        "completed_lesson_ids": [],
        "weak_objectives": [],
        "next_recommendation": None,
        "quiz_summary": {
            "total_attempts": 0,
            "total_correct": 0,
            "recent_results": [],
            "last_session_at": None,
        },
        "adaptive_state": {
            "last_policy_version": None,
            "last_recommendation_at": None,
            "seen_question_ids": [],
        },
        "history": [],
    }


def progress_summary(
    curriculum: dict[str, Any],
    progress: dict[str, Any],
) -> dict[str, Any]:
    statuses = progress.get("objective_status", {})
    objectives = curriculum.get("objectives", [])
    total = len(objectives)
    proficient = sum(
        1
        for objective in objectives
        if statuses.get(objective["id"], {}).get("status") == "proficient"
    )
    practicing = sum(
        1
        for objective in objectives
        if statuses.get(objective["id"], {}).get("status") in {"introduced", "practicing"}
    )
    needs_review = sum(
        1
        for objective in objectives
        if statuses.get(objective["id"], {}).get("status") == "needs_review"
    )
    summary = progress.get("quiz_summary", {})
    attempts = int(summary.get("total_attempts", 0))
    correct = int(summary.get("total_correct", 0))
    return {
        "certification_id": progress.get("certification_id"),
        "current_stage_id": progress.get("current_stage_id"),
        "objective_count": total,
        "proficient_objectives": proficient,
        "in_progress_objectives": practicing,
        "needs_review_objectives": needs_review,
        "overall_progress_percent": round((proficient / total * 100) if total else 0.0, 2),
        "quiz_attempts": attempts,
        "quiz_correct": correct,
        "quiz_accuracy": round((correct / attempts) if attempts else 0.0, 4),
        "weak_objectives": progress.get("weak_objectives", []),
        "next_recommendation": progress.get("next_recommendation"),
    }
