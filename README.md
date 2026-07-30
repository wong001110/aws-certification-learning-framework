# AWS Certification Learning Framework

An open-source, agent-compatible framework for personalized AWS certification learning, structured lessons, original exam-style question generation, answer review, and adaptive mock exams.

> [!IMPORTANT]
> This is an independent, unofficial learning project. It is not affiliated with, endorsed by, or sponsored by Amazon Web Services. AWS, Amazon Web Services, and related marks are trademarks of Amazon.com, Inc. or its affiliates.
>
> This repository does **not** contain actual certification exam questions, exam dumps, or reconstructed confidential exam content. All practice questions and lessons must be independently authored and grounded in public AWS documentation.

## Current version: v0.2

The framework still runs primarily inside an AI conversation. Version 0.2 adds portable curricula, lesson blueprints, and progress files so different agents can continue the same learning path without relying only on chat memory.

```text
GitHub repository
  -> AI agent loads skill + certification pack
  -> agent loads curriculum + learner progress
  -> bounded conversational lesson or quiz
  -> evidence-based progress update
  -> next adaptive activity
```

The framework separates reusable behavior from certification-specific knowledge:

```text
Universal skill + Certification pack + Curriculum + Learner progress
= Personalized certification tutor
```

## v0.2 capabilities

- Select a suitable AWS certification based on a learner's role and background.
- Build a staged plan from a versioned curriculum and official exam blueprint.
- Teach bounded interactive lessons and explain acronyms on first use.
- Persist progress by stable learning objective rather than elapsed time.
- Generate lesson blueprints when a curriculum module has no authored lesson.
- Generate original questions at foundational, associate, professional, or specialty depth.
- Review technical accuracy, answer uniqueness, distractor quality, and source grounding.
- Assemble balanced quizzes and mock exams.
- Validate certification packs, curricula, lessons, progress files, and questions in continuous integration.

## Included reference packs

| Certification | Level | Curriculum | Sample lesson |
|---|---|---:|---:|
| AWS Certified Cloud Practitioner (CLF-C02) | Foundational | Yes | Yes |
| AWS Certified AI Practitioner (AIF-C01) | Foundational | Yes | Yes |
| AWS Certified Solutions Architect - Associate (SAA-C03) | Associate | Yes | Yes |
| AWS Certified Developer - Associate (DVA-C02) | Associate | Yes | Yes |
| AWS Certified Data Engineer - Associate (DEA-C01) | Associate | Yes | Yes |

The registry lists additional active certification families so contributors can add packs without changing the core skills.

## Quick start

```bash
git clone https://github.com/wong001110/aws-certification-learning-framework.git
cd aws-certification-learning-framework
```

Open the directory with an AI agent that can read local files.

### Continue a structured SAA-C03 course

```text
Read AGENTS.md, then load:
- skills/learning-planner/SKILL.md
- skills/tutor/SKILL.md
- skills/progress-coach/SKILL.md
- certifications/associate/SAA-C03/certification.yaml
- certifications/associate/SAA-C03/curriculum.yaml
- examples/learner-profile.yaml
- examples/progress/saa-c03-example.yaml

Continue the course in Traditional Chinese.
Use the curriculum objective IDs as progress keys.
Explain every acronym on first use.
Teach one bounded lesson segment at a time.
Do not reveal quiz answers until I respond.
Update the progress file after meaningful evidence.
```

### Start with a clean progress file

Copy the templates:

```bash
cp examples/learner-profile.yaml learner-profile.yaml
cp templates/progress.yaml progress.yaml
```

Then change the certification ID, curriculum version, language, and experience levels.

### Generate a structured lesson

```text
Read AGENTS.md and skills/lesson-author/SKILL.md.
Load the DVA-C02 certification pack and curriculum.
Create a lesson blueprint for one current-stage module.
Return YAML conforming to schemas/lesson.schema.json.
Use current official AWS sources.
```

### Generate original practice questions

```text
Read AGENTS.md and skills/question-author/SKILL.md.
Load certifications/foundational/AIF-C01/certification.yaml.
Generate five original exam-level questions as JSON conforming to schemas/question.schema.json.
Use only public AWS sources. Do not copy, reconstruct, or closely paraphrase existing exam questions.
```

### Review repository content

```text
Read skills/question-reviewer/SKILL.md and rubrics/universal-question-quality.yaml.
Review the structured questions and lessons.
Reject ambiguous answers, weak distractors, unsupported technical claims, or incorrect certification depth.
```

## Local validation

Requirements: Python 3.11 or newer.

```bash
python -m pip install --no-build-isolation -e '.[dev]'
python -m validator.validate
python -m pytest
python -m ruff check validator tests
```

Or:

```bash
make check
```

## Repository layout

```text
skills/           Reusable agent behavior, including lesson authoring
certifications/   Versioned certification packs, curricula, lessons, and registry
schemas/          Machine-readable question, curriculum, lesson, and progress contracts
rubrics/          Review and difficulty standards
examples/         Learner profile, progress state, and original example questions
templates/        Starting files for lessons and progress
validator/        Deterministic content and cross-reference validation
tests/            Validator regression tests
docs/             Architecture, source policy, lesson, and contribution guides
.github/           Continuous integration
```

## Design principles

1. **Official-source grounding**: technical facts must be verified against public AWS documentation.
2. **Original content only**: no dumps, reconstructed questions, or near-copy paraphrases.
3. **Curriculum as source of truth**: objective IDs control sequencing and progress.
4. **Evidence-based mastery**: one correct guess does not equal proficiency.
5. **Depth, not keyword matching**: questions and lessons test the selected certification's reasoning depth.
6. **Plausible alternatives**: learners must understand service boundaries and tradeoffs.
7. **Model independence**: skills are portable instructions rather than vendor-specific prompts.
8. **Structured output first**: content can be rendered in chat, a CLI, or a future web application.
9. **Human-review friendly**: lessons and questions include sources, evidence, and review metadata.

## Roadmap

- **v0.1**: conversational skill framework, three reference packs, question schemas, validator, and CI.
- **v0.2**: structured curricula and lessons, adaptive progress files, five reference packs.
- **v0.3**: command-line workflow for course initialization, validation, progress updates, question review, and mock-exam assembly.
- **v0.4**: official-document retrieval and source freshness checks.
- **v1.0**: optional MCP/API service and web practice interface.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [docs/source-policy.md](docs/source-policy.md), [docs/adding-a-certification.md](docs/adding-a-certification.md), and [docs/lesson-authoring.md](docs/lesson-authoring.md) before submitting content.

## License

- Source code: [MIT License](LICENSE)
- Original educational content, rubrics, examples, and documentation: [CC BY 4.0](NOTICE.md)
