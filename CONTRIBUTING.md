# Contributing

Contributions are welcome for skills, certification packs, curricula, lessons, adaptive policies, source metadata, validators, documentation, progress examples, and independently authored questions.

## Required rules

1. Use current public AWS sources for technical facts.
2. Do not submit exam dumps, recalled questions, reconstructed confidential content, or close paraphrases.
3. Add sources to `sources/catalog.yaml` and record `source_ids`, URLs, and verification dates.
4. Keep certification-specific facts in packs and curricula rather than universal skills.
5. Preserve published objective IDs or document a migration.
6. Do not commit `.cache/aws-cert-docs/` or copied AWS documentation.
7. Run `make check` before a pull request.

## Adding a source

A source entry must use an official AWS host, have a unique stable ID, describe relevant certifications or objectives, and define a refresh interval. Verify the page's technical relevance, not only its availability.

## Adding a question

A question must conform to `schemas/question.schema.json`, identify certification/domain/objectives/sources, contain complete analysis, have an unambiguous answer, match certification depth, use plausible distinct distractors, and be independently authored.

## Adding a lesson

A lesson must conform to `schemas/lesson.schema.json`, reference curriculum objectives and catalog sources, teach a bounded cluster, include observable evidence, compare nearest alternatives, and be independently reviewed.

## Adding an adaptive example

Quiz plans and attempts must conform to their schemas. Do not manually mark a learner proficient without the evidence required by the curriculum.

## Pull request checklist

- [ ] Content is original and contains no confidential exam material.
- [ ] Technical claims map to current official source IDs.
- [ ] Source freshness is valid.
- [ ] Domain weights total 100.
- [ ] Curriculum and lesson references are valid.
- [ ] Questions, progress, attempts, and quiz plans conform to schemas.
- [ ] Tests and lint pass.
- [ ] Learner-facing acronyms are expanded on first use.
