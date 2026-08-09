# Priority-Based UX Audit Scoping

Use this model to scope heuristic evaluations and UX audits by impact priority, and to assign consistent severity to findings. Adapted from the rule taxonomy in [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT). It complements — does not replace — [ux-audit-framework.md](ux-audit-framework.md) (process) and the heuristic evaluation template in `assets/audits/`.

## Table of Contents

- [Why Priority-Ordered Audits](#why-priority-ordered-audits)
- [Audit Dimension Priorities](#audit-dimension-priorities)
- [Severity Model](#severity-model)
- [Using the Queryable Guideline Database](#using-the-queryable-guideline-database)

## Why Priority-Ordered Audits

Unscoped heuristic reviews produce flat finding lists where a missing focus ring and an off-brand shadow carry equal weight. Auditing in priority order forces evaluator time onto the dimensions that block users first, and gives stakeholders a defensible ranking when remediation budgets are limited.

Rule: report findings grouped by dimension priority, not by screen. A screen-by-screen report hides systemic failures (e.g. every form validating on keystroke) behind page-local noise.

## Audit Dimension Priorities

| Priority | Dimension | Impact | What the Evaluator Checks |
|----------|-----------|--------|---------------------------|
| 1 | Accessibility | CRITICAL | contrast ratios, keyboard/focus paths, labels, reduced-motion, text scaling |
| 2 | Touch & interaction | CRITICAL | target sizes and spacing, feedback latency, loading-state controls, gesture alternatives |
| 3 | Performance-perceived | HIGH | layout shift, skeleton vs spinner, list virtualization, input latency |
| 4 | Visual consistency | HIGH | one style language, icon family discipline, elevation scale, token usage |
| 5 | Layout & responsive | HIGH | breakpoint behavior, zoom enabled, spacing rhythm, safe areas |
| 6 | Typography & color | MEDIUM | base size and line-height, semantic tokens, dark-mode contrast tested separately |
| 7 | Motion | MEDIUM | duration bands, purpose of each animation, interruptibility, reduced-motion path |
| 8 | Forms & feedback | MEDIUM | label visibility, error placement and recovery, validation timing, focus management |
| 9 | Navigation | HIGH | back-behavior predictability, state restoration, deep-link coverage, pattern mixing |
| 10 | Data display | LOW | chart-type fit, legend/tooltip access, table fallback, color-independence |

Note priority 9 is HIGH despite its position: navigation defects are ranked after form defects only because they are rarer, not because they are cheaper.

## Severity Model

Assign each finding one severity, tied to evidence — not evaluator taste:

| Severity | Definition | Evidence Bar |
|----------|------------|--------------|
| Critical | blocks task completion or excludes an assistive-tech user | reproduced blocker or WCAG failure on a core task path |
| High | causes errors, abandonment, or repeated friction on core paths | observed failure or guideline breach on priority 1–5 dimension |
| Medium | slows users or degrades trust; workaround exists | guideline breach with plausible user cost |
| Low | polish or consistency issue with no task impact | visual/convention deviation only |

Cap any finding without observed-user or standards evidence at Medium. Heuristic opinion alone never yields a Critical.

## Using the Queryable Guideline Database

The sibling design skill vendors an offline, severity-rated guideline database (UX rules with do/don't pairs and code examples, queryable by keyword via BM25 search). During an audit, use it to ground findings in named rules instead of evaluator phrasing:

```bash
# from frameworks/shared-skills/skills/software-ui-ux-design/
python3 scripts/search.py "validation error focus" --domain ux
python3 scripts/search.py "touch targets safe areas" --domain web
```

See [../../software-ui-ux-design/references/design-database-search.md](../../software-ui-ux-design/references/design-database-search.md) for domains and query strategy. Citing a database rule (with its severity and platform column) in the finding makes the report auditable and keeps severity assignments consistent across evaluators.
