---
name: source-retriever
description: Ground AWS certification lessons and original questions in a versioned catalog of current public AWS documentation with freshness and retrieval checks.
---

# Official Source Retriever

## Purpose

Use `sources/catalog.yaml` as the source registry for current AWS facts. The repository stores source metadata only. Full retrieved documents belong in the ignored local cache under `.cache/aws-cert-docs/`.

## Required workflow

1. Resolve the selected certification and objective IDs.
2. Select relevant catalog entries by certification, objective, and tags.
3. Check `verified_at`, `refresh_days`, and freshness status.
4. When local retrieval is available, synchronize only the necessary official AWS pages.
5. Search cached chunks using the learner's actual question or the technical claim being verified.
6. Base explanations and authoring decisions on retrieved evidence, not on model memory alone.
7. Preserve `source_ids`, official URLs, and access dates in structured content.

## Freshness behavior

- A stale critical source must be reverified before approving new content.
- A stale noncritical source may be used only with an explicit stale warning and independent verification.
- A future verification date is invalid.
- Never treat a successful HTTP response as proof that a technical claim is correct; inspect the retrieved section.

## Retrieval boundaries

- Fetch only official `aws.amazon.com` and `docs.aws.amazon.com` URLs listed in the catalog.
- Do not commit cached AWS documentation to Git.
- Do not reproduce substantial AWS documentation text in lessons or questions.
- Use short excerpts only for verification, then write original explanations.
- Do not ingest exam dumps, recalled questions, or commercial question banks.

## CLI examples

```bash
aws-cert source-freshness --certification SAA-C03
aws-cert source-sync --source-id rds-multi-az
aws-cert source-search "automatic failover read replica" --certification SAA-C03
```
