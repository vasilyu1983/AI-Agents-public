# Persona Testing Report — {{app name}}

## Executive Summary

- App / build: {{URL, version, date}}
- Personas tested: {{N}} ({{names + segments}})
- Scenarios run: {{N}} | Completed: {{N}} | Abandoned: {{N}}
- Top verdict: {{one sentence — the single most important thing to fix}}
- Overall persona-fit score: {{1-5}} — {{one line justification}}

## Persona Verdicts

| Persona | Scenarios | Completion | Would return? | One-line verdict (in persona voice) |
|---|---|---|---|---|
| {{name}} | {{n/m}} | {{%}} | yes / unsure / no | "{{...}}" |

## Findings (ranked by severity, then frequency across personas)

### {{F-1}} — {{finding title}}

- Severity: {{0-4}} | Personas affected: {{list}} | Scenario/step: {{refs to session logs}}
- What happened: {{1-3 sentences, grounded in a logged step}}
- Persona quote: "{{verbatim from session log}}"
- Evidence: {{screenshot ref / console error / network trace}}
- Recommended fix: {{smallest change that removes the friction}}
- Effort estimate: low / medium / high

## What to Improve (prioritized)

| Priority | Change | Fixes findings | Expected effect |
|---|---|---|---|
| P1 | {{...}} | {{F-ids}} | {{completion/trust/speed effect}} |

## What to Avoid

- {{pattern that tested well elsewhere but hurt this ICP — do not "fix" it}}
- {{tempting change that would break a working flow}}

## What Worked (keep)

- {{flows/patterns that all personas passed without friction — protect in regression tests}}

## Validity and Limitations

- Simulation caveats: findings come from LLM persona simulation, not real users. Treat severity-4 issues as real (they are mechanical failures); treat preference/emotion findings as hypotheses to confirm with real users.
- Personas were {{validated / assumed}} — see each persona profile's Provenance section.
- Not covered: {{devices, locales, flows not exercised}}

## Follow-ups

- [ ] Convert severity ≥3 findings into regression tests (`qa-testing-playwright`)
- [ ] Validate top preference findings with real users (`software-ux-research`)
- [ ] Re-run this persona pack after fixes; compare completion and friction counts
