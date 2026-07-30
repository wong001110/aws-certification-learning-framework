---
name: lesson-author
description: Create structured adaptive AWS certification lesson blueprints from curriculum objectives and fresh official AWS sources.
---

# Lesson Author

Create a reusable blueprint conforming to `schemas/lesson.schema.json`. It is executed conversationally and is not a fixed lecture script.

## Inputs

- certification pack and curriculum;
- one module and one to three related objectives;
- learner profile and progress when available;
- `sources/catalog.yaml` and retrieved current AWS evidence.

## Process

1. Confirm objective IDs, domains, prerequisites, and curriculum version.
2. Select fresh relevant source IDs through the source-retriever skill.
3. Define a bounded outcome and estimated duration.
4. Build orientation, explanation, comparison or worked example, knowledge check, and summary.
5. Add hands-on work only when the certification expects implementation evidence.
6. Map observable knowledge-check evidence directly to objectives.
7. Preserve source IDs, URLs, and access dates.
8. Keep instructions adaptable rather than scripting exact prose.
9. Independently review before approval.

## Depth

- Foundational: concepts, use cases, business value, shared responsibility, recognition.
- Associate: practical choices, service boundaries, troubleshooting, and tradeoffs.
- Professional: organizational, migration, governance, and multi-system constraints.
- Specialty: deeper failure analysis and implementation detail.

Do not invent quotas, prices, or current feature behavior. Do not use dumps or closely paraphrase public samples.
