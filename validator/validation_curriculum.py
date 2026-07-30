from __future__ import annotations

from pathlib import Path
from typing import Any

from validator.sources import is_official_aws_url
from validator.validation_common import (
    ROOT,
    _cycle_nodes,
    _load_catalog_if_available,
    duplicate_values,
    load_yaml,
    validate_catalog_references,
    validate_schema,
)


def validate_lesson(
    lesson: dict[str, Any],
    path: Path,
    certification_id: str,
    curriculum_version: str,
    objective_ids: set[str],
    source_catalog: dict[str, Any] | None = None,
) -> list[str]:
    errors = validate_schema(lesson, ROOT / "schemas" / "lesson.schema.json", path)
    source_catalog = source_catalog if source_catalog is not None else _load_catalog_if_available()

    if lesson.get("certification_id") != certification_id:
        errors.append(f"{path}: lesson certification_id does not match curriculum")
    if lesson.get("curriculum_version") != curriculum_version:
        errors.append(f"{path}: lesson curriculum_version does not match curriculum")

    unknown_objectives = set(lesson.get("objective_ids", [])) - objective_ids
    if unknown_objectives:
        errors.append(f"{path}: lesson references unknown objectives {sorted(unknown_objectives)}")

    check_ids = [check.get("id") for check in lesson.get("knowledge_checks", [])]
    duplicates = duplicate_values(check_ids)
    if duplicates:
        errors.append(f"{path}: duplicate knowledge check ids {sorted(duplicates)}")

    review = lesson.get("review", {})
    approved = review.get("status") == "approved"
    errors.extend(
        validate_catalog_references(
            sources=lesson.get("sources", []),
            source_ids=lesson.get("source_ids", []),
            path=path,
            label="lesson",
            source_catalog=source_catalog,
            require_ids=approved,
        )
    )
    if approved and not review.get("verified_at"):
        errors.append(f"{path}: approved lessons require verified_at")
    return errors


