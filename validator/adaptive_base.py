from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from math import floor
from pathlib import Path
from typing import Any, Iterable

import yaml

DEFAULT_POLICY: dict[str, Any] = {
    "schema_version": 1,
    "policy_version": "0.4",
    "weights": {
        "status_gap": 0.40,
        "accuracy_gap": 0.18,
        "confidence_gap": 0.14,
        "evidence_gap": 0.10,
        "domain_weight": 0.08,
        "recency": 0.10,
    },
    "status_values": {
        "not_started": 0.72,
        "introduced": 0.64,
        "practicing": 0.52,
        "proficient": 0.08,
        "needs_review": 1.00,
    },
    "weak_objective_bonus": 0.35,
    "core_objective_bonus": 0.08,
    "evidence_target": 3,
    "recency_days": 21,
    "prerequisite_mode": "strict",
    "max_objectives_per_session": 3,
    "activity_by_status": {
        "not_started": "lesson",
        "introduced": "focused_quiz",
        "practicing": "focused_quiz",
        "proficient": "focused_quiz",
        "needs_review": "focused_quiz",
    },
    "difficulty_by_status": {
        "not_started": "teaching",
        "introduced": "teaching",
        "practicing": "exam",
        "proficient": "pressure",
        "needs_review": "exam",
    },
    "question_type_mix": {
        "multiple_choice": 0.75,
        "multiple_response": 0.25,
    },
}


def load_policy(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        return deepcopy(DEFAULT_POLICY)
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: adaptive policy must be a YAML mapping")
    merged = deepcopy(DEFAULT_POLICY)
    for key, item in value.items():
        if isinstance(item, dict) and isinstance(merged.get(key), dict):
            merged[key].update(item)
        else:
            merged[key] = item
    return merged


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def objective_maps(curriculum: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, str]]:
    objectives = {entry["id"]: entry for entry in curriculum.get("objectives", [])}
    modules = {entry["id"]: entry for entry in curriculum.get("modules", [])}
    objective_to_module: dict[str, str] = {}
    for module in curriculum.get("modules", []):
        for objective_id in module.get("objective_ids", []):
            objective_to_module.setdefault(objective_id, module["id"])
    return objectives, modules, objective_to_module


def stage_objective_ids(curriculum: dict[str, Any], stage_id: str) -> set[str]:
    modules = {module["id"]: module for module in curriculum.get("modules", [])}
    for stage in curriculum.get("stages", []):
        if stage.get("id") == stage_id:
            return {
                objective_id
                for module_id in stage.get("module_ids", [])
                for objective_id in modules.get(module_id, {}).get("objective_ids", [])
            }
    return set()


def prerequisite_blockers(objective: dict[str, Any], progress: dict[str, Any]) -> list[str]:
    statuses = progress.get("objective_status", {})
    blockers: list[str] = []
    for prerequisite_id in objective.get("prerequisite_objective_ids", []):
        status = statuses.get(prerequisite_id, {}).get("status", "not_started")
        if status != "proficient":
            blockers.append(prerequisite_id)
    return blockers


def _domain_weight(objective: dict[str, Any], pack: dict[str, Any]) -> float:
    weights = {domain["id"]: domain["weight"] / 100 for domain in pack.get("domains", [])}
    return max((weights.get(domain_id, 0.0) for domain_id in objective.get("domain_ids", [])), default=0.0)


def _recency_score(last_updated: str | None, now: datetime, recency_days: int) -> float:
    parsed = parse_datetime(last_updated)
    if parsed is None:
        return 0.5
    days = max(0.0, (now - parsed.astimezone(now.tzinfo)).total_seconds() / 86400)
    return clamp(days / max(1, recency_days))


def _activity_for(objective: dict[str, Any], status: str, policy: dict[str, Any]) -> str:
    evidence = set(objective.get("mastery_evidence", []))
    if status == "needs_review" and "compare" in evidence:
        return "comparison"
    if status == "practicing" and "hands_on" in evidence:
        return "hands_on"
    if status in {"practicing", "proficient"} and "integrated_scenario" in evidence:
        return "integrated_scenario"
    return policy["activity_by_status"].get(status, "focused_quiz")


