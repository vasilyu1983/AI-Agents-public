# Shared Skills Instructions

These rules apply under `frameworks/shared-skills/`. Root repository boundaries still apply.

## Change Contract

- Treat `graph/` (`graph.json`, `codex-discovery.md`, DOT, and per-router Mermaid) as the canonical catalog.
- After any `SKILL.md` body or routing change, run `python3 scripts/graph-export.py` from this directory. The graph hashes full skill bodies, so prose edits can make it stale. Stage the regenerated artifacts with the skill change; later body edits require regeneration again.
- When a `SKILL.md` exceeds 250 lines, add or retain a pilot task in `evals/tasks/pilot-router-and-long-skills.json` in the same change. Check with `python3 scripts/validate-eval-manifests.py`.
- Keep affected README files and router documentation aligned with inventory changes. Read counts from the generated catalog; avoid new hand-maintained totals.
- `router-main` is the universal entry point; domain routers own scenarios and journeys.
- `project-*` skills are self-contained. Cross-link only within the same project family unless the user explicitly approves an exception.
- When a real route helps, misses, or fires incorrectly, append one dated evidence line to `routing-log.md`.
- Security-review third-party skills before installing them into any runtime: `python3 scripts/check-external-skill.py <staged-skill-dir>`. Exit 2 blocks installation; exit 1 requires reviewing findings.

## Validation by Scope

From `frameworks/shared-skills/`, run the smallest complete set that covers the change:

```bash
# SKILL.md body or routing edits
python3 scripts/graph-export.py
python3 scripts/validate-graph.py
python3 scripts/audit-coverage.py --check
python3 scripts/validate-eval-manifests.py

# Any edited skill bundle
python3 skills/agents-skills/scripts/validate_skill.py skills/<skill>

# Bundles with data/script-contracts.json or documented script-constant changes
python3 scripts/check-script-contracts.py --skill <skill> --check

# Repository memory edits
bash skills/agents-memory/scripts/lint_claude_memory.sh ../..

# Agent or skill additions that affect profile claims
python3 ../../scripts/check-profile-claims.py --check

# Executable model/version pins; only BLOCKING entries fail the gate
python3 scripts/check-version-pins.py skills --check

# Skill prose versus skill-owned data
python3 scripts/check-data-drift.py --check
```

ROT and DRIFT findings are informational and often intentional examples. Do not mass-edit them to zero; inspect the classes and act only on executable-path findings.

Run `python3 scripts/refresh-versions.py --check` when current framework/runtime versions are edited; it requires network access. Run `python3 scripts/check-citation-claims.py --precise` when editing a skill that cites papers. Citation findings are advisory and mean untraceable, not necessarily wrong.

When editing `dev-context-code-graph`, `dev-context-multi-repo`, or `dev-context-engineering`, also run:

```bash
python3 skills/dev-context-code-graph/scripts/test_graph_core_sync.py
python3 skills/dev-context-code-graph/scripts/test_code_graph_regressions.py
python3 skills/dev-context-multi-repo/scripts/test_knowledge_graph_regressions.py
```

For documentation-only edits outside skill bundles and generated artifacts, inspect the diff and run applicable link, command, and instruction checks. For implementation or validator changes, run focused tests plus the gates above and fix regressions caused by the change.

## Source and Data Policy

- Never manufacture a numeric result. Read the cited primary source, reproduce its direction and magnitude faithfully, or hedge.
- Do not hardcode “the current version” in prose. Read the consuming skill’s `data/versions.json` or write “current stable — verify.” Keep literals when the number is a breaking boundary, EOL/compliance date, standard identifier, floor constraint, worked example, or historical price.
- Each skill owns the data it consumes under its own `data/`; there is no repository-level shared data directory.
- A skill that states a current model price or framework version must own the matching `model-pricing.json` or `versions.json` so `check-data-drift.py` can compare it.
- Retired model rates remain for replaying historical usage. When a current price changes, update every consuming copy and its `last_verified` date after checking the vendor source.
- Skills that load data programmatically must remain detachable. Resolve paths from `Path(__file__).resolve()` and keep an embedded fallback behind `try/except ImportError`; use `skills/ai-llm/scripts/cost_estimator.py` as the pattern.
- Fixes to duplicated `_lib/resolve_versions.py` files must be copied to every consumer. Verify deployed resolution with `python3 skills/ai-llm/_lib/resolve_versions.py`; “not carried by this skill” is expected, but neither file resolving is a failure.

`scripts/refresh-versions.py` defines `VERSION_CONSUMERS` and rewrites each consuming `versions.json`. Model pricing has no live resolver and remains hand-maintained. Do not centralize these files: skills must work when copied alone or distributed as plugins.

## Publication Boundary

Public allowlisted skills must not contain employer/client identities, handles, PII, secrets, or client-sensitive examples. Use “client-specific families” and follow `../../docs/public-publication-policy.md`.

`../../scripts/sync-repo-into-public.sh` publishes each allowlisted skill’s `data/` and `_lib/`. Its per-skill loop fails closed, while its tree-level sync excludes known private directories by denylist. Review publication behavior before adding any new top-level directory under `shared-skills/`.

## Catalog and Routing

Use `graph/codex-discovery.md` first and `graph/graph.json` for full detail. Confirm skill names with:

```bash
python3 scripts/find-skill.py --resolve <name>
python3 scripts/find-skill.py "<task description>"
```

The Claude hook and this script share `scripts/skill-aliases.json`. Add an alias only after confirming the target skill covers the attempted name. When a legitimate task does not rank its owner, improve the description or routing surface and add trigger/non-trigger evidence; do not tune only the search phrase.
