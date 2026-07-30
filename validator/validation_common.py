from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from validator.sources import catalog_source_map, is_official_aws_url, load_source_catalog

ROOT = Path(__file__).resolve().parents[1]


class ValidationFailure(Exception):
    """Raised when repository content violates a deterministic rule."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path}: expected a JSON object")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path}: expected a YAML mapping")
    return value


def load_structured(path: Path) -> dict[str, Any]:
    return load_json(path) if path.suffix.lower() == ".json" else load_yaml(path)


def validate_schema(
    instance: dict[str, Any],
    schema_path: Path,
    instance_path: Path,
) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{instance_path}: {'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in sorted(
            validator.iter_errors(instance),
            key=lambda item: list(item.absolute_path),
        )
    ]


def load_registry() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    registry = load_yaml(ROOT / "certifications" / "registry.yaml")
    entries = registry.get("certifications", [])
    certifications = {entry["id"]: entry for entry in entries}
    if len(certifications) != len(entries):
        raise ValidationFailure("certifications/registry.yaml: duplicate certification id")
    return registry, certifications


def duplicate_values(values: Iterable[str | None]) -> set[str | None]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def validate_source_list(
    sources: list[dict[str, Any]],
    path: Path,
    label: str,
) -> list[str]:
    if not sources:
        return [f"{path}: {label} requires at least one source"]
    if not all(is_official_aws_url(source.get("url", "")) for source in sources):
        return [f"{path}: all {label} sources must use official AWS hosts"]
    return []


def _load_catalog_if_available() -> dict[str, Any] | None:
    path = ROOT / "sources" / "catalog.yaml"
    return load_source_catalog(path) if path.exists() else None


def validate_catalog_references(
    *,
    sources: list[dict[str, Any]],
    source_ids: list[str],
    path: Path,
    label: str,
    source_catalog: dict[str, Any] | None,
    require_ids: bool,
) -> list[str]:
    errors = validate_source_list(sources, path, label)
    if source_catalog is None:
        return errors
    if require_ids and not source_ids:
        errors.append(f"{path}: {label} requires source_ids from sources/catalog.yaml")
        return errors

    source_map = catalog_source_map(source_catalog)
    unknown_ids = set(source_ids) - set(source_map)
    if unknown_ids:
        errors.append(f"{path}: {label} references unknown source_ids {sorted(unknown_ids)}")
        return errors

    catalog_urls = {source_map[source_id]["url"] for source_id in source_ids}
    content_urls = {source.get("url") for source in sources}
    if source_ids and catalog_urls != content_urls:
        missing = sorted(catalog_urls - content_urls)
        extra = sorted(content_urls - catalog_urls)
        if missing:
            errors.append(f"{path}: {label} source_ids resolve to unlisted URLs {missing}")
        if extra:
            errors.append(f"{path}: {label} contains URLs without matching source_ids {extra}")
    return errors


def _cycle_nodes(graph: dict[str, set[str]]) -> set[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            if node in trail:
                cycles.update(trail[trail.index(node) :])
            else:
                cycles.add(node)
            return
        if node in visited:
            return
        visiting.add(node)
        trail.append(node)
        for neighbor in graph.get(node, set()):
            if neighbor in graph:
                visit(neighbor, trail)
        trail.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node, [])
    return cycles
