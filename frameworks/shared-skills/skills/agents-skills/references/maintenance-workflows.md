# Skill Maintenance Workflows

Repository-specific procedures for creating, auditing, and shipping skills. Read only the section that matches the task.

## Table of Contents

- [Scenario Matrix](#scenario-matrix)
- [Scaffolding and Support Files](#scaffolding-and-support-files)
- [Compatibility and Invocation](#compatibility-and-invocation)
- [Validation](#validation)
- [Catalog and Routing Changes](#catalog-and-routing-changes)
- [Common Failure Modes](#common-failure-modes)

## Scenario Matrix

| Scenario | Action | Complete when |
|----------|--------|---------------|
| Create a portable skill | Use standard `skill-creator`; set explicit `name` and trigger-rich `description`; add two or three eval tasks | Static validator passes and real trigger language selects it |
| Audit or modernize | Run `python3 scripts/validate_skill.py <skill-dir>`; fix contract drift, links, navigation, and sources | Zero applicable errors and no unscoped runtime field beside a portability claim |
| Add Claude-only fields | Verify current field semantics, add the field, and name Claude in `compatibility` | The field appears only in a clearly runtime-scoped contract |
| Make a manual command workflow | Apply verified invocation controls and arguments; keep the body as an executable task prompt | Manual invocation runs the procedure and implicit activation is disabled as intended |
| Ship to Claude Code and Codex | Keep `SKILL.md` canonical; align wrapper/adjunct metadata semantically | Both surfaces express the same intent and the drift gate passes |
| Build a router or composition | Apply the stage-based selection pipeline in `skill-patterns.md` | Every rejected candidate has a filter reason and final selection is traceable |
| Reduce a long root | Move detail to `references/`, helpers to `scripts/`, templates to `assets/` | The root is navigation-first and every support file is reachable |
| Repair under- or over-triggering | Change description/routing surface and add positive plus negative cases | Trigger and non-trigger cases both pass |
| Add cross-session state | Use Pattern 7 in `skill-patterns.md`; keep state out of source truth | First run works without state and no secret is stored |
| Change discovery or routing | Regenerate graph and update applicable routing/eval registries | Graph and coverage checks pass |

If no row matches, use the create or audit workflow and keep the change bounded to the requested capability.

## Scaffolding and Support Files

Use standard `skill-creator` for a fresh skeleton rather than hand-authoring boilerplate. Then apply the repository delta:

- Add `compatibility: Portable core only. Add runtime-specific notes if extensions are used.` unless deliberately runtime-scoped.
- Keep `SKILL.md` functional and navigation-first.
- Put decision trees, variants, and background in `references/`.
- Put deterministic validation, conversion, generation, or scoring in `scripts/`.
- Put output templates and boilerplate in `assets/`.
- Link every support file in the workflow or Navigation; a file mentioned only in an inventory is usually inert.
- Bias toward splitting before 500 lines. At this repository's 250-line threshold, ensure the long-skill pilot manifest contains a routing task.

## Compatibility and Invocation

Portable assumptions are limited to the Agent Skills open contract: explicit `name`, `description`, optional `license`, `compatibility`, `metadata`, and the skill bundle. Treat implementation-specific support for `allowed-tools` separately.

Runtime controls such as `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `when_to_use`, `context`, `agent`, `model`, `effort`, `hooks`, `paths`, `shell`, and `disallowed-tools` require current runtime verification. Their substitutions and lifecycle semantics are not portable.

For side-effecting workflows such as deploys, sends, or production writes, use the target runtime's verified explicit/manual invocation control. Document the equivalent separately for every supported runtime.

For Codex in this repository:

- Keep the portable `SKILL.md` authoritative and valid without adjunct files.
- Use `agents/openai.yaml` only for Codex-facing interface and policy metadata when present.
- Keep `short_description` suitable for UI display and `default_prompt` focused on when to load the skill.
- Check semantic alignment; exact text equality is neither required nor sufficient.

See `frontmatter-reference.md` for field-level details and `anthropic-skills-guide.md` for Claude behavior.

## Validation

From the `agents-skills` directory, select checks by scope:

```bash
# One skill
python3 scripts/validate_skill.py <skill-dir>

# Validator regressions
python3 scripts/test_validate_skill.py

# Whole catalog and metadata
python3 scripts/validate_catalog.py /path/to/skills/root
python3 scripts/audit_skill_metadata.py /path/to/skills/root
python3 scripts/build_skill_graph.py /path/to/skills/root --check
```

The static tools cover frontmatter, folder naming, links, long-reference TOCs, source metadata, runtime-field/portability conflicts, registry references, local inventory thresholds, compact-index structure, and graph edges. They do not prove routing or answer quality. Use `skill-validation.md` for trigger, non-trigger, navigation, and effectiveness-claim design.

Repository pilot commands from the repository root:

```bash
python3 frameworks/shared-skills/evals/test_run_skill_bench.py
python3 frameworks/shared-skills/evals/run_skill_bench.py \
  frameworks/shared-skills/evals/tasks/pilot-router-and-long-skills.json \
  --adapter codex \
  --repo-root . \
  --output frameworks/shared-skills/evals/outputs/pilot-router-and-long-skills-codex-YYYY-MM-DD.jsonl
```

Store benchmark output as JSONL under `frameworks/shared-skills/evals/outputs/`; do not create a separate Markdown run summary unless requested.

## Catalog and Routing Changes

From `frameworks/shared-skills/`:

```bash
python3 scripts/graph-export.py
python3 scripts/validate-graph.py
python3 scripts/audit-coverage.py --check
python3 scripts/validate-eval-manifests.py
```

Regenerate after any `SKILL.md` body or routing edit because the graph hashes full bodies. Refresh the audit baseline only when the intended source change explains the delta; never use a baseline rewrite to hide an unexplained failure.

Do not shorten complete skill bodies merely to satisfy a discovery budget. Diagnose installed, enabled, and model-visible inventories separately using [skill-context-budgets.md](skill-context-budgets.md). The generated `graph/codex-discovery.md` supports compact selection after loading; it does not filter the native startup catalog. Apply the target host's supported catalog budget before considering a smaller installation.

## Common Failure Modes

- A broad description omits the user language that should trigger it, or overlaps an adjacent skill without a negative case.
- A skill claims portability while depending on one runtime's headers, substitutions, hooks, or invocation model.
- Examples and policy prose accumulate in `SKILL.md` even though they are needed only for one branch of the workflow.
- Support directories exist but the workflow never tells the agent when to open them.
- Syntax and link checks pass while trigger, non-trigger, or navigation behavior remains untested.
- A source list is stale, secondary-only, or disconnected from claims in the workflow.
- Candidate enrichment silently removes options instead of preserving them or naming a filter reason.
- Adjacent candidates are ranked before each is evaluated independently.
- Useful workflow detail is deleted to reduce listed context even though a compact generated discovery layer already exists.
- Model-quality or token-saving percentages are repeated without a matched control, reproducible run, source provenance, and limitations.
