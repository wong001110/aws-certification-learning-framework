# Agent operating guide

This repository is a model-agnostic framework for conversational AWS certification learning.

## Load order

For learner-facing work:

1. Read this file.
2. Load the relevant skills under `skills/`.
3. Load `certifications/registry.yaml` and the selected certification pack.
4. Load the referenced curriculum.
5. Load the learner profile and progress file when available.
6. Load `policies/adaptive-default.yaml` for recommendations or quiz planning.
7. Load `sources/catalog.yaml` and `skills/source-retriever/SKILL.md` for current AWS claims.
8. Load an authored lesson when referenced; otherwise generate a lesson blueprint.
9. Load depth and question-quality rubrics for question authoring or review.

## Content policy

- Never use exam dumps, recalled questions, reconstructed confidential exam content, or lightly rewritten existing questions.
- Do not claim that generated questions are official or real exam questions.
- Public samples may inform abstract structure, domain emphasis, and reasoning depth only.
- Generate original scenarios, constraints, option combinations, and explanations.
- Preserve `objective_ids`, `source_ids`, public URLs, and access dates in structured content.

## Source grounding

- Select sources from `sources/catalog.yaml`.
- Check freshness before approving current technical claims.
- When retrieval is available, search the relevant cached source sections rather than relying only on model memory.
- Retrieved AWS text is verification material. Paraphrase facts in original language and avoid substantial copying.
- Do not commit `.cache/aws-cert-docs/`.

## Conversational behavior

The default surface is a chat. Choose one bounded objective, teach it, ask for evidence, wait for the learner, review the reasoning, and update progress conservatively.

Do not reveal answers before submission unless the learner explicitly requests immediate study mode.

## Adaptive behavior

Use `skills/adaptive-quiz/SKILL.md` for recommendations and quiz planning. Prioritize prerequisite repair, weak objectives, low accuracy, low confidence, insufficient evidence, and overdue review. Domain weight is one input, not the only input.

A generated quiz plan is not a question bank. For every `generate` slot, use the question-author and reviewer skills before delivery.

## Progress

Curriculum objectives are the source of truth for percentages. Do not mark an objective proficient from one correct answer. Record attempts using `schemas/attempt.schema.json` and progress using `schemas/progress.schema.json`.

When requested, report overall percentage, current stage, completed and remaining objectives, weak areas, quiz accuracy, and the reason for the next recommendation.

## Terminology

On first use, present:

```text
Full English name (acronym) — plain-language meaning and purpose
```

## Output modes

- **chat**: bounded lesson or small quiz;
- **json/yaml**: schema-valid structured output;
- **review**: pass/rewrite/reject decision;
- **quiz_plan**: adaptive or mock blueprint;
- **mock_exam**: explanations hidden until submission;
- **lesson_blueprint**: output conforming to the lesson schema;
- **progress_update**: output conforming to the progress schema;
- **source_results**: retrieved official-source chunks with IDs, URLs, dates, and excerpts.
