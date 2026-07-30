# Structured lesson authoring guide

Version 0.2 adds a curriculum-driven lesson system. The curriculum defines stable objectives and sequencing; lesson files define reusable teaching blueprints.

## Curriculum versus lesson

A curriculum answers:

- What must the learner master?
- In which order?
- Which exam domains does each objective support?
- What evidence is required before progression?

A lesson answers:

- How should one coherent group of objectives be taught?
- Which alternatives and limitations must be compared?
- What activity will demonstrate understanding?
- Which official sources support the lesson?

Lesson files are not fixed scripts. The tutor adapts examples, language, and pacing to the learner while preserving the objective IDs and lesson boundary.

## File placement

Place a curriculum at:

```text
certifications/<level>/<exam-code>/curriculum.yaml
```

Place authored lessons under:

```text
certifications/<level>/<exam-code>/lessons/
```

Reference lesson paths from the matching curriculum module.

## Minimum lesson sequence

An approved lesson should normally contain:

1. orientation or prior-knowledge check;
2. explanation;
3. comparison or worked example;
4. knowledge check;
5. summary.

Associate, Professional, and Specialty lessons may add hands-on work when implementation evidence is expected.

## Mastery evidence

Knowledge checks must describe observable evidence. Avoid evidence such as "understands the service." Prefer:

- distinguishes two service boundaries;
- identifies the decisive constraint;
- applies the concept to a new scenario;
- diagnoses a failure cause;
- completes a hands-on task.

## Source policy

Use current public AWS sources. Record access dates. Public exam materials may inform abstract depth and response style but must not be copied or closely paraphrased.

## Validation

Run:

```bash
python -m validator.validate
python -m pytest
python -m ruff check validator tests
```
