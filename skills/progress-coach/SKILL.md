---
name: progress-coach
description: Maintain schema-valid objective evidence, spaced review, weak-area diagnosis, and next AWS certification activities.
---

# Progress Coach

Use `schemas/progress.schema.json`. Track mastery by curriculum objective, not time spent.

## Evidence

Use explanation quality, comparison accuracy, scenario transfer, repeated question performance, troubleshooting, and hands-on completion. One correct guess is not mastery.

Maintain confidence, evidence count, attempts, correct responses, streaks, last-seen time, next-review time, and weak status. Record each new observation through `schemas/attempt.schema.json` when possible.

## Update rules

- Add evidence only when the activity directly tests the objective.
- Never reduce attempts or evidence counts.
- Mark `needs_review` after meaningful contradictory evidence or loss of transfer ability.
- Mark `proficient` only after curriculum evidence and sufficient repeated performance.
- Remove weak status only after new successful evidence.
- Do not use the adaptive priority score as a mastery score.

## Next activity

Load `skills/adaptive-quiz/SKILL.md` and `policies/adaptive-default.yaml`. Prefer prerequisite repair, comparison for confused alternatives, focused questions, hands-on evidence, integrated scenarios, timed quizzes, and finally mock exams.

Store the recommendation and reason in `next_recommendation` and expose a concise progress summary.
