# agents-skills — Learnings

## Patterns That Work

- [2026-08-28] For a multi-skill expert upgrade, run read-only persona reviewer agents first (one memo each), then one implementer per file set with a shared brief carrying the cross-cutting fixes; that keeps one writer per file.
- [2026-08-05] Presentation layer over a governed pipeline (a project-scoped triage engine's usage-performance pack): consume derived CSVs+manifest, inherit suppressions verbatim, never re-score.
- [2026-06-11] When vendoring a third-party skill, copy only data files its script registries (CSV_CONFIG-style) actually reference; grep-verify license, stdlib-only imports, no network/exec; attribute upstream in the reference doc and sources.json.
- [2026-06-10] When deepening a domain skill, gap-check the user's named subdomains against existing references, then wire each new reference into a workflow stage — a reference cited only in Navigation is dead weight.
- [2026-07-11] Re-verified Claude Code + agentskills.io + Codex CLI primary docs against this skill's claims: the skill-listing character budget defaults to 1% of the model's context window (not the previously stated 2%/~16K), configurable via `skillListingBudgetFraction`; new frontmatter fields `arguments` and `shell` exist and were missing from the compatibility matrix; `context: fork` skips `CLAUDE.md` only for `agent: Explore`/`Plan`; Codex CLI natively discovers skills from `.agents/skills` + `~/.codex/skills` reading plain `name`/`description` — this repo's `agents/openai.yaml` is a local convenience file, not something Codex reads out of the box. Frontmatter field semantics drift fast enough that a full re-fetch of the three primary docs (not just a diff-based skim) caught real errors — do this on every audit, not just when a field "seems off."
## Mistakes to Avoid

- [2026-08-26] Citing a previously-uncited skill makes its audit-coverage-exceptions.json entry STALE: delete that entry, then rewrite the baseline. Baseline rewrite alone never clears STALE.
- [2026-07-16] Citing cross-router skills in a router's references/*.md trips audit-coverage 'implicit_handoffs' — declare them in the router registry's handoffs block in the same commit.
- [2026-08-05] Before creating a new skill, check whether an existing engine/pack already owns the domain — a new capability on an existing pipeline usually belongs as pack content (recipe + script), not a sibling skill; user preferred consolidating founder AI-adoption reporting into the existing project-scoped engine over a standalone skill.
## Domain Knowledge

- [2026-09-11] Correction to 2026-07-11: Codex supports agents/openai.yaml for UI, dependencies, and invocation policy; the earlier claim that Codex does not read it is outdated.
- [2026-08-26] validate_skill.py rejects non-HTTPS urls in data/sources.json; point internal repo-local documents from metadata.description prose instead of a source url.
- [2026-08-05] audit-coverage --check needs 4 touches per new skill: router registry entry, citations in 2 routers' references, handoff declaration in the citing router, audit-config direct_use_skills.
## Open Questions

## Consolidated Principles

