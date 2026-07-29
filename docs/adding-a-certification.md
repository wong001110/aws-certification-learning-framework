# Adding a certification pack

A certification pack lets the universal skills support another AWS certification without changing their core instructions.

## 1. Confirm the certification

Use the official AWS Certification Exam Guides index. Record the active exam code, name, level, and official exam-guide URL.

## 2. Create the pack

Create `certifications/<level>/<exam-code>/certification.yaml` and use an existing reference pack as a template. Include identity, status, verification date, official exam guide, candidate profile, response types, domain weights, depth profile, question patterns, and out-of-scope boundaries.

## 3. Update the registry

Add the pack to `certifications/registry.yaml`.

## 4. Add original examples

Add at least one independently authored example that conforms to the question schema, tests a named domain, cites current public AWS sources, and has been independently reviewed.

## 5. Run checks

```bash
make check
```
