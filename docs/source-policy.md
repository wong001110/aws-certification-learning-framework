# Source and content policy

## Allowed sources

Use cataloged public pages from AWS Certification, AWS service documentation, AWS Architecture Center, AWS Well-Architected guidance, AWS Prescriptive Guidance, AWS Security documentation, and official AWS product pages.

Every approved lesson and question must include:

- catalog `source_ids`;
- matching source titles and URLs;
- access dates;
- original explanatory wording.

## Source catalog

Add official sources to `sources/catalog.yaml` before referencing them in approved content. Record verification date, refresh interval, source type, tags, and relevant certification or objective IDs.

Do not add third-party blogs merely because they are useful explanations. They may be recommended separately, but they are not authoritative inputs to approved framework content.

## Freshness

`verified_at` means a contributor checked the page and its relevance, not merely that the URL returned HTTP 200. Critical exam guides and scope pages use shorter refresh intervals than stable concept pages.

Stale content must be reverified before approval. Content affected by an exam or service change should be marked `needs_revalidation`.

## Local retrieval

The optional retriever may cache official documentation under `.cache/aws-cert-docs/`. The cache is not source-controlled and must not be treated as a permanent copy of AWS documentation.

Use retrieved excerpts only to verify facts. Do not publish substantial copied text.

## Prohibited material

Do not add or use confidential exam content, recalled questions, live-exam screenshots or transcripts, reconstructed questions, lightly paraphrased commercial questions, or claims that generated content is official or guaranteed to appear.

Public AWS sample questions may inform abstract response types, scenario density, distractor plausibility, and reasoning depth. Do not copy their scenarios, wording, option combinations, or rationales.
