from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from math import floor
from pathlib import Path
from typing import Any, Iterable

from validator.adaptive_base import DEFAULT_POLICY, objective_maps, recommend_objectives

def _largest_remainder_counts(weights: dict[str, float], total: int) -> dict[str, int]:
    if total <= 0:
        return {key: 0 for key in weights}
    positive = {key: max(0.0, value) for key, value in weights.items()}
    denominator = sum(positive.values()) or 1.0
    exact = {key: total * value / denominator for key, value in positive.items()}
    counts = {key: floor(value) for key, value in exact.items()}
    remaining = total - sum(counts.values())
    order = sorted(exact, key=lambda key: (-(exact[key] - counts[key]), key))
    for key in order[:remaining]:
        counts[key] += 1
    return counts


def mock_domain_counts(pack: dict[str, Any], total: int) -> dict[str, int]:
    return _largest_remainder_counts(
        {domain["id"]: float(domain["weight"]) for domain in pack.get("domains", [])},
        total,
    )


def question_type_counts(pack: dict[str, Any], policy: dict[str, Any], total: int) -> dict[str, int]:
    allowed = set(pack.get("question_types", []))
    configured = {
        key: float(value)
        for key, value in policy.get("question_type_mix", {}).items()
        if key in allowed
    }
    if not configured:
        configured = {key: 1.0 for key in allowed}
    return _largest_remainder_counts(configured, total)


def load_question_bank(paths: Iterable[Path]) -> list[dict[str, Any]]:
    import json

    bank: list[dict[str, Any]] = []
    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            bank.append({"path": str(path), "question": value})
    return bank


def assemble_quiz_plan(
    *,
    certification_id: str,
    curriculum: dict[str, Any],
    pack: dict[str, Any],
    progress: dict[str, Any] | None,
    question_bank: list[dict[str, Any]],
    count: int,
    mode: str,
    policy: dict[str, Any] | None = None,
    generated_at: datetime | None = None,
    time_limit_minutes: int | None = None,
) -> dict[str, Any]:
    if count <= 0:
        raise ValueError("question count must be positive")
    policy = policy or DEFAULT_POLICY
    generated_at = generated_at or datetime.now(timezone.utc)
    objectives, _, _ = objective_maps(curriculum)

    if mode == "mock":
        domain_counts = mock_domain_counts(pack, count)
        recommended = []
    else:
        if progress is None:
            raise ValueError("adaptive and focused quiz plans require progress")
        recommended = recommend_objectives(
            curriculum,
            pack,
            progress,
            policy,
            limit=max(1, min(count, int(policy.get("max_objectives_per_session", 3)))),
            now=generated_at,
        )
        domain_weights: dict[str, float] = defaultdict(float)
        for index, recommendation in enumerate(recommended):
            priority = len(recommended) - index
            for domain_id in recommendation["domain_ids"]:
                domain_weights[domain_id] += priority
        domain_counts = _largest_remainder_counts(dict(domain_weights), count)

    type_counts = question_type_counts(pack, policy, count)
    type_queue = [
        question_type
        for question_type, amount in sorted(type_counts.items())
        for _ in range(amount)
    ]
    domain_queue = [
        domain_id
        for domain_id, amount in sorted(domain_counts.items())
        for _ in range(amount)
    ]
    while len(domain_queue) < count:
        domain_queue.append(pack["domains"][len(domain_queue) % len(pack["domains"])]["id"])

    objective_by_domain: dict[str, list[str]] = defaultdict(list)
    if recommended:
        for item in recommended:
            for domain_id in item["domain_ids"]:
                objective_by_domain[domain_id].append(item["objective_id"])
    else:
        for objective in curriculum.get("objectives", []):
            for domain_id in objective.get("domain_ids", []):
                objective_by_domain[domain_id].append(objective["id"])

    unused_bank = [
        item
        for item in question_bank
        if item["question"].get("certification_id") == certification_id
    ]
    slots: list[dict[str, Any]] = []
    objective_rotation: dict[str, int] = defaultdict(int)

    for position in range(1, count + 1):
        domain_id = domain_queue[position - 1]
        question_type = type_queue[position - 1] if position - 1 < len(type_queue) else pack["question_types"][0]
        candidates = objective_by_domain.get(domain_id) or list(objectives)
        objective_id = candidates[objective_rotation[domain_id] % len(candidates)]
        objective_rotation[domain_id] += 1
        status = (progress or {}).get("objective_status", {}).get(objective_id, {}).get("status", "practicing")
        difficulty = policy["difficulty_by_status"].get(status, "exam") if mode != "mock" else "exam"

        existing_index = next(
            (
                index
                for index, item in enumerate(unused_bank)
                if item["question"].get("domain_id") == domain_id
                and question_type == item["question"].get("question_type")
                and (
                    not item["question"].get("objective_ids")
                    or objective_id in item["question"].get("objective_ids", [])
                )
            ),
            None,
        )
        if existing_index is not None:
            existing = unused_bank.pop(existing_index)
            source = {
                "kind": "existing",
                "question_id": existing["question"]["id"],
                "path": existing["path"],
            }
        else:
            source = {
                "kind": "generate",
                "authoring_constraints": {
                    "objective_ids": [objective_id],
                    "domain_id": domain_id,
                    "difficulty": difficulty,
                    "question_type": question_type,
                    "official_sources_required": True,
                    "original_content_required": True,
                },
            }
        slots.append(
            {
                "position": position,
                "domain_id": domain_id,
                "objective_ids": [objective_id],
                "difficulty": difficulty,
                "question_type": question_type,
                "source": source,
                "selection_reason": (
                    "weighted official-domain coverage" if mode == "mock" else "adaptive objective priority"
                ),
            }
        )

    return {
        "schema_version": 1,
        "id": f"{certification_id.lower()}-{mode}-{generated_at.strftime('%Y%m%dT%H%M%SZ')}",
        "certification_id": certification_id,
        "mode": mode,
        "generated_at": generated_at.isoformat(),
        "policy_version": str(policy.get("policy_version", "0.4")),
        "question_count": count,
        "time_limit_minutes": time_limit_minutes,
        "domain_distribution": domain_counts,
        "question_type_distribution": type_counts,
        "objective_ids": sorted({objective for slot in slots for objective in slot["objective_ids"]}),
        "slots": slots,
        "notice": "This is an unofficial planning blueprint. Generated questions must be original and independently reviewed.",
    }
