# HTML vs Markdown for Spec Artifacts

Moved out of SKILL.md to keep the core lean. Load this when choosing the output format for a human-facing PRD, tech spec, exploration doc, or planning brief.

Markdown is the default for most context-file surfaces (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`), but it is not always the right format for the *human-facing artifacts* this skill produces (PRDs, tech specs, exploration docs, planning briefs, code-review writeups). For artifacts intended to be read by humans rather than parsed by the next agent, consider HTML.

This guidance is based on [Thariq, *Using Claude Code: The Unreasonable Effectiveness of HTML*](https://x.com/trq212/status/2052809885763747935) (Claude Code team, 2026-05-08).

### When HTML wins over Markdown

- The artifact will exceed ~100 lines and needs to actually be read by stakeholders (most PRDs and tech specs cross this threshold).
- The spec benefits from visual structure: tables, SVG diagrams, color-coded findings, side-by-side comparisons, annotated code diffs.
- The artifact will be shared via link (S3, internal storage) rather than read in a repo viewer.
- The spec is **exploratory** — multiple design options compared in a grid, mockups, data-flow diagrams.
- The artifact is interactive — sliders, drag-drop reordering, form-based configuration with a "copy as JSON / prompt / diff" export button at the end.

### When Markdown still wins

- Agent-consumed context files (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`) stay markdown — agents parse markdown reliably and HTML adds no signal for them.
- Artifacts that live in version control and need clean diffs — HTML diffs are noisy and hard to review.
- Short artifacts (≤100 lines) where added expressiveness is not worth the extra generation time and tokens.
- Acceptance criteria meant to be evaluated programmatically (Gherkin, JSON Schema), where structure matters more than rendering.

### Concrete tradeoffs

| Dimension | Markdown | HTML |
|---|---|---|
| Generation time | Baseline | Longer (more markup to emit; no measured multiple, so benchmark on your own artifacts) |
| Token cost | Lower | Higher (frontier large-context models absorb it for most artifacts) |
| Read-through likelihood for >100-line specs | Low — author of [Thariq's article](https://x.com/trq212/status/2052809885763747935) reports "I tend to not actually read more than a 100-line markdown file" | Much higher — visual structure invites reading |
| Shareability | Poor — most browsers don't render natively | Excellent — upload + link |
| Version-control diffs | Clean | Noisy |
| Interactive elements | None | Sliders, drag-drop, forms, copy buttons |
| Agent re-ingestion | Native | Works, but markdown is denser per token |

### The export-button pattern (interactive specs)

When generating an interactive HTML artifact, always end with an export control: *"copy as JSON"*, *"copy as prompt"*, *"copy diff"*, *"copy as markdown"*. The button turns UI manipulation back into pasteable text that closes the loop into the next prompt or PR description. Interactive specs without an export button create a one-way artifact the user can't act on.

### Recipe — HTML spec authoring

1. Decide format up front based on the table above. Default to markdown for context-file surfaces; default to HTML for read-once human artifacts >100 lines.
2. For HTML, point Claude at the codebase's existing UI or design system. Maintain one **design-system HTML file** per project that other HTML artifacts can reference to match company style.
3. For exploration specs, request a grid layout with multiple options side-by-side, each labeled with the tradeoff it makes.
4. For interactive HTML, specify the export control explicitly in the prompt — do not assume the agent will add it.
5. For implementation handoff, write the HTML spec for the human reviewer; then in the next session, pass the HTML file to the implementation agent along with markdown acceptance criteria. The implementation agent gets binary criteria; the human gets the richer artifact.

### Related skills

- Interactive HTML with controls + export button: `playground:playground` plugin skill (interactive playground pattern is the same shape)
- Frontend design for matching company style: `frontend-design:frontend-design` plugin skill
- Plan output format selection (HTML vs markdown for plan documents): [`../../dev-workflow-planning/SKILL.md`](../../dev-workflow-planning/SKILL.md)

### What not to do

- Do not build a forced `/html` skill or rule that everything must be HTML — Thariq's own caution. Prompting fluency beats a forced abstraction.
- Do not put PRDs and context files in the same format by default — the right format depends on the audience (human vs agent).
- Do not lose acceptance criteria in HTML decoration — the binary, measurable parts must remain extractable, ideally as a code block or table the implementation agent can parse cleanly.
