# Contributing

Contributions are welcome for skills, certification packs, curricula, lesson blueprints, validators, documentation, progress examples, and independently authored practice questions.

## Required rules

1. Use public AWS sources for technical facts.
2. Do not submit exam dumps, recalled questions, reconstructed confidential content, or close paraphrases of existing questions.
3. Record source URLs and verification dates for technical lessons and questions.
4. Keep certification-specific facts inside certification packs and curricula rather than hard-coding them into universal skills.
5. Preserve stable curriculum objective IDs once published, or document a migration.
6. Run `make check` before submitting a pull request.

## Adding a question

A question must:

- conform to `schemas/question.schema.json`;
- identify its certification, domain, difficulty, tested skills, and source URLs;
- contain a complete option-by-option explanation;
- have an unambiguous answer;
- meet the depth profile for the selected certification level;
- use plausible distractors that fail for distinct reasons;
- be independently authored.

## Adding a lesson

A lesson must:

- conform to `schemas/lesson.schema.json`;
- reference objectives from the matching curriculum;
- teach a bounded, coherent objective cluster;
- include observable mastery evidence;
- compare nearest alternatives and important limitations;
- cite current public AWS sources;
- be independently reviewed before approval.

## Adding a certification pack

Follow `docs/adding-a-certification.md`. A pack must include an official exam-guide URL, content domains with weights, target depth, supported question types, a versioned curriculum, and a last-verified date.

## Pull request checklist

- [ ] Content is original and does not reproduce confidential exam material.
- [ ] Technical claims are grounded in public AWS documentation.
- [ ] Domain weights total 100.
- [ ] Curriculum stages, modules, objectives, and lesson references are valid.
- [ ] Lesson and progress files conform to their schemas.
- [ ] JSON and YAML validation passes.
- [ ] Tests pass.
- [ ] New acronyms are expanded on first use in learner-facing text.
