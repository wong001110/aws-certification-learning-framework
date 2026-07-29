---
name: question-author
description: Generate independently authored AWS certification practice questions at the correct certification depth.
---

# Question Author

## Required inputs

- certification pack;
- exam domain and task objective;
- level depth profile;
- desired response type;
- current public AWS sources;
- optional learner weaknesses.

## Authoring workflow

1. Choose one assessable objective from the certification pack.
2. Verify all technical facts using public AWS documentation.
3. Design an original scenario, not a paraphrase of an existing question.
4. Add only constraints needed to identify the best response.
5. Create the correct response before distractors.
6. Create distractors that represent distinct incomplete mental models.
7. Confirm the response count and answer uniqueness.
8. Write decisive constraints and option-by-option analysis.
9. Output JSON conforming to `schemas/question.schema.json`.
10. Send the result through the Question Reviewer before approval.

## Depth rules

Read `rubrics/depth-profiles.yaml`. Do not turn foundational certifications into architecture implementation exams. Do not reduce professional or specialty certifications to service-definition recall.

## Distractor rules

A distractor should be plausible within the content area and fail for a specific reason: it violates a hard requirement, solves only part of the problem, increases overhead, uses the wrong service boundary, or is unnecessarily complex or costly.

Avoid nonsense options, fake AWS services, and grammatical clues.

## Originality policy

Never use confidential exam content, recalled questions, reconstructed questions, or lightly rewritten official or third-party questions. Public sample material may inform abstract style and depth only.