def validate_curriculum(
    curriculum: dict[str, Any],
    path: Path,
    certification_id: str,
    expected_version: str,
    allowed_domains: set[str],
    source_catalog: dict[str, Any] | None = None,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors = validate_schema(curriculum, ROOT / "schemas" / "curriculum.schema.json", path)
    source_catalog = source_catalog if source_catalog is not None else _load_catalog_if_available()
    lessons: dict[str, dict[str, Any]] = {}

    if curriculum.get("certification_id") != certification_id:
        errors.append(f"{path}: curriculum certification_id does not match pack")
    if curriculum.get("curriculum_version") != expected_version:
        errors.append(f"{path}: curriculum version does not match pack")

    stages = curriculum.get("stages", [])
    modules = curriculum.get("modules", [])
    objectives = curriculum.get("objectives", [])
    stage_ids = [stage.get("id") for stage in stages]
    module_ids = [module.get("id") for module in modules]
    objective_id_list = [objective.get("id") for objective in objectives]

    for label, values in (("stage", stage_ids), ("module", module_ids), ("objective", objective_id_list)):
        duplicates = duplicate_values(values)
        if duplicates:
            errors.append(f"{path}: duplicate {label} ids {sorted(duplicates)}")

    stage_orders = [stage.get("order") for stage in stages]
    if len(stage_orders) != len(set(stage_orders)):
        errors.append(f"{path}: duplicate stage order")
    elif sorted(stage_orders) != list(range(1, len(stage_orders) + 1)):
        errors.append(f"{path}: stage order values must form a continuous sequence from 1")

    known_modules = set(module_ids)
    known_objectives = set(objective_id_list)
    module_graph: dict[str, set[str]] = {}
    objective_graph: dict[str, set[str]] = {}

    for stage in stages:
        unknown = set(stage.get("module_ids", [])) - known_modules
        if unknown:
            errors.append(f"{path}: stage {stage.get('id')} references unknown modules {sorted(unknown)}")

    for objective in objectives:
        objective_id = objective.get("id")
        unknown_domains = set(objective.get("domain_ids", [])) - allowed_domains
        if unknown_domains:
            errors.append(f"{path}: objective {objective_id} uses unknown domains {sorted(unknown_domains)}")
        prerequisites = set(objective.get("prerequisite_objective_ids", []))
        objective_graph[str(objective_id)] = prerequisites
        unknown_prerequisites = prerequisites - known_objectives
        if unknown_prerequisites:
            errors.append(
                f"{path}: objective {objective_id} references unknown prerequisite objectives "
                f"{sorted(unknown_prerequisites)}"
            )
        if objective_id in prerequisites:
            errors.append(f"{path}: objective {objective_id} cannot require itself")

    for module in modules:
        module_id = module.get("id")
        unknown_domains = set(module.get("domain_ids", [])) - allowed_domains
        if unknown_domains:
            errors.append(f"{path}: module {module_id} uses unknown domains {sorted(unknown_domains)}")
        unknown_objectives = set(module.get("objective_ids", [])) - known_objectives
        if unknown_objectives:
            errors.append(f"{path}: module {module_id} references unknown objectives {sorted(unknown_objectives)}")
        prerequisites = set(module.get("prerequisite_module_ids", []))
        module_graph[str(module_id)] = prerequisites
        unknown_prerequisites = prerequisites - known_modules
        if unknown_prerequisites:
            errors.append(
                f"{path}: module {module_id} references unknown prerequisite modules "
                f"{sorted(unknown_prerequisites)}"
            )
        if module_id in prerequisites:
            errors.append(f"{path}: module {module_id} cannot require itself")

        for lesson_path_value in module.get("lesson_paths", []):
            lesson_path = ROOT / lesson_path_value
            if not lesson_path.exists():
                errors.append(f"{path}: module {module_id} references missing lesson {lesson_path_value}")
                continue
            lesson = load_yaml(lesson_path)
            lesson_id = lesson.get("id")
            if lesson_id in lessons:
                errors.append(f"{path}: duplicate referenced lesson id {lesson_id}")
            lessons[str(lesson_id)] = lesson
            errors.extend(
                validate_lesson(
                    lesson,
                    lesson_path,
                    certification_id,
                    expected_version,
                    known_objectives,
                    source_catalog,
                )
            )

    module_cycles = _cycle_nodes(module_graph)
    if module_cycles:
        errors.append(f"{path}: module prerequisites contain a cycle {sorted(module_cycles)}")
    objective_cycles = _cycle_nodes(objective_graph)
    if objective_cycles:
        errors.append(f"{path}: objective prerequisites contain a cycle {sorted(objective_cycles)}")

    known_lessons = set(lessons)
    for lesson_id, lesson in lessons.items():
        unknown = set(lesson.get("prerequisite_lesson_ids", [])) - known_lessons
        if unknown:
            errors.append(f"{path}: lesson {lesson_id} references unknown prerequisite lessons {sorted(unknown)}")

    errors.extend(
        validate_catalog_references(
            sources=curriculum.get("sources", []),
            source_ids=curriculum.get("source_ids", []),
            path=path,
            label="curriculum",
            source_catalog=source_catalog,
            require_ids=source_catalog is not None,
        )
    )
    return errors, lessons


def validate_certification_packs(
    certifications: dict[str, dict[str, Any]],
    source_catalog: dict[str, Any] | None = None,
) -> tuple[
    list[str],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, dict[str, Any]]],
]:
    errors: list[str] = []
    packs: dict[str, dict[str, Any]] = {}
    curricula: dict[str, dict[str, Any]] = {}
    lessons: dict[str, dict[str, dict[str, Any]]] = {}
    schema_path = ROOT / "schemas" / "certification.schema.json"
    source_catalog = source_catalog if source_catalog is not None else _load_catalog_if_available()
    source_urls = {source["url"] for source in (source_catalog or {}).get("sources", [])}

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
        duplicates = duplicate_values(domain_ids)
        if duplicates:
            errors.append(f"{pack_path}: duplicate domain ids {sorted(duplicates)}")

        source = pack.get("source", {}).get("exam_guide", "")
        if not is_official_aws_url(source):
            errors.append(f"{pack_path}: exam guide must use an official AWS URL")
        if source_catalog is not None and source not in source_urls:
            errors.append(f"{pack_path}: exam guide URL is missing from sources/catalog.yaml")

        curriculum_config = pack.get("curriculum", {})
        curriculum_path_value = curriculum_config.get("path")
        expected_version = curriculum_config.get("version")
        if not curriculum_path_value:
            errors.append(f"{pack_path}: certification pack requires a curriculum path")
            continue
        curriculum_path = ROOT / curriculum_path_value
        if not curriculum_path.exists():
            errors.append(f"{pack_path}: curriculum path does not exist")
            continue

        curriculum = load_yaml(curriculum_path)
        curricula[certification_id] = curriculum
        curriculum_errors, lesson_map = validate_curriculum(
            curriculum,
            curriculum_path,
            certification_id,
            expected_version,
            set(domain_ids),
            source_catalog,
        )
        errors.extend(curriculum_errors)
        lessons[certification_id] = lesson_map

    return errors, packs, curricula, lessons
