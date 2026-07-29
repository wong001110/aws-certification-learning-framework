# Contributing

Contributions are welcome for skills, certification packs, validators, documentation, and independently authored practice questions.

## Required rules

1. Use public AWS sources for technical facts.
2. Do not submit exam dumps, recalled questions, reconstructed confidential content, or close paraphrases of existing questions.
3. Record the source URL and verification date for every technical question.
4. Keep certification-specific facts inside a certification pack rather than hard-coding them into universal skills.
5. Run `make check` before submitting a pull request.

## Adding a question

A question must:

- conform to `schemas/question.schema.json`;
- identify its certification, domain, difficulty, tested skills, and source URLs;
- contain a complete option-by-option explanation;
- have an unambiguous answer;
- meet the depth profile for the selected certification level;
- use plausible distractors that fail for distinct reasons;
- be independently authored.

## Adding a certification pack

Follow `docs/adding-a-certification.md`. A pack must include an official exam-guide URL, content domains with weights, target depth, supported question types, and a last-verified date.

## Pull request checklist

- [ ] Content is original and does not reproduce confidential exam material.
- [ ] Technical claims are grounded in public AWS documentation.
- [ ] Domain weights total 100.
- [ ] JSON and YAML validation passes.
- [ ] Tests pass.
- [ ] New acronyms are expanded on first use in learner-facing text.
