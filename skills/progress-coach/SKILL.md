---
name: progress-coach
description: Maintain schema-valid objective progress, diagnose weak areas, and select the next AWS certification learning activity.
---

# Progress Coach

## Progress model

Use `schemas/progress.schema.json`. Track mastery by curriculum objective, not by time spent. Each objective may be `not_started`, `introduced`, `practicing`, `proficient`, or `needs_review`.

## Evidence

Use explanation quality, comparison accuracy, scenario transfer, repeated question performance, troubleshooting, and hands-on completion. One correct guess is not mastery.

For each objective maintain:

- confidence from 0 to 1;
- evidence count;
- attempts and correct responses;
- last update time;
- weak-area status.

## Update rules

- Add evidence only when the activity directly tests the objective.
- Do not reduce attempts or evidence counts.
- Mark `needs_review` after repeated errors, contradiction of a core concept, or loss of transfer ability.
- Mark `proficient` only when the curriculum's mastery evidence and current stage completion requirements are met.
- Remove an objective from `weak_objectives` only after new successful evidence.

## Next-action policy

Prefer the smallest activity that addresses the current bottleneck:

1. missing prerequisite explanation;
2. comparison exercise for confused alternatives;
3. focused questions for weak constraints;
4. hands-on work where implementation evidence is required;
5. integrated scenarios for transfer;
6. timed quizzes after broad coverage;
7. mock exams only after prerequisite stages are complete.

Store the recommendation and reason in `next_recommendation`.

## Reporting

Show overall progress, current stage, completed objectives, remaining objectives, weak areas, and the next recommendation when requested by the learner profile.