def recommend_objectives(
    curriculum: dict[str, Any],
    pack: dict[str, Any],
    progress: dict[str, Any],
    policy: dict[str, Any] | None = None,
    *,
    limit: int | None = None,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    policy = policy or DEFAULT_POLICY
    now = now or datetime.now(timezone.utc)
    objectives, _, _ = objective_maps(curriculum)
    status_map = progress.get("objective_status", {})
    weak = set(progress.get("weak_objectives", []))
    current = stage_objective_ids(curriculum, progress.get("current_stage_id", ""))

    candidate_ids = set(current) | weak
    if not candidate_ids:
        candidate_ids = set(objectives)

    # Add prerequisite blockers so the engine can repair the path rather than
    # recommending an objective the learner is not ready to study.
    for objective_id in list(candidate_ids):
        objective = objectives.get(objective_id, {})
        candidate_ids.update(prerequisite_blockers(objective, progress))

    weights = policy["weights"]
    evidence_target = max(1, int(policy.get("evidence_target", 3)))
    recency_days = max(1, int(policy.get("recency_days", 21)))
    prerequisite_mode = policy.get("prerequisite_mode", "strict")

    results: list[dict[str, Any]] = []
    for objective_id in candidate_ids:
        objective = objectives.get(objective_id)
        if not objective:
            continue
        blockers = prerequisite_blockers(objective, progress)
        if blockers and prerequisite_mode == "strict" and objective_id not in weak:
            continue

        state = status_map.get(objective_id, {})
        status = state.get("status", "not_started")
        attempts = int(state.get("attempts", 0))
        correct = int(state.get("correct", 0))
        confidence = float(state.get("confidence", 0.0))
        evidence_count = int(state.get("evidence_count", 0))

        accuracy_gap = 0.5 if attempts == 0 else 1 - (correct / attempts)
        confidence_gap = 1 - confidence
        evidence_gap = clamp((evidence_target - evidence_count) / evidence_target)
        recency = _recency_score(state.get("last_updated"), now, recency_days)
        status_gap = float(policy["status_values"].get(status, 0.5))
        domain_weight = _domain_weight(objective, pack)

        score = (
            status_gap * weights["status_gap"]
            + accuracy_gap * weights["accuracy_gap"]
            + confidence_gap * weights["confidence_gap"]
            + evidence_gap * weights["evidence_gap"]
            + domain_weight * weights["domain_weight"]
            + recency * weights["recency"]
        )
        reasons: list[str] = []
        if objective_id in weak:
            score += float(policy.get("weak_objective_bonus", 0.0))
            reasons.append("listed as a weak objective")
        if objective.get("importance") == "core":
            score += float(policy.get("core_objective_bonus", 0.0))
            reasons.append("core curriculum objective")
        if attempts and accuracy_gap >= 0.4:
            reasons.append(f"accuracy is {correct}/{attempts}")
        if confidence < 0.6:
            reasons.append(f"confidence is {confidence:.2f}")
        if evidence_count < evidence_target:
            reasons.append(f"evidence count is {evidence_count}/{evidence_target}")
        if blockers:
            score -= 0.25 * len(blockers)
            reasons.append(f"blocked by prerequisites: {', '.join(blockers)}")
        if not reasons:
            reasons.append("due for spaced review")

        results.append(
            {
                "objective_id": objective_id,
                "title": objective.get("title", objective_id),
                "domain_ids": objective.get("domain_ids", []),
                "status": status,
                "score": round(score, 6),
                "activity_type": _activity_for(objective, status, policy),
                "difficulty": policy["difficulty_by_status"].get(status, "exam"),
                "prerequisite_blockers": blockers,
                "reason": "; ".join(reasons),
            }
        )

    results.sort(key=lambda item: (-item["score"], item["objective_id"]))
    max_items = limit or int(policy.get("max_objectives_per_session", 3))
    return results[:max_items]
