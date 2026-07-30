---
name: exam-assembler
description: Assemble balanced adaptive quizzes and mock-exam plans from reviewed questions and certification blueprints.
---

# Exam Assembler

## Inputs

- certification pack, curriculum, and official domain weights;
- approved current question pool;
- target count and mode;
- optional learner progress and adaptive policy.

## Rules

1. Use `schemas/quiz-plan.schema.json` as the planning contract.
2. For adaptive mode, use the adaptive-quiz skill and objective evidence.
3. For mock mode, allocate questions by official domain weights as closely as integer counts allow.
4. Reuse only approved, fresh, objective-aligned questions.
5. Turn gaps into explicit original-question authoring slots.
6. Respect supported response types.
7. Prevent duplicate scenarios and near-duplicate option sets.
8. Balance correct answer positions when the actual question set is rendered.
9. Hide explanations until submission in exam mode.
10. Separate official exam metadata from user-selected practice settings.

After submission, report practice performance, reasoning errors, objective and domain gaps, and a repair plan. Never claim that a practice score guarantees passing.
