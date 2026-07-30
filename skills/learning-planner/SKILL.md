---
name: learning-planner
description: Build a staged, progress-aware learning plan from a selected AWS certification pack, structured curriculum, and learner profile.
---

# Learning Planner

## Purpose

Turn an official exam blueprint and repository curriculum into a practical, interactive study sequence.

## Required process

1. Load the selected certification pack and its referenced curriculum.
2. Validate that certification ID and curriculum version match.
3. Load the learner profile and adaptive progress file, or initialize progress from the curriculum.
4. Map existing experience to curriculum objectives without marking untested objectives proficient.
5. Follow objective prerequisites and module order.
6. Allocate extra attention according to domain weight, objective importance, and demonstrated weakness.
7. Add hands-on activities where the certification expects implementation knowledge.
8. Select the smallest next activity that produces missing mastery evidence.
9. Define stage completion using the curriculum completion rules.

## Curriculum behavior

- Use curriculum objective IDs as stable progress keys.
- Do not invent a parallel topic list when a curriculum exists.
- A module may have an authored lesson path. Load it when relevant.
- If no lesson file exists, use `skills/lesson-author/SKILL.md` to generate an adaptive lesson blueprint from the module and objectives.
- Stage percentages derive from objective status, not lesson count or time spent.

## Adaptive sequencing

Prioritize in this order:

1. unmet prerequisite;
2. objective marked `needs_review`;
3. weak core objective in the current stage;
4. missing mastery evidence;
5. next module in curriculum order;
6. integrated or timed work only after broad coverage.

## Progress reporting

When enabled, every lesson must show overall progress, current stage, current module, completed objectives, current objective, remaining objectives, and weak areas.
