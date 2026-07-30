# Architecture

## MVP boundary

The MVP is a repository-driven conversational framework. It does not require a web application, database, retrieval service, or model fine-tuning.

```text
Learner message
    -> Universal skills + learner profile
    -> Certification pack
    -> Versioned curriculum
    -> Lesson blueprint + adaptive progress
    -> AI conversation output
    -> Question review and progress evidence
```

## Separation of concerns

- Universal skills define selection, planning, lesson authoring, teaching, question authoring, review, exam assembly, and progress coaching.
- Certification packs define official metadata, domains, weights, response types, target depth, source URLs, and curriculum location.
- Curricula define stable stages, modules, objectives, prerequisites, and mastery evidence.
- Lesson files define reusable teaching blueprints that agents adapt to the learner.
- Progress files persist objective evidence across conversations and AI models.
- Schemas make content portable and testable.
- The deterministic validator checks structure, cross-references, weights, answer counts, source policy, lesson references, and progress integrity.

The validator cannot prove complete technical correctness. Independent review and current AWS documentation are still required.

## Runtime flow

1. Select a certification pack.
2. Load its curriculum.
3. Read or initialize learner progress.
4. Choose the smallest unmet objective or weak area.
5. Load an authored lesson or generate a schema-valid blueprint.
6. Teach one bounded segment and collect evidence.
7. Update progress conservatively.
8. Move to integrated scenarios, timed quizzes, and mock exams only when prerequisites are satisfied.

## Future extension points

Command-line course initialization, deterministic progress updates, official-document retrieval, source freshness checks, similarity detection, an MCP or HTTP API, and a web interface.
