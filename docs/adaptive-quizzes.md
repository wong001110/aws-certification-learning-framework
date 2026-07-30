# Adaptive quizzes and progress updates

Version 0.4 includes the command-line workflow planned for v0.3.

## Recommendation model

The default policy combines objective status, accuracy, confidence, mastery evidence, official domain weight, and review recency. Weak objectives receive an explicit bonus. Strict prerequisite mode prevents the engine from recommending an advanced objective while required objectives remain unmastered.

The score is a prioritization heuristic, not a psychometric exam score. It decides what to practice next; it does not predict an AWS Certification result.

## Create progress

```bash
aws-cert init-progress --certification SAA-C03 --output progress.yaml
```

## Inspect the next activities

```bash
aws-cert recommend \
  --certification SAA-C03 \
  --progress progress.yaml
```

## Plan a quiz

```bash
aws-cert quiz-plan \
  --certification SAA-C03 \
  --mode adaptive \
  --progress progress.yaml \
  --count 10 \
  --output quiz-plan.yaml
```

A plan can reuse a matching approved repository question. Empty slots contain explicit original-question authoring constraints.

For a mock exam plan:

```bash
aws-cert quiz-plan \
  --certification SAA-C03 \
  --mode mock \
  --count 65 \
  --time-limit 130 \
  --output mock-plan.yaml
```

Mock planning follows certification-domain percentages. It is a blueprint for an unofficial practice exam, not a copy of the live AWS exam.

## Record evidence

Create an attempt that conforms to `schemas/attempt.schema.json`, then run:

```bash
aws-cert record-attempt \
  --certification SAA-C03 \
  --progress progress.yaml \
  --attempt attempt.yaml
```

The update is conservative. Proficiency requires repeated evidence and sufficient accuracy. Incorrect evidence can move an objective from `proficient` to `needs_review`.
