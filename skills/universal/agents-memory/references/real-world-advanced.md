# Real-World Advanced AGENTS.md — Annotated Example

A curated, annotated version of a production AGENTS.md from [openclaw/openclaw](https://github.com/openclaw/openclaw), a TypeScript CLI tool with multi-platform builds, plugin architecture, and parallel agent workflows.

This example shows what an **evolved, battle-tested** project memory file looks like — one shaped by real incidents rather than idealized templates. Project-specific details (VM playbooks, platform publishing) have been trimmed to highlight **transferable patterns**.

---
## Table of Contents

- [Section 1: GitHub Workflow Guardrails](#section-1-github-workflow-guardrails)
- [Repository Guidelines](#repository-guidelines)
- [Section 2: Auto-Close Label Automation](#section-2-auto-close-label-automation)
- [Auto-close labels (issues and PRs)](#auto-close-labels-issues-and-prs)
- [Section 3: PR Quality Gates (Evidence-Based Merge)](#section-3-pr-quality-gates-evidence-based-merge)
- [PR truthfulness and bug-fix validation](#pr-truthfulness-and-bug-fix-validation)
- [Section 4: Shorthand Commands & Agent Vocabulary](#section-4-shorthand-commands-&-agent-vocabulary)
- [Shorthand Commands](#shorthand-commands)
- [Agent-Specific Notes](#agent-specific-notes)
- [Section 5: Multi-Agent Safety Rules](#section-5-multi-agent-safety-rules)
- [Section 6: Lint/Format Churn Resolution](#section-6-lintformat-churn-resolution)
- [Section 7: Release & Version Guardrails](#section-7-release-&-version-guardrails)
- [Section 8: Dependency & Tool Schema Guardrails](#section-8-dependency-&-tool-schema-guardrails)
- [What Makes This File Effective](#what-makes-this-file-effective)
- [Adapting This for Your Project](#adapting-this-for-your-project)


## Section 1: GitHub Workflow Guardrails

> **Why this works**: encodes hard-won lessons about GitHub CLI footguns directly into agent memory, so agents don't repeat past mistakes.

```markdown
# Repository Guidelines

- GitHub comment footgun: never use `gh issue/pr comment -b "..."` when body
  contains backticks or shell chars. Always use single-quoted heredoc
  (`-F - <<'EOF'`) so no command substitution/escaping corruption.
- GitHub linking footgun: don't wrap issue/PR refs like `#123` in backticks
  when you want auto-linking. Use plain `#123`.
- PR review conversations: if a bot leaves review conversations on your PR,
  address them and resolve those conversations yourself once fixed.
- GitHub searching footgun: don't limit yourself to the first 500 issues or
  PRs when wanting to search all. Keep going until you've reached the last page.
```

**Pattern**: Name the footgun, state the rule, explain why. Agents remember negatives ("never do X") better than vague positives.

---

## Section 2: Auto-Close Label Automation

> **Why this works**: encodes process rules so agents handle triage consistently without human intervention for common cases.

```markdown
## Auto-close labels (issues and PRs)

- If an issue/PR matches one of the reasons below, apply the label and let
  `.github/workflows/auto-response.yml` handle comment/close/lock.
- Do not manually close + manually comment for these reasons.
- Why: keeps wording consistent, preserves automation behavior, and keeps
  triage searchable by label.

- `r: support`: close with redirect to community support channels.
- `r: spam`: close + lock as spam (`lock_reason: spam`).
- `invalid`: close invalid items (issues are closed as `not_planned`).
- `dirty`: close PRs with too many unrelated/unexpected changes (PR-only).
```

**Pattern**: Document automation trigger labels directly in AGENTS.md so agents use them instead of manual actions.

---

## Section 3: PR Quality Gates (Evidence-Based Merge)

> **Why this works**: prevents hallucinated bug fixes — a common failure mode where agents claim to fix bugs without verifiable evidence.

```markdown
## PR truthfulness and bug-fix validation

- Never merge a bug-fix PR based only on issue text, PR text, or AI rationale.
- Minimum merge gate for bug-fix PRs:
  1. symptom evidence (repro/log/failing test),
  2. verified root cause in code with file/line,
  3. fix touches the implicated code path,
  4. regression test (fail before/pass after) when feasible;
     if not feasible, include manual verification proof.
- If claim is unsubstantiated or likely hallucinated: do not merge.
  Request evidence/changes, or close when appropriate.
```

**Pattern**: Make the evidence bar explicit. Without this, agents will confidently merge fixes that "look right" but were never verified.

---

## Section 4: Shorthand Commands & Agent Vocabulary

> **Why this works**: reduces ambiguity by defining a shared vocabulary between human and agent.

```markdown
## Shorthand Commands

- `sync`: if working tree is dirty, commit all changes (pick a sensible
  Conventional Commit message), then `git pull --rebase`; if rebase conflicts
  and cannot resolve, stop; otherwise `git push`.

## Agent-Specific Notes

- Vocabulary: "makeup" = "mac app".
```

**Pattern**: Define project-specific shorthand so agents don't guess. Even one-word aliases prevent entire classes of miscommunication.

---

## Section 5: Multi-Agent Safety Rules

> **Why this works**: 7 specific rules that prevent parallel agents from corrupting each other's work — learned from real multi-agent collisions.

```markdown
- **Multi-agent safety:** do **not** create/apply/drop `git stash` entries
  unless explicitly requested. Assume other agents may be working.
- **Multi-agent safety:** when the user says "push", you may
  `git pull --rebase` to integrate latest changes (never discard other agents'
  work). When the user says "commit", scope to your changes only.
- **Multi-agent safety:** do **not** create/remove/modify `git worktree`
  checkouts unless explicitly requested.
- **Multi-agent safety:** do **not** switch branches / check out a different
  branch unless explicitly requested.
- **Multi-agent safety:** running multiple agents is OK as long as each agent
  has its own session.
- **Multi-agent safety:** when you see unrecognized files, keep going; focus
  on your changes and commit only those.
- **Multi-agent safety:** focus reports on your edits; avoid guard-rail
  disclaimers unless truly blocked; when multiple agents touch the same file,
  continue if safe.
```

**Pattern**: Prefix related rules with a bold category tag for scannability. Each rule addresses one specific collision vector.

---

## Section 6: Lint/Format Churn Resolution

> **Why this works**: prevents agents from stopping to ask about trivial formatting changes, which breaks flow in multi-agent setups.

```markdown
- Lint/format churn:
  - If staged+unstaged diffs are formatting-only, auto-resolve without asking.
  - If commit/push already requested, auto-stage and include formatting-only
    follow-ups in the same commit, no extra confirmation.
  - Only ask when changes are semantic (logic/data/behavior).
```

**Pattern**: Draw an explicit line between "auto-resolve" and "ask the human." Without this, agents interrupt for every whitespace diff.

---

## Section 7: Release & Version Guardrails

> **Why this works**: prevents agents from accidentally publishing or bumping versions without authorization.

```markdown
- Release guardrails: do not change version numbers without operator's
  explicit consent; always ask permission before running any npm
  publish/release step.
- Version locations: `package.json` (CLI), `build.gradle.kts` (Android),
  `Info.plist` (iOS/macOS), `docs/install/updating.md` (pinned version).
- "Bump version everywhere" means all version locations above except
  auto-generated files.
```

**Pattern**: Index where versions live so agents don't miss a location. Pair with an explicit consent gate for destructive publish actions.

---

## Section 8: Dependency & Tool Schema Guardrails

> **Why this works**: encodes project-specific anti-patterns that an agent wouldn't know without prior incident context.

```markdown
- Never update the Carbon dependency.
- Any dependency with `pnpm.patchedDependencies` must use an exact version
  (no `^`/`~`).
- Patching dependencies requires explicit approval; do not do this by default.
- Tool schema guardrails: avoid `Type.Union` in tool input schemas;
  no `anyOf`/`oneOf`/`allOf`. Use `stringEnum` for string lists.
- Bug investigations: read source code of relevant npm dependencies and all
  related local code before concluding.
```

**Pattern**: When you discover a footgun, add a one-line rule. Don't over-explain — the rule is "never do X" and optionally why.

---

## What Makes This File Effective

1. **Incident-driven** — most rules exist because something went wrong. The rules reference the specific failure mode, not abstract best practices.
2. **Multi-agent aware** — 7 explicit rules prevent parallel agent collisions on git state.
3. **Evidence-based merge gates** — prevents hallucinated bug fixes, a common AI failure mode.
4. **Operational, not just coding** — covers releases, security advisories, triage automation, and VM testing.
5. **Layered detail** — high-frequency rules are inline; detailed playbooks are referenced via docs or skills.
6. **Shorthand vocabulary** — reduces ambiguity with defined terms and command aliases.
7. **Auto-resolution boundaries** — explicitly separates "ask the human" from "just do it" (format churn vs. semantic changes).

---

## Adapting This for Your Project

1. **Start small** — add rules only when something goes wrong, not preemptively.
2. **Name the footgun** — "GitHub comment footgun: never use X" is more memorable than "use Y for GitHub comments."
3. **Add multi-agent rules early** — if you run 2+ agents, add the safety rules before the first collision, not after.
4. **Index version locations** — list every file where a version string lives; agents will miss locations you don't document.
5. **Define evidence gates** — if agents merge PRs, require explicit evidence (repro, root cause, test) before merge.
6. **Keep operational playbooks in docs/skills** — reference them from AGENTS.md but don't inline 50-line VM recipes.

Source: [openclaw/openclaw AGENTS.md](https://github.com/openclaw/openclaw/blob/main/AGENTS.md)
