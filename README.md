# AWS Certification Learning Framework

An open-source, agent-compatible framework for personalized AWS certification learning, original exam-style question generation, answer review, and adaptive mock exams.

> [!IMPORTANT]
> This is an independent, unofficial learning project. It is not affiliated with, endorsed by, or sponsored by Amazon Web Services. AWS, Amazon Web Services, and related marks are trademarks of Amazon.com, Inc. or its affiliates.
>
> This repository does **not** contain actual certification exam questions, exam dumps, or reconstructed confidential exam content. All practice questions must be independently authored and grounded in public AWS documentation.

## What this repository is

The MVP is designed to run inside an AI conversation. An AI agent reads the reusable skills, a certification pack, and an optional learner profile, then teaches, generates original practice questions, reviews answers, and adjusts the learning plan.

```text
GitHub repository
  -> AI agent loads skills + certification pack
  -> conversational lesson or quiz
  -> answer review + weakness diagnosis
  -> next lesson or adaptive quiz
```

The framework separates reusable behavior from certification-specific knowledge:

```text
Universal skill + Certification pack + Learner profile = Personalized certification tutor
```

## MVP capabilities

- Select a suitable AWS certification based on a learner's role and background.
- Build a staged learning plan from an official exam blueprint.
- Teach interactively and explain acronyms on first use.
- Generate original questions at foundational, associate, professional, or specialty depth.
- Review technical accuracy, answer uniqueness, distractor quality, and source grounding.
- Assemble balanced quizzes and mock exams.
- Validate structured question files and certification packs in continuous integration.

## Included reference packs

| Certification | Level | Status in this repository |
|---|---|---|
| AWS Certified Cloud Practitioner (CLF-C02) | Foundational | Reference pack |
| AWS Certified AI Practitioner (AIF-C01) | Foundational | Reference pack |
| AWS Certified Solutions Architect - Associate (SAA-C03) | Associate | Reference pack |

The registry also lists the current certification families so contributors can add more packs without changing the core skills.

## Quick start with an AI agent

### Interactive tutor

```text
Read AGENTS.md, then load:
- skills/learning-planner/SKILL.md
- skills/tutor/SKILL.md
- certifications/associate/SAA-C03/certification.yaml
- examples/learner-profile.yaml

Teach me interactively in Chinese. Explain every acronym the first time it appears, show progress, and do not reveal quiz answers until I respond.
```

### Generate original practice questions

```text
Read AGENTS.md and skills/question-author/SKILL.md.
Load certifications/foundational/AIF-C01/certification.yaml.
Generate five original exam-level questions and return JSON that conforms to schemas/question.schema.json.
Use only public AWS sources. Do not copy, reconstruct, or closely paraphrase existing exam questions.
```

### Review questions

```text
Read skills/question-reviewer/SKILL.md and rubrics/universal-question-quality.yaml.
Review the JSON files under examples/questions/.
Reject any question with an ambiguous answer, weak distractors, unsupported facts, or incorrect certification depth.
```

## Local validation

Requirements: Python 3.11 or newer.

```bash
python -m pip install -e '.[dev]'
python -m validator.validate
pytest
```

Or:

```bash
make check
```

## Repository layout

```text
skills/           Reusable agent behavior
certifications/   Versioned certification packs and registry
schemas/          Machine-readable content contracts
rubrics/          Review and difficulty standards
examples/         Learner profile and original example questions
validator/        Deterministic content validation
checks/           Static policy and distribution checks
models/           Shared model-agnostic terminology
.github/           Continuous integration
```

## Design principles

1. **Official-source grounding**: technical facts must be verified against public AWS documentation.
2. **Original content only**: no dumps, reconstructed questions, or near-copy paraphrases.
3. **Depth, not keyword matching**: questions should test the reasoning depth of the selected certification.
4. **Plausible distractors**: incorrect options should reflect incomplete knowledge, not nonsense.
5. **Model independence**: skills are written as portable instructions rather than vendor-specific prompts.
6. **Structured output first**: questions are stored as JSON so they can be rendered in chat, a CLI, or a future web application.
7. **Human-review friendly**: every answer includes decisive constraints, option-by-option analysis, sources, and review metadata.

## Roadmap

- **v0.1**: conversational skill framework, three reference packs, schemas, examples, validator, and CI.
- **v0.2**: richer topic maps, lesson schemas, adaptive progress files, and more certification packs.
- **v0.3**: command-line workflow for generation, review, and mock-exam assembly.
- **v0.4**: official-document retrieval and source freshness checks.
- **v1.0**: optional MCP/API service and web practice interface.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [docs/source-policy.md](docs/source-policy.md), and [docs/adding-a-certification.md](docs/adding-a-certification.md) before submitting content.

## License

- Source code: [MIT License](LICENSE)
- Original educational content, rubrics, examples, and documentation: [CC BY 4.0](NOTICE.md)
