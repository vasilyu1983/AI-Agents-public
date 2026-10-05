# Nielsen's 10 Usability Heuristics — Evaluation Guide

Jakob Nielsen's ten heuristics (developed with Rolf Molich in 1990, refined by Nielsen in 1994) are broad principles for interaction design, used here as the checklist for an expert design review. The canonical wording is on [NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/). Research-side methods (when an expert review is not enough, cognitive walkthroughs, usability testing) live in [software-ux-research](../../software-ux-research/SKILL.md).

## Table of Contents

- [The Ten Heuristics](#the-ten-heuristics)
- [Severity Rating](#severity-rating)
- [Evaluation Process](#evaluation-process)
- [Findings Format](#findings-format)
- [Where the Fixes Live](#where-the-fixes-live)

---

## The Ten Heuristics

| # | Heuristic | What to look for | Common modern violation |
|---|-----------|------------------|-------------------------|
| 1 | Visibility of system status | Every action gets timely feedback; loading, saving, syncing and background jobs are visible | Silent autosave or sync failures; spinners with no progress for long jobs; AI agents acting with no visible status |
| 2 | Match between system and the real world | Users' words, familiar concepts, real-world order | Internal jargon and error codes ("Error 422"), database field names as labels |
| 3 | User control and freedom | Clear exits, cancel, undo and back | Destructive actions with no undo; modals with no close; back button that loses form state |
| 4 | Consistency and standards | Same words, icons and behaviours for the same things (internal), and platform conventions (external) | Two button styles for the same action; custom controls that ignore platform conventions |
| 5 | Error prevention | Constraints, good defaults and confirmation before costly mistakes | Free-text fields where a picker would prevent errors; no confirmation on irreversible actions |
| 6 | Recognition rather than recall | Options, recent items and context visible; no memorising between screens | Codes users must copy between screens; hidden gestures as the only path |
| 7 | Flexibility and efficiency of use | Accelerators for experts that do not burden novices | No keyboard shortcuts or command palette in power-user tools; no bulk actions |
| 8 | Aesthetic and minimalist design | Every element earns its place; clear hierarchy | Competing CTAs, promotional banners on task screens, repeated copy |
| 9 | Help users recognise, diagnose and recover from errors | Plain-language message at the problem, with the cause and a way out | Generic "Something went wrong"; errors only at the top of a long form; input cleared after an error |
| 10 | Help and documentation | Help is searchable, task-focused and available in context | Help only in an external site; product tours that cannot be revisited |

Error-message structure, inline validation timing and form patterns are in [form-design-patterns.md](form-design-patterns.md).

## Severity Rating

Rate each finding 0-4 on the NN/g scale, judging **frequency** (how many users hit it), **impact** (how hard it is to overcome) and **persistence** (one-time or every time):

| Rating | Meaning | Action |
|--------|---------|--------|
| 0 | Not a usability problem | None |
| 1 | Cosmetic | Fix if time allows |
| 2 | Minor | Low-priority fix |
| 3 | Major | High-priority fix |
| 4 | Catastrophic | Fix before release |

Tie severity to evidence, not evaluator taste: a finding backed only by heuristic opinion should not be rated above 2 until it is observed with users or tied to a standards failure (for example a WCAG criterion on a core task path). Blocking a core task or excluding assistive-technology users is a 4.

## Evaluation Process

1. **Prepare**: define the flows and user tasks in scope, the platforms and breakpoints, and the states to cover (loading, empty, error, success).
2. **Evaluate independently**: three to five evaluators each walk the tasks alone, noting every issue with the heuristic violated, the location and a screenshot. Independent passes find more distinct problems than a group walk-through.
3. **Aggregate**: merge findings, deduplicate issues that share a root cause, and agree one severity per issue.
4. **Group by priority dimension, not by screen**: order the report using the categories in [ui-quality-priority-rules.md](ui-quality-priority-rules.md) (accessibility and interaction first). Screen-by-screen lists hide systemic failures, such as every form validating on keystroke.
5. **Hand off**: each finding becomes a design fix, a research question, or a test candidate.

## Findings Format

```text
ID: H-012
Issue: No confirmation before deleting a workspace
Heuristic: #3 User control and freedom (also #5 Error prevention)
Location: Settings > Workspace > Delete (desktop and mobile)
Evidence: screenshot; 2 of 5 evaluators; no undo exists
Severity: 3 (Major) — frequency low, impact high, persistent
Recommendation: Add a confirmation that names the workspace, or a time-limited undo
```

## Where the Fixes Live

- Priority order and polish rules: [ui-quality-priority-rules.md](ui-quality-priority-rules.md)
- Forms, validation and error recovery: [form-design-patterns.md](form-design-patterns.md)
- Per-surface patterns (data tables, settings, search, pricing, onboarding, modals): [surface-type-recipes.md](surface-type-recipes.md)
- Loading and feedback states: [performance-ux-vitals.md](performance-ux-vitals.md)
- Accessibility criteria behind a finding: [wcag-accessibility.md](wcag-accessibility.md)
- NN/g sources: [10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), [How to Conduct a Heuristic Evaluation](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/), [Severity Ratings for Usability Problems](https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/)
