# Changelog

All notable framework changes are documented here.

## 0.4.0 - 2026-07-30

### Added

- Command-line interface for validation, progress initialization, recommendations, quiz planning, attempt recording, question review, source synchronization, source search, and freshness reporting.
- Explainable adaptive objective prioritization and spaced-review metadata.
- Adaptive, focused, and official-domain-weighted mock-exam plan schemas.
- Attempt schema and deterministic progress-update workflow.
- Versioned catalog of official AWS sources covering all five reference packs.
- Optional local official-document cache, HTML chunking, SHA-256 tracking, and BM25-style lexical retrieval.
- Source-aware agent skills, contributor documentation, examples, and regression tests.
- Scheduled source-freshness workflow.

### Changed

- Approved questions and lessons now map human-readable sources to catalog `source_ids`.
- Curricula now identify their catalog sources.
- Progress can store streaks, next-review dates, quiz summaries, and adaptive state.
- Package version updated to 0.4.0.

## 0.2.0 - 2026-07-30

### Added

- Structured curriculum, lesson, and adaptive progress schemas.
- Curriculum-driven objectives, stages, modules, prerequisites, and mastery evidence.
- Reusable lesson-author skill and five approved lesson blueprints.
- Adaptive progress example and contributor templates.
- Developer Associate (DVA-C02) and Data Engineer Associate (DEA-C01) reference packs.
- Curriculum, lesson, cross-reference, and progress validation.

### Changed

- Learning planner, tutor, progress coach, and agent load order use structured curricula.
- Existing CLF-C02, AIF-C01, and SAA-C03 packs reference versioned curricula.

## 0.1.0 - 2026-07-30

- Initial conversational skill framework, registry, three reference packs, question schema, validator, tests, and CI.
