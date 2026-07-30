from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from validator.adaptive import (
    assemble_quiz_plan,
    initialize_progress,
    load_policy,
    load_question_bank,
    progress_summary,
    recommend_objectives,
    update_progress_from_attempt,
)
from validator.sources import (
    DEFAULT_CACHE_DIR,
    catalog_source_map,
    freshness_report,
    load_source_catalog,
    search_cached_sources,
    sync_catalog_sources,
)
from validator.validate import (
    ROOT,
    load_json,
    load_registry,
    load_structured,
    validate_all,
    validate_attempt,
    validate_certification_packs,
    validate_question,
)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _write_structured(value: dict[str, Any] | list[Any], path: Path | None) -> None:
    if path is None:
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(path)


def _framework() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, dict[str, Any]]],
    dict[str, Any],
]:
    _, certifications = load_registry()
    catalog = load_source_catalog(ROOT / "sources" / "catalog.yaml")
    errors, packs, curricula, lessons = validate_certification_packs(certifications, catalog)
    if errors:
        raise ValueError("framework content is invalid:\n- " + "\n- ".join(errors))
    return certifications, packs, curricula, lessons, catalog


def _certification(
    certification_id: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    _, packs, curricula, lessons, catalog = _framework()
    if certification_id not in packs or certification_id not in curricula:
        raise ValueError(f"unsupported certification pack: {certification_id}")
    return packs[certification_id], curricula[certification_id], lessons.get(certification_id, {}), catalog


def command_validate(args: argparse.Namespace) -> int:
    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    errors = validate_all(as_of=as_of, strict_freshness=args.strict_freshness)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed.")
    return 0


def command_init_progress(args: argparse.Namespace) -> int:
    _, curriculum, _, _ = _certification(args.certification)
    progress = initialize_progress(curriculum, certification_id=args.certification)
    _write_structured(progress, Path(args.output) if args.output else None)
    return 0


def command_recommend(args: argparse.Namespace) -> int:
    pack, curriculum, _, _ = _certification(args.certification)
    progress = load_structured(Path(args.progress))
    policy = load_policy(Path(args.policy) if args.policy else ROOT / "policies" / "adaptive-default.yaml")
    recommendations = recommend_objectives(
        curriculum,
        pack,
        progress,
        policy,
        limit=args.limit,
        now=_parse_datetime(args.as_of),
    )
    result = {"summary": progress_summary(curriculum, progress), "recommendations": recommendations}
    _write_structured(result, Path(args.output) if args.output else None)
    return 0


def command_quiz_plan(args: argparse.Namespace) -> int:
    pack, curriculum, _, _ = _certification(args.certification)
    progress = load_structured(Path(args.progress)) if args.progress else None
    policy = load_policy(Path(args.policy) if args.policy else ROOT / "policies" / "adaptive-default.yaml")
    question_bank = load_question_bank(sorted((ROOT / "examples" / "questions").glob("*.json")))
    generated_at = _parse_datetime(args.generated_at)
    plan = assemble_quiz_plan(
        certification_id=args.certification,
        curriculum=curriculum,
        pack=pack,
        progress=progress,
        question_bank=question_bank,
        count=args.count,
        mode=args.mode,
        policy=policy,
        generated_at=generated_at,
        time_limit_minutes=args.time_limit,
    )
    _write_structured(plan, Path(args.output) if args.output else None)
    return 0


def command_record_attempt(args: argparse.Namespace) -> int:
    pack, curriculum, _, _ = _certification(args.certification)
    progress_path = Path(args.progress)
    progress = load_structured(progress_path)
    attempt_path = Path(args.attempt)
    attempt = load_structured(attempt_path)
    errors = validate_attempt(attempt, attempt_path, {args.certification: pack}, {args.certification: curriculum})
    if errors:
        print("Attempt validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    policy = load_policy(Path(args.policy) if args.policy else ROOT / "policies" / "adaptive-default.yaml")
    updated = update_progress_from_attempt(progress, attempt, curriculum, pack, policy)
    output = Path(args.output) if args.output else progress_path
    _write_structured(updated, output)
    return 0


def command_progress_summary(args: argparse.Namespace) -> int:
    _, curriculum, _, _ = _certification(args.certification)
    progress = load_structured(Path(args.progress))
    _write_structured(progress_summary(curriculum, progress), Path(args.output) if args.output else None)
    return 0


def command_question_review(args: argparse.Namespace) -> int:
    certifications, packs, curricula, _, catalog = _framework()
    path = Path(args.question)
    question = load_json(path)
    errors = validate_question(question, path, certifications, packs, curricula, catalog)
    result = {
        "question_id": question.get("id"),
        "decision": "pass" if not errors else "rewrite",
        "errors": errors,
    }
    _write_structured(result, Path(args.output) if args.output else None)
    return 0 if not errors else 1


def command_source_freshness(args: argparse.Namespace) -> int:
    catalog = load_source_catalog(ROOT / "sources" / "catalog.yaml")
    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    report = freshness_report(catalog, as_of=as_of, certification_id=args.certification)
    summary = Counter(item["status"] for item in report)
    result = {"as_of": (as_of or date.today()).isoformat(), "summary": dict(summary), "sources": report}
    _write_structured(result, Path(args.output) if args.output else None)
    stale = [item for item in report if item["status"] in {"stale", "future"}]
    return 1 if args.fail_on_stale and stale else 0


def command_source_sync(args: argparse.Namespace) -> int:
    catalog = load_source_catalog(ROOT / "sources" / "catalog.yaml")
    source_map = catalog_source_map(catalog)
    source_ids = list(args.source_id or [])
    if args.certification:
        source_ids.extend(
            source["id"]
            for source in catalog.get("sources", [])
            if args.certification in source.get("certification_ids", [])
        )
    if args.all:
        source_ids.extend(source_map)
    source_ids = sorted(set(source_ids))
    if not source_ids:
        raise ValueError("select --source-id, --certification, or --all")
    cache_dir = Path(args.cache_dir) if args.cache_dir else DEFAULT_CACHE_DIR
    paths = sync_catalog_sources(catalog, source_ids, cache_dir=cache_dir, force=args.force)
    _write_structured(
        {"synced": [{"source_id": path.stem, "cache_path": str(path)} for path in paths]},
        Path(args.output) if args.output else None,
    )
    return 0


def command_source_search(args: argparse.Namespace) -> int:
    catalog = load_source_catalog(ROOT / "sources" / "catalog.yaml")
    results = search_cached_sources(
        args.query,
        catalog=catalog,
        cache_dir=Path(args.cache_dir) if args.cache_dir else DEFAULT_CACHE_DIR,
        certification_id=args.certification,
        source_ids=set(args.source_id or []) or None,
        limit=args.limit,
    )
    _write_structured(
        {"query": args.query, "result_count": len(results), "results": results},
        Path(args.output) if args.output else None,
    )
    return 0 if results else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aws-cert",
        description="CLI for the AWS Certification Learning Framework.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate repository content")
    validate_parser.add_argument("--strict-freshness", action="store_true")
    validate_parser.add_argument("--as-of", help="ISO date used for freshness checks")
    validate_parser.set_defaults(handler=command_validate)

    init_parser = subparsers.add_parser("init-progress", help="Create a clean progress file")
    init_parser.add_argument("--certification", required=True)
    init_parser.add_argument("--output")
    init_parser.set_defaults(handler=command_init_progress)

    recommend_parser = subparsers.add_parser("recommend", help="Recommend the next adaptive activities")
    recommend_parser.add_argument("--certification", required=True)
    recommend_parser.add_argument("--progress", required=True)
    recommend_parser.add_argument("--policy")
    recommend_parser.add_argument("--limit", type=int, default=3)
    recommend_parser.add_argument("--as-of", help="ISO datetime used for recency scoring")
    recommend_parser.add_argument("--output")
    recommend_parser.set_defaults(handler=command_recommend)

    plan_parser = subparsers.add_parser("quiz-plan", help="Create an adaptive quiz or mock exam plan")
    plan_parser.add_argument("--certification", required=True)
    plan_parser.add_argument("--mode", choices=["adaptive", "focused", "mock"], default="adaptive")
    plan_parser.add_argument("--progress")
    plan_parser.add_argument("--policy")
    plan_parser.add_argument("--count", type=int, default=10)
    plan_parser.add_argument("--time-limit", type=int)
    plan_parser.add_argument("--generated-at", help="ISO datetime for deterministic output")
    plan_parser.add_argument("--output")
    plan_parser.set_defaults(handler=command_quiz_plan)

    attempt_parser = subparsers.add_parser("record-attempt", help="Apply one attempt to a progress file")
    attempt_parser.add_argument("--certification", required=True)
    attempt_parser.add_argument("--progress", required=True)
    attempt_parser.add_argument("--attempt", required=True)
    attempt_parser.add_argument("--policy")
    attempt_parser.add_argument("--output")
    attempt_parser.set_defaults(handler=command_record_attempt)

    summary_parser = subparsers.add_parser("progress-summary", help="Summarize objective progress")
    summary_parser.add_argument("--certification", required=True)
    summary_parser.add_argument("--progress", required=True)
    summary_parser.add_argument("--output")
    summary_parser.set_defaults(handler=command_progress_summary)

    review_parser = subparsers.add_parser("question-review", help="Run deterministic question review")
    review_parser.add_argument("--question", required=True)
    review_parser.add_argument("--output")
    review_parser.set_defaults(handler=command_question_review)

    freshness_parser = subparsers.add_parser("source-freshness", help="Report source verification freshness")
    freshness_parser.add_argument("--certification")
    freshness_parser.add_argument("--as-of", help="ISO date")
    freshness_parser.add_argument("--fail-on-stale", action="store_true")
    freshness_parser.add_argument("--output")
    freshness_parser.set_defaults(handler=command_source_freshness)

    sync_parser = subparsers.add_parser("source-sync", help="Cache selected official AWS documentation")
    sync_parser.add_argument("--source-id", action="append")
    sync_parser.add_argument("--certification")
    sync_parser.add_argument("--all", action="store_true")
    sync_parser.add_argument("--cache-dir")
    sync_parser.add_argument("--force", action="store_true")
    sync_parser.add_argument("--output")
    sync_parser.set_defaults(handler=command_source_sync)

    search_parser = subparsers.add_parser("source-search", help="Search cached official AWS documentation")
    search_parser.add_argument("query")
    search_parser.add_argument("--certification")
    search_parser.add_argument("--source-id", action="append")
    search_parser.add_argument("--cache-dir")
    search_parser.add_argument("--limit", type=int, default=5)
    search_parser.add_argument("--output")
    search_parser.set_defaults(handler=command_source_search)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (KeyError, OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
