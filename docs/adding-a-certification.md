# Adding a certification pack

A certification pack lets the universal skills support another AWS certification without changing their core instructions.

## 1. Confirm the certification

Use the official AWS Certification Exam Guides index. Record the active exam code, name, level, target candidate, response types, domain weights, and official exam-guide URL.

## 2. Create the pack

Create:

```text
certifications/<level>/<exam-code>/certification.yaml
certifications/<level>/<exam-code>/curriculum.yaml
certifications/<level>/<exam-code>/lessons/
```

Use an existing reference pack as a template.

The certification file must include identity, status, verification date, official exam guide, candidate profile, response types, domain weights, depth profile, question patterns, out-of-scope boundaries, and the curriculum path and version.

## 3. Create the curriculum

The curriculum must conform to `schemas/curriculum.schema.json` and include:

- ordered stages;
- modules and prerequisites;
- stable objective IDs;
- official domain mappings;
- mastery evidence;
- at least one official source.

A module can have zero authored lessons. Agents may generate a lesson from its objectives. Reference every committed lesson path from one or more relevant modules.

## 4. Add lesson blueprints

Add at least one approved lesson conforming to `schemas/lesson.schema.json`. The lesson must reference existing curriculum objectives and official public sources.

## 5. Update the registry

Add or update the pack path in `certifications/registry.yaml`.

## 6. Add original examples

Add independently authored examples where useful. Questions must conform to the question schema and lessons must conform to the lesson schema. Do not copy public samples or commercial question banks.

## 7. Run checks

```bash
make check
```
