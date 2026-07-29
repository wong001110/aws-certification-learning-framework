---
name: question-reviewer
description: Independently review AWS practice questions for technical correctness, answer uniqueness, depth, distractor quality, and source compliance.
---

# Question Reviewer

## Review sequence

1. Validate the JSON schema.
2. Check the certification and domain against the registry and pack.
3. Verify each technical assertion against current public AWS sources.
4. Solve the question independently without reading the declared answer first when possible.
5. Compare the independent answer with the declared answer.
6. Test whether another option also satisfies all stated requirements.
7. Score the question using `rubrics/universal-question-quality.yaml`.
8. Return `approved`, `rewrite`, or `rejected`.

## Automatic rejection conditions

- incorrect AWS fact;
- ambiguous or multiple unintended best answers;
- copied or reconstructed confidential content;
- unsupported claim about lowest cost, highest performance, or least operational effort;
- wrong depth for the certification;
- missing option analysis or sources;
- obsolete service behavior presented as current.

## Rewrite conditions

- weak or obvious distractors;
- unnecessary wording;
- correct answer is conspicuously longer or more specific;
- scenario contains unused constraints;
- question can be solved by one superficial keyword.

Return scores, evidence, failure modes, and precise rewrite instructions. Do not silently fix and approve a question in the same review pass.
