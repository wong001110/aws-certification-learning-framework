---
name: adaptive-quiz
description: Select learning objectives and assemble original AWS certification quizzes from persistent evidence, prerequisites, domain weights, and official-source grounding.
---

# Adaptive Quiz

## Load order

1. Load the certification pack and curriculum.
2. Load the learner progress file.
3. Load `policies/adaptive-default.yaml`.
4. Load `skills/question-author/SKILL.md` and `skills/question-reviewer/SKILL.md` when a plan requires new questions.
5. Load `skills/source-retriever/SKILL.md` before making current AWS claims.

## Selection rules

Prioritize objectives by observable need, not by topic order alone:

- prerequisite blockers before dependent objectives;
- objectives marked `needs_review` or listed in `weak_objectives`;
- low accuracy or low confidence;
- insufficient mastery evidence;
- overdue spaced review;
- official exam-domain weight;
- core objectives before supporting objectives when other signals are equal.

Do not overfit to one incorrect answer. Use several observations when possible.

## Quiz modes

- **adaptive**: target the highest-priority current or weak objectives;
- **focused**: target explicitly requested objectives or domains;
- **mock**: follow official domain weights and suppress explanations until submission.

A quiz plan must conform to `schemas/quiz-plan.schema.json`. Use an approved existing question only when its certification, domain, objective, difficulty, and question type match the slot. Otherwise create an authoring request; do not silently substitute an unrelated question.

## After an answer

Record an attempt conforming to `schemas/attempt.schema.json`, then update:

- attempts and correct answers;
- evidence count and confidence;
- correct or incorrect streak;
- weak-objective status;
- next review time;
- recent quiz summary;
- next recommended activity.

One correct answer does not prove mastery. Preserve the curriculum's mastery-evidence requirements.
