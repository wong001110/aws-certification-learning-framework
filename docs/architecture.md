# Architecture

## MVP boundary

The MVP is a repository-driven conversational framework. It does not require a web application, database, retrieval service, or model fine-tuning.

```text
Learner message
    -> Universal skill + learner profile
    -> Certification pack
    -> AI conversation output
    -> Structured question, review, or progress state
```

## Separation of concerns

- Universal skills define planning, teaching, question authoring, review, exam assembly, and progress coaching.
- Certification packs define official metadata, domains, weights, response types, target depth, and source URLs.
- Schemas make generated content portable and testable.
- The deterministic validator checks structure, registry references, weights, answer counts, source policy, and review thresholds.

The validator cannot prove complete technical correctness. An independent reviewer and current AWS documentation are still required.

## Future extension points

Official-document retrieval, source freshness checks, similarity detection, learner progress persistence, a mock-exam CLI, an MCP or HTTP API, and a web interface.
