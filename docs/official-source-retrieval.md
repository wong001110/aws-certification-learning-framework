# Official AWS source retrieval

## Design

The repository commits a small catalog of official AWS URLs and verification metadata. It does not commit copies of AWS documentation.

```text
sources/catalog.yaml
  -> freshness report
  -> optional local synchronization
  -> ignored JSON chunk cache
  -> lexical retrieval
  -> lesson or question authoring with source IDs
```

This provides a deterministic, model-independent retrieval layer. It can later be replaced by a vector database or a managed knowledge base without changing certification packs, objective IDs, or structured content.

## Freshness

```bash
aws-cert source-freshness --fail-on-stale
```

Each source records a manual verification date and refresh interval. The check is intentionally separate from HTTP synchronization: a page still existing does not guarantee that existing lessons and questions remain technically correct.

## Synchronize selected pages

```bash
aws-cert source-sync --source-id saa-c03-exam-guide
aws-cert source-sync --certification SAA-C03
```

The synchronizer:

- accepts only cataloged official AWS hosts;
- limits response size;
- removes navigation, scripts, and styling;
- stores chunked text and a SHA-256 digest locally;
- writes only to `.cache/aws-cert-docs/` by default.

Network access is optional. Contributors can validate repository structure without downloading documents.

## Search

```bash
aws-cert source-search \
  "managed relational database automatic failover" \
  --certification SAA-C03 \
  --limit 5
```

Search uses a local BM25-style lexical ranker with title, heading, and tag boosts. Results include source ID, URL, chunk heading, verification date, fetch date, score, and excerpt.

## Content authoring

Approved questions and lessons must include both:

- `source_ids`, which resolve through the catalog;
- `sources`, which preserve human-readable titles, URLs, and access dates.

The validator rejects mismatched IDs and URLs. Retrieved wording should be used for verification and then rewritten in original language.
