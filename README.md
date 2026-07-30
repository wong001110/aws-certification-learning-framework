# AWS Certification Learning Framework

An open-source, agent-compatible framework for personalized AWS certification learning, structured lessons, adaptive quizzes, original exam-style question generation, official-source retrieval, answer review, and mock-exam planning.

> [!IMPORTANT]
> This is an independent, unofficial learning project. It is not affiliated with, endorsed by, or sponsored by Amazon Web Services. AWS, Amazon Web Services, and related marks are trademarks of Amazon.com, Inc. or its affiliates.
>
> This repository does **not** contain actual certification exam questions, exam dumps, or reconstructed confidential exam content. All practice questions and lessons must be independently authored and grounded in public AWS documentation.

## Current version: v0.4

The default learning surface is still an AI conversation. Version 0.4 adds the v0.3 command-line workflow, adaptive quiz planning, evidence-based progress updates, a versioned official AWS source catalog, source freshness reporting, and an optional local Retrieval-Augmented Generation (RAG) retrieval cache.

```text
GitHub repository
  -> AI agent loads skills + certification pack + curriculum
  -> progress engine recommends the next objective
  -> lesson, focused quiz, or mock-exam plan
  -> official AWS source retrieval and verification
  -> evidence-based progress update
```

## v0.4 capabilities

- Select a suitable AWS certification based on role and background.
- Teach from versioned curricula and reusable lesson blueprints.
- Persist progress by stable learning objective.
- Prioritize weak or overdue objectives using accuracy, confidence, evidence, prerequisites, recency, and exam-domain weight.
- Generate adaptive, focused, and weighted mock-exam plans.
- Record attempts and update spaced-review dates conservatively.
- Generate and review original questions at the selected certification depth.
- Maintain a catalog of official AWS sources with verification dates and refresh intervals.
- Optionally cache and search selected AWS documentation locally without committing copied documentation to Git.
- Validate packs, curricula, lessons, progress, questions, source metadata, attempts, and quiz plans in continuous integration.

## Included reference packs

| Certification | Level | Curriculum | Sample lesson |
|---|---|---:|---:|
| AWS Certified Cloud Practitioner (CLF-C02) | Foundational | Yes | Yes |
| AWS Certified AI Practitioner (AIF-C01) | Foundational | Yes | Yes |
| AWS Certified Solutions Architect - Associate (SAA-C03) | Associate | Yes | Yes |
| AWS Certified Developer - Associate (DVA-C02) | Associate | Yes | Yes |
| AWS Certified Data Engineer - Associate (DEA-C01) | Associate | Yes | Yes |

## Installation

```bash
git clone https://github.com/wong001110/aws-certification-learning-framework.git
cd aws-certification-learning-framework
python -m venv .venv
```

Activate the environment, then install:

```bash
python -m pip install --no-build-isolation -e '.[dev]'
```

This installs the `aws-cert` command. Learners using an AI agent that can read repository files may continue using the project without invoking the CLI directly.

## Conversational use

```text
Read AGENTS.md, then load:
- skills/learning-planner/SKILL.md
- skills/tutor/SKILL.md
- skills/adaptive-quiz/SKILL.md
- skills/progress-coach/SKILL.md
- skills/source-retriever/SKILL.md
- certifications/associate/SAA-C03/certification.yaml
- certifications/associate/SAA-C03/curriculum.yaml
- examples/learner-profile.yaml
- examples/progress/saa-c03-example.yaml

Continue the course in Traditional Chinese.
Explain every acronym on first use.
Use official source IDs and verify current AWS claims.
Teach one bounded segment at a time.
Do not reveal quiz answers before I respond.
Update progress only after meaningful evidence.
```

## CLI workflow

Create a clean progress file:

```bash
aws-cert init-progress --certification SAA-C03 --output progress.yaml
```

Recommend the next activities:

```bash
aws-cert recommend \
  --certification SAA-C03 \
  --progress progress.yaml
```

Create an adaptive quiz plan:

```bash
aws-cert quiz-plan \
  --certification SAA-C03 \
  --mode adaptive \
  --progress progress.yaml \
  --count 10 \
  --output quiz-plan.yaml
```

Create a weighted mock-exam plan:

```bash
aws-cert quiz-plan \
  --certification SAA-C03 \
  --mode mock \
  --count 65 \
  --time-limit 130 \
  --output mock-plan.yaml
```

Apply an attempt to progress:

```bash
aws-cert record-attempt \
  --certification SAA-C03 \
  --progress progress.yaml \
  --attempt attempt.yaml
```

See [docs/adaptive-quizzes.md](docs/adaptive-quizzes.md).

## Official-source retrieval

Check source freshness:

```bash
aws-cert source-freshness --fail-on-stale
```

Synchronize only the documentation needed for a task:

```bash
aws-cert source-sync --source-id rds-multi-az
```

Search the ignored local cache:

```bash
aws-cert source-search \
  "automatic database failover read replica" \
  --certification SAA-C03
```

The repository commits only `sources/catalog.yaml`. Retrieved text is stored under `.cache/aws-cert-docs/`, which is ignored by Git. Network access is optional for structural validation. See [docs/official-source-retrieval.md](docs/official-source-retrieval.md).

## Validation

```bash
python -m validator.validate
python -m pytest
python -m ruff check validator tests
python -m validator source-freshness --fail-on-stale
```

Or:

```bash
make check
```

## Repository layout

```text
skills/           Portable agent behavior
certifications/   Certification packs, curricula, and lessons
policies/         Adaptive learning policy
sources/          Official AWS source metadata catalog
schemas/          Machine-readable content contracts
examples/         Questions, progress, attempts, and quiz plans
validator/        CLI, adaptive engine, retrieval, and validation
templates/        Starting structured files
docs/             Architecture and contributor guidance
tests/            Regression tests
.github/           Continuous integration and freshness checks
```

## Design principles

1. **Official-source grounding**: current technical claims resolve to cataloged public AWS sources.
2. **Original content only**: no dumps, reconstructed questions, or near-copy paraphrases.
3. **Curriculum as source of truth**: stable objective IDs control sequencing and progress.
4. **Evidence-based mastery**: one correct guess is not proficiency.
5. **Adaptive but explainable**: recommendations expose their scoring reasons and prerequisite blockers.
6. **Depth, not keyword matching**: questions test the reasoning depth of the selected certification.
7. **Local-first retrieval**: downloaded documentation is optional, inspectable, and uncommitted.
8. **Model independence**: skills and structured data can be used by different AI agents.
9. **Human-review friendly**: all approved content preserves objective IDs, source IDs, explanations, and review metadata.

## Roadmap

- **v0.1**: conversational skills, three packs, question schema, validator, and CI.
- **v0.2**: structured curricula, lessons, progress files, and five packs.
- **v0.3**: CLI, adaptive recommendations, attempt recording, and quiz planning. Included in v0.4.
- **v0.4**: official-source catalog, freshness checks, local retrieval cache, and source-aware validation.
- **v0.5**: optional embeddings or hybrid retrieval adapters and richer question-pool analytics.
- **v1.0**: optional MCP/API service and web practice interface.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [docs/source-policy.md](docs/source-policy.md), [docs/adding-a-certification.md](docs/adding-a-certification.md), [docs/lesson-authoring.md](docs/lesson-authoring.md), and [docs/official-source-retrieval.md](docs/official-source-retrieval.md).

## License

- Source code: [MIT License](LICENSE)
- Original educational content, rubrics, examples, and documentation: [CC BY 4.0](NOTICE.md)
