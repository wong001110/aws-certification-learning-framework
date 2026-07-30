# Adaptive progress model

Progress is stored by curriculum objective so it remains stable across AI models and conversations.

## Status values

- `not_started`: no meaningful evidence;
- `introduced`: the concept has been explained;
- `practicing`: the learner can recall or apply it with support;
- `proficient`: the learner has produced the curriculum's required evidence;
- `needs_review`: recent evidence shows confusion or loss of transfer.

## Confidence and evidence

Confidence is a practical estimate from 0 to 1, not an exam probability. Evidence count records relevant demonstrations, not every message.

A single correct multiple-choice answer should not create proficiency. Use explanation quality, comparison, transfer to new scenarios, troubleshooting, and hands-on work.

## Overall progress

Recommended calculation:

```text
not_started = 0
introduced = 0.25
practicing = 0.60
needs_review = 0.40
proficient = 1.00
```

Compute the mean across curriculum objectives. Objective importance and domain weight may be shown separately, but progress must not be based only on elapsed time.

## Persistence

The MVP keeps progress in a YAML file. An agent with file-write permission can update it after each completed activity. Other agents can read the same file and continue the course without relying on hidden conversation memory.
