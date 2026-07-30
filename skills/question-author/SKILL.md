---
name: question-author
description: Generate independently authored AWS certification practice questions at the correct certification depth with official-source grounding.
---

# Question Author

## Required inputs

- certification pack and curriculum objective IDs;
- exam domain and depth profile;
- desired response type;
- `sources/catalog.yaml` and current retrieved AWS evidence;
- optional learner weaknesses or quiz-plan slot.

## Workflow

1. Select one assessable curriculum objective or a coherent objective pair.
2. Use `skills/source-retriever/SKILL.md` to select fresh catalog sources and verify technical facts.
3. Design an original scenario, not a paraphrase of an existing question.
4. Add only constraints needed to determine the best response.
5. Create the correct response before distractors.
6. Create distractors representing distinct incomplete mental models.
7. Confirm response count, answer uniqueness, and certification depth.
8. Write decisive constraints and option-by-option analysis.
9. Preserve `objective_ids`, `source_ids`, matching URLs, and access dates.
10. Output JSON conforming to `schemas/question.schema.json`.
11. Send the result through the Question Reviewer before approval.

## Depth

Read `rubrics/depth-profiles.yaml`. Do not turn foundational certifications into implementation exams. Do not reduce professional or specialty certifications to definition recall.

## Distractors

A distractor should be plausible and fail for a specific reason: hard-requirement violation, partial solution, excess overhead, wrong service boundary, unnecessary cost, or incorrect technical assumption.

Avoid fake services, nonsense choices, grammatical clues, predictable answer positions, and keyword-only matching.

## Originality

Never use confidential exam content, recalled questions, reconstructed questions, or lightly rewritten official or third-party questions. Public samples may inform abstract style and depth only.
