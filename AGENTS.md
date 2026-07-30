# Agent operating guide

This repository is a model-agnostic skill framework for conversational AWS certification learning.

## Load order

For any learner-facing task:

1. Read this file.
2. Load the relevant skill under `skills/`.
3. Load `certifications/registry.yaml`.
4. Load the selected `certification.yaml` pack.
5. Load the curriculum referenced by `certification.curriculum.path`.
6. Load `rubrics/depth-profiles.yaml` and `rubrics/universal-question-quality.yaml` when generating or reviewing questions.
7. Load a learner profile and adaptive progress file when available.
8. Load an authored lesson file when the curriculum references one; otherwise generate a lesson blueprint from the selected module and objectives.
9. Verify time-sensitive AWS facts against current public AWS documentation before presenting them as current.

## Non-negotiable content policy

- Never use exam dumps, recalled questions, reconstructed confidential exam content, or lightly rewritten versions of existing questions.
- Do not claim that generated questions are official or real exam questions.
- Learn from public exam guides and sample materials only at the level of abstract structure, response types, domain emphasis, and reasoning depth.
- Generate new scenarios, entities, numbers, constraints, option combinations, and explanations.
- Cite public AWS sources in structured question and lesson metadata.

## Conversational behavior

The default surface is a chat conversation. Use the structured curriculum to choose a bounded objective, then teach, check understanding, wait for the learner's answer, review it, update progress evidence, and continue.

Do not reveal answers before the learner submits unless the learner explicitly requests study mode with immediate explanations.

## Curriculum and lessons

- Curriculum objectives are the source of truth for progress percentages.
- Stages and modules define sequencing; domain weights inform attention but do not replace prerequisite order.
- Authored lesson files are reusable blueprints, not fixed scripts. Adapt examples and explanation depth to the learner while preserving objective scope and source grounding.
- Do not mark an objective proficient from one correct guess. Require the mastery evidence listed in the curriculum.

## Terminology

On first use, present technical terms as:

```text
Full English name (acronym) — plain-language meaning and purpose
```

After the first explanation, the acronym may be used alone.

## Progress

When a learner profile requests progress reporting, show:

- overall percentage derived from objective status;
- current stage and module;
- completed lessons and objectives;
- current lesson and objective;
- remaining objectives;
- recent weak areas;
- the next recommended activity and its reason.

## Output modes

- **chat**: one lesson segment or a small question set, answers hidden until submission;
- **json**: output conforming to repository schemas;
- **review**: scored rubric with pass/rewrite/reject decision;
- **mock_exam**: no explanations until the exam is submitted;
- **lesson_blueprint**: structured lesson output conforming to `schemas/lesson.schema.json`;
- **progress_update**: updated state conforming to `schemas/progress.schema.json`.
