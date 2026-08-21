# Harness Audit Playbook

Periodic health check of an agent harness (skill library, deploy targets, hooks, catalogs). Distilled from the 2026-08-14 audit of this repo. Run when asked to "check the harness", "is my setup strong", or before a pruning pass.

## Order of Operations

1. **Inventory before opinion.** Count skills/agents/hooks in the repo library and every deploy target (`~/.claude/skills`, `~/.agents/skills`, `~/.codex/skills`, project-local `.claude/skills` in other repos). Distinguish symlinks from real directories — real dirs in deploy targets are either third-party installs or drift.
2. **Verify best practices against current sources.** Harness practice moves fast; do not audit from parametric memory. Web-search the current consensus (skill-budget mechanics, prune cadence, orchestration patterns) and cite it.
3. **Instrument before pruning.** Never prune on intuition. Log actual skill fires (Claude Code: `PostToolUse` hook on the Skill tool; Codex: append point in the resolver script) and collect ≥30 days before any data-driven cut. Re-run the routing eval before/after — accuracy should rise as the catalog shrinks; if not, the prune targets were wrong.
4. **Audit sprawl read-only first.** Produce a keep/archive/delete proposal; execute only after explicit approval.

## Hard Rules

- **Canonical library is the only source of truth.** Sync flows library → satellites (symlinks), never satellite → library. A diverged project-local copy is drift to discard, not content to rescue. Before "rescuing" any off-library skill, check `git log --all` — deliberately deleted (consolidation, reorg) means the stray copy dies too.
- **Do not touch official marketplace skills (Claude/Codex/vendor catalogs).** Real dirs like the Cloudflare set (`cloudflare`, `wrangler`, `workers-best-practices`, …) are third-party content: leave in deploy dirs, never absorb into the library, never add to graph/INDEX/public sync, never let them republish. Authorship test: vendor voice in descriptions, upstream doc URLs, retrieval-bias boilerplate. Gate every third-party skill with `check-external-skill.py`; CAUTION verdicts go to the human.
- **Gates are immutable to the content they gate.** Never edit an audit/coverage/drift script to make new content pass. If the gate rejects it, the content conforms or stays out.
- **Check recoverability before deleting.** Deletion of a snapshot copy is safe only if git history (or the live library) holds the content. Unbacked-up + diverged = do not delete without human sign-off.
- **Divergence tripwire on snapshot cleanup:** before replacing a snapshot dir with a symlink, run `find <dir> -newermt <snapshot-date> -type f`. Any hits → leave that dir, report it. Spot-diff 2–3 dirs against the library to confirm stale-copy vs fork before bulk deletion.

## What "Strong" Looks Like (audit criteria)

- Library ↔ generated graph ↔ deploy symlinks agree exactly (zero drift either way).
- Fire-rate telemetry exists and the routing log records real routing outcomes, not just intentions.
- No hash-suffixed or generation-artifact entries; no stale INDEX advertising dead names (stale indexes invite confabulated invocations).
- Hooks fail loud, gate scripts exit nonzero, third-party boundary is explicit.
- An orchestration layer exists above single-skill routing: named workflows with adversarial verification (reviewer proposes falsifiable claims; independent refuters must attack them; majority-refuted findings die).

## Anti-Patterns Observed

- Counting catalog size as strength — every unfired entry taxes discovery budget; lean beats large.
- Promoting deploy-dir content into the library because "it's unmanaged" — location on disk does not establish ownership; authorship does.
- Editing the gate instead of the content (rubber-stamps the audit).
- Pruning, merging, or "improving" skills as a side effect of an audit — the audit reports; a separately approved pass executes.
