---
name: lesson-author
description: Create structured, adaptive AWS certification lesson blueprints from curriculum objectives and official public sources.
---

# Lesson Author

## Purpose

Create a reusable lesson blueprint that conforms to `schemas/lesson.schema.json`. The lesson is executed conversationally by the tutor and is not a fixed lecture script.

## Required inputs

- selected certification pack;
- referenced curriculum;
- one module and one to three related objectives;
- learner profile when available;
- current public AWS documentation.

## Authoring process

1. Confirm objective IDs, domain alignment, prerequisites, and curriculum version.
2. Define a bounded lesson outcome and estimated duration.
3. Build a delivery sequence containing orientation, explanation, comparison or worked example, a knowledge check, and summary.
4. Add hands-on work only when implementation evidence is appropriate for the certification.
5. Include at least one knowledge check whose expected evidence maps directly to the objective.
6. Ground technical claims in official AWS sources and record access dates.
7. Keep the lesson adaptable: instructions describe what the tutor should accomplish, not exact prose that must be repeated.
8. Run independent review before marking the lesson approved.

## Depth alignment

- Foundational lessons emphasize concepts, use cases, business value, shared responsibility, and recognition.
- Associate lessons include practical implementation choices, service boundaries, troubleshooting, and tradeoffs.
- Professional lessons combine organizational, migration, governance, and multi-system constraints.
- Specialty lessons require deeper domain failure analysis and implementation detail.

## Quality rules

- Teach one coherent cluster of objectives.
- Include nearest alternatives and conditions that change the correct decision.
- Avoid long encyclopedic service lists.
- Do not use exam dumps or closely paraphrase public sample questions.
- Do not invent quotas, pricing, or current feature behavior.
- Use stable objective IDs and official source URLs.
