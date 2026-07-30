# Architecture

## Runtime boundary

Version 0.4 remains local-first and conversation-first. A web application, external database, vector database, and model fine-tuning are not required.

```text
Learner message or CLI command
  -> universal skill + certification pack
  -> versioned curriculum + progress
  -> adaptive policy
  -> official source catalog
  -> optional local retrieval cache
  -> lesson, quiz plan, review, or progress update
```

## Components

- **Skills** define portable agent behavior.
- **Certification packs** define exam metadata, domains, depth, and curriculum location.
- **Curricula** define stages, modules, objectives, prerequisites, and mastery evidence.
- **Lessons** define reusable teaching blueprints.
- **Progress** persists objective evidence across conversations and models.
- **Adaptive policy** produces explainable objective priorities and quiz slots.
- **Source catalog** maps stable IDs to official AWS URLs and freshness metadata.
- **Local retrieval** downloads selected pages to an ignored chunk cache and ranks chunks lexically.
- **Schemas and validator** enforce structure and cross-references.
- **CLI** exposes deterministic workflows without replacing conversational teaching.

## Retrieval architecture

The committed catalog is authoritative for permitted sources. The cache is disposable and can be rebuilt.

```text
sources/catalog.yaml
  -> source-freshness
  -> source-sync
  -> .cache/aws-cert-docs/*.json
  -> source-search
  -> agent verifies claims and stores source_ids
```

The initial retriever is deliberately simple and inspectable. A future embeddings or hybrid adapter can implement the same source-ID contract.

## Quality boundary

The validator can prove structural consistency, source mapping, answer metadata, distributions, and progress arithmetic. It cannot prove that every AWS claim is technically correct. Current official documentation plus independent review remain mandatory.
