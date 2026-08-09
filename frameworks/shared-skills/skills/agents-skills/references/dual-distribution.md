# Dual-Distribution Pattern

How to ship one skill source to two (or more) runtimes without drift. Pattern observed in [`anthropics/financial-services`](https://github.com/anthropics/financial-services); recorded here as portable guidance.

## Problem

A skill that lives only in `frameworks/shared-skills/skills/<skill>/` works for local agent runtimes (Claude Code, Codex via OpenClaw). But that's only one delivery channel. The same skill content might also need to ship as:

- A Cowork plugin for non-developer operators
- A Managed Agents API template deployed via `/v1/agents` to a customer tenant
- A partner-bundled plugin a third party installs in their own runtime
- A SaaS product where the skill is the system prompt behind an HTTP endpoint

The naive answer — copy the skill into each target — guarantees drift. Six months in, every channel ships a different version, and no one can tell which is canonical.

## Pattern

**One canonical source, many wrappers, drift caught by tooling.**

```
canonical/
  agents/<slug>.md             ← THE system prompt (one file, single source of truth)
  skills/                      ← shared skill bundles
    <skill>/SKILL.md
    <skill>/references/...

distributions/
  plugin/<slug>/
    .plugin/plugin.json        ← references agents/<slug>.md via system.file
    skills/                    ← bundled COPIES, kept in sync by script
  managed-agent/<slug>/
    agent.yaml                 ← references agents/<slug>.md via system.file
    subagents/*.yaml
    steering-examples.json
    README.md                  ← security tier + handoff notes
  partner-bundle/<slug>/
    ... whatever the partner runtime expects ...

scripts/
  sync.sh                      ← propagates canonical → distributions
  check.sh                     ← lints all manifests, fails on drift
```

## Three Disciplines

### 1. One canonical artifact, never two

The system prompt lives in exactly one file. Every distribution **references** that file rather than copying its content into a YAML or JSON manifest. If a distribution format insists on inlined content (some plugin manifests do), the sync script copies from canonical at build time — never hand-edited in the distribution.

### 2. Manifest fields point at canonical paths

Each wrapper's manifest carries a `system.file` or equivalent field that points back to the canonical source:

```yaml
# managed-agent agent.yaml
system:
  file: ../../canonical/agents/kyc-screener.md   # not inline content
skills:
  - path: ../../canonical/skills/kyc-screener-rules
  - path: ../../canonical/skills/sanctions-list
```

A manifest with inlined system-prompt content is an anti-pattern in this model — it cannot be auto-synced.

### 3. Drift detection runs in CI / pre-commit

A `check.sh` lints every manifest and either:

- Verifies every `system.file` / `skills.path` reference resolves to a real canonical file
- Diffs every bundled-copy distribution against its canonical source and **fails if drift detected**

If drift is detected, the sync script (not a human editor) fixes it by overwriting the bundled copy from canonical. Humans only edit canonical.

## When to Adopt

- You ship the same skill to **two or more distinct runtime targets** with non-trivial wrapper formats
- A drift between targets would produce observable behavior differences (different system prompts → different model behavior)
- You have or can create a single CI/pre-commit gate that runs the drift check

If you only ship to one target, this pattern is overkill. If you ship to two but the wrappers are nearly identical, a simple symlink topology (as in this repo for `~/.claude/skills/` and `~/.agents/skills/`) is enough.

## What NOT to Do

- **Hand-edit the bundled copies.** Anything in a distribution directory must be reproducible from canonical + sync. If you hand-edit, drift is silent.
- **Inline the system prompt in a YAML manifest.** The manifest references the source file. YAML quoting will eat your formatting eventually.
- **Skip the check gate.** Without enforcement, the discipline collapses within weeks. The check must be cheap enough that nobody disables it.

## Reference Implementation

[`anthropics/financial-services`](https://github.com/anthropics/financial-services) ships every named agent (KYC Screener, GL Reconciler, Pitch Agent, etc.) as both a Cowork plugin and a Managed Agents cookbook. Their `scripts/check.py` lints manifests and detects drift; their `scripts/sync-agent-skills.py` propagates canonical → bundles. See their `CLAUDE.md` for the full layout.

For this repo, the analogous pattern is the symlink topology: canonical at `frameworks/shared-skills/skills/`, surfaces at `~/.claude/skills/` and `~/.agents/skills/`, drift detection via `framework-alignment/scripts/check_symlink_drift.sh`.

## See Also

- `agents-skills/SKILL.md` — skill spec and portable contract
- `framework-alignment/scripts/check_symlink_drift.sh` — symlink drift detector for this repo
- `ai-coding-agents-release-distribution` — release/distribution mechanics across runtimes
- `ai-coding-agents-plugins` — plugin manifest formats
