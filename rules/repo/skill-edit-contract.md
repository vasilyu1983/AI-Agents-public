---
paths:
  - "skills/**"
description: Load before creating or editing any skill.
owner: docs/procedures/skill-library-maintenance.md
---
# Skill Edit Contract

Load this before creating or editing any skill under `skills/`.

- Rule IDs point into skill-library-maintenance.md, which holds the rationale, gates and dated facts.
- Batch runs follow skill-library-operations.md.
- Git in a shared tree follows multi-agent-git-safety.md.
- `skills/AGENTS.md` wins on conflict.

1. **Search before creating** (R1). Run `python3 scripts/find-skill.py "<task>"`. Extend an existing owner when it covers the capability.
2. **Read what you will change, not the library** (M1).
   - the `SKILL.md`;
   - the references a signal points at;
   - `learnings.consolidated.md`;
   - the owning registry entry.
3. **Protect other people's work** (M3). Run `git status` first and edit only paths you own. Never stash, `reset --hard`, check out or restore paths, or `clean -f`. Hooks block these commands; report a block instead of working around it.
4. **Give every fact one home** (§1).
   - Judgment goes in `SKILL.md`.
   - Depth goes in `references/`, linked with a load condition from the step that needs it, one level deep (S4); a reference links on to another reference only when `SKILL.md` links that one too. A support file nothing links to is never loaded: link it or cut it.
   - Volatile values are generalized or replaced by a lookup step (F1). Only a value a bundled script reads at run time goes in `data/*.json`, with `source` and `last_verified` (F10); prose never repeats it.
   - Live state is fetched at run time.
   - Counts are generated.
5. **Keep out of prose any value that changes faster than the prose** (F1). No current versions, prices or limits, and no "as of" claims. Literals are allowed only for:
   - boundaries;
   - EOL and effective dates;
   - standard IDs;
   - floors;
   - labelled examples;
   - historical prices.

   Provenance dates on cited evidence are fine. Prove it: `python3 audit/audit-scan.py volatile --check <skill>` exits 0 (from the repository root).

   Do not add a generic `## Fact-Checking` block (F1). A skill with changeable external facts writes a specific lookup step where the fact is used, not a boilerplate section restating "verify before answering."
6. **Apply the token test to every paragraph** (Q1). Keep only what a strong current model would get wrong without it. Delete generic advice, recaps, restated descriptions, and identity or effort lines.
7. **Encode decisions, not menus** (Q3–Q5).
   - Give one default plus the condition for deviating from it.
   - Build gotchas from real failures.
   - Give exact commands only for fragile steps.
8. **Frame for judgment** (Q6). Use hard rules only for high stakes or observed failures, each with a one-clause reason. Avoid ALL-CAPS emphasis.
9. **Never invent a number** (Q11). Cite only what you read. An effectiveness or savings claim needs a control; otherwise write "not yet measured".
10. **Write the description as trigger text** (S6, R5). Follow "Does X. Use when Y.", with the key use case first and within the audit budget. `SKILL.md` stays canonical over `agents/openai.yaml`; when it changes, align `short_description` and `default_prompt` in `agents/openai.yaml`, and check that neighbouring skills don't lose their triggers.
11. **Put critical content first** (S2). A leaf skill hands off at most one level (S9).
12. **Make the minimal diff** (M2, M5, M7). Pick one pattern and never blend two. Bump `version` by hand only when the contract changes: minor for a changed trigger, workflow step or output, major for a scope change, split, merge or rename. Wording, link and fact refreshes don't bump it. `last_validated` is set by script.
13. **Leave parent-only files to the parent** (M8, R2). With other writers active, never edit any of these:
    - generated `graph/`;
    - registries or router skills;
    - `routing-log.md`;
    - audit, alias or eval manifests;
    - duplicated `_lib` copies, and any file several skills carry as identical copies (the planner lists them, F15);
    - instruction files, READMEs, `rules/` and `docs/procedures/` files, settings or hooks.

    Put the change you need in your report. The parent, or a solo editor, registers, regenerates and commits once.
14. **Report evidence, not confidence** (E1). Name the evidence level: static, loaded, routed or evaluated. Name every skipped check. A fresh-context reviewer checks the work once per wave (M6).
15. **Run the gates for your scope** from "Validation by Scope" in `skills/AGENTS.md`, and fix any failure you caused.

Why and procedure: docs/procedures/skill-library-maintenance.md#0-the-principle
