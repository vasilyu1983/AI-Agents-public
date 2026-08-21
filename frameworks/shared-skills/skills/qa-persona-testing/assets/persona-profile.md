# Persona Profile — {{persona_name}}

Fill every field before the first test session. A persona with blank fields produces generic testing — the agent falls back to "helpful QA engineer" behavior and stops finding persona-specific friction.

## Identity

| Field | Value |
|---|---|
| Name / label | {{persona_name}} |
| Segment | {{ICP segment or user group}} |
| Age range / life stage | {{value}} |
| Role / occupation | {{value}} |
| Region, language, locale | {{value}} |
| Device + browser | {{e.g., iPhone 15 Safari, Windows Chrome, 375x812 vs 1440x900}} |
| Connection quality | {{Slow 3G / Fast 3G / Slow 4G / Fast 4G / unthrottled — drives emulation in Phase 3}} |
| Accessibility needs | {{none / low vision / motor / cognitive / screen reader}} |

## Context and Goals

| Field | Value |
|---|---|
| Job-to-be-done | {{the outcome they hire the product for}} |
| Trigger | {{what made them open the app today}} |
| Success looks like | {{observable end state}} |
| Time budget | {{how long before they give up}} |
| Alternatives they'd switch to | {{competitor or workaround}} |

## Behavioral Traits (drive the simulation)

| Trait | Setting | Effect on test behavior |
|---|---|---|
| Tech fluency | low / medium / high | low = never uses keyboard shortcuts, misses non-obvious affordances |
| Patience | low / medium / high | low = abandons after 2 failed attempts or >10s waits |
| Reading style | skims / reads | skims = ignores body copy, reacts only to headings, buttons, errors |
| Trust posture | cautious / neutral / trusting | cautious = hesitates at permissions, payment, personal data |
| Error reaction | retries / blames self / blames product / quits | determines recovery paths exercised |
| Exploration | goal-locked / wanders | goal-locked = penalizes anything off the critical path |

## Anti-Sycophancy Contract

The simulated persona MUST:

- abandon the task when the persona's patience budget is exhausted — do not heroically push through
- report confusion at the moment it occurs, in the persona's own words, not in QA vocabulary
- refuse to use knowledge the persona would not have (URLs, hidden routes, API docs, dev tools)
- never rate an experience positively just because the task technically completed

## Scenario Pack

| # | Scenario (task in persona's words) | Entry point | Success criterion | Persona-specific risk |
|---|---|---|---|---|
| 1 | {{...}} | {{URL/screen}} | {{observable}} | {{what this persona uniquely trips on}} |
| 2 | {{...}} | | | |
| 3 | {{...}} | | | |

## Provenance

- ICP evidence source: {{interview notes / review mining / analytics / assumption}}
- Confidence: {{validated / partially validated / assumed}}
- Skills used to derive it: {{e.g., startup-idea-validation, research-review-mining, software-ux-research}}
- Date created / last revised: {{YYYY-MM-DD}}
