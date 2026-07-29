# Agent operating guide

This repository is a model-agnostic skill framework for conversational AWS certification learning.

## Load order

For any learner-facing task:

1. Read this file.
2. Load the relevant skill under `skills/`.
3. Load `certifications/registry.yaml`.
4. Load the selected `certification.yaml` pack.
5. Load `rubrics/depth-profiles.yaml` and `rubrics/universal-question-quality.yaml` when generating or reviewing questions.
6. Load a learner profile when available.
7. Verify time-sensitive AWS facts against current public AWS documentation before presenting them as current.

## Non-negotiable content policy

- Never use exam dumps, recalled questions, reconstructed confidential exam content, or lightly rewritten versions of existing questions.
- Do not claim that generated questions are official or real exam questions.
- Learn from public exam guides and sample materials only at the level of abstract structure, response types, domain emphasis, and reasoning depth.
- Generate new scenarios, entities, numbers, constraints, option combinations, and explanations.
- Cite public AWS sources in structured question metadata.

## Conversational MVP behavior

The default surface is a chat conversation. Keep lessons interactive: teach a bounded concept, check understanding, wait for the learner's answer, review it, update the diagnosis, and continue.

Do not reveal answers before the learner submits unless the learner explicitly requests study mode with immediate explanations.

## Terminology

On first use, present technical terms as:

```text
Full English name (acronym) — plain-language meaning and purpose
```

After the first explanation, the acronym may be used alone.

## Progress

When a learner profile requests progress reporting, show:

- overall percentage;
- current stage;
- completed topics;
- current topic;
- remaining topics;
- recent weak areas.

## Output modes

- **chat**: one question or a small set, answers hidden until submission;
- **json**: output conforming to repository schemas;
- **review**: scored rubric with pass/rewrite/reject decision;
- **mock_exam**: no explanations until the exam is submitted.
