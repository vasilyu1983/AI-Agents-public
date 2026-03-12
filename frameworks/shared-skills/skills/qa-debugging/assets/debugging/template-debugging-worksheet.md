# Debugging Worksheet (Reproduce -> Isolate -> Instrument -> Verify)

Use this worksheet to keep debugging evidence-driven and fast.

## Core

### 1) Reproduce

- Symptom (what users see): ___________________________________________
- Expected behavior: _________________________________________________
- Actual behavior: ___________________________________________________
- Repro steps (minimal): _____________________________________________
- Repro rate: ____ / ____ runs (____%)
- Environment: local / CI / staging / prod
- Version/build SHA: _________________________________________________

Evidence captured:
- Error message / stack trace: _______________________________________
- Timestamp(s): _____________________________________________________
- Request ID / trace ID: ____________________________________________
- Logs / traces / screenshots attached: yes/no

### 2) Isolate

- Smallest failing input: ___________________________________________
- Smallest component boundary: ______________________________________
- "Recent change" suspected? yes/no
- Bisect plan (git bisect / feature flags): __________________________

### 3) Instrument

- What signal is missing? logs / metrics / traces / assertions
- Instrumentation added (scoped): ____________________________________
- What do you expect to see if hypothesis is true? ___________________

### 4) Verify

- Fix summary (root cause): _________________________________________
- Regression test added (path/layer): ________________________________
- Verified in CI-like conditions: yes/no
- Post-fix monitoring signals checked: _______________________________

### Do / Avoid

Do:
- Prefer minimal repro and smallest layer.
- Record evidence links (IDs, logs, traces) so others can verify.

Avoid:
- Random changes without a hypothesis.
- "Fixing" by adding sleeps or weakening assertions.

## Optional: AI / Automation

Do:
- Use AI to summarize logs/traces and propose hypotheses; keep evidence IDs in the summary.
- Use AI to draft a regression test outline, then implement and validate manually.

Avoid:
- Treating AI output as root cause without corroboration.
