---
name: question-reviewer
description: Independently review AWS practice questions for technical correctness, source freshness, answer uniqueness, depth, and distractor quality.
---

# Question Reviewer

## Review sequence

1. Validate `schemas/question.schema.json`.
2. Check certification, domain, and objective IDs against the pack and curriculum.
3. Resolve `source_ids` through `sources/catalog.yaml` and check freshness.
4. Retrieve relevant official sections when available and verify each technical assertion.
5. Solve independently without reading the declared answer first when possible.
6. Compare the independent answer with the declared answer.
7. Test whether another option also satisfies all requirements.
8. Score with `rubrics/universal-question-quality.yaml`.
9. Return `approved`, `rewrite`, or `rejected`.

## Automatic rejection

Reject incorrect AWS facts, ambiguous answers, copied or reconstructed confidential content, unsupported superlative claims, wrong depth, mismatched source IDs and URLs, obsolete behavior, or missing option analysis.

## Rewrite

Rewrite is required for weak distractors, unused constraints, wording clues, conspicuously long correct answers, or questions solvable through one superficial keyword.

Return scores, retrieved evidence IDs, failure modes, and precise rewrite instructions. Do not silently fix and approve in the same review pass.
