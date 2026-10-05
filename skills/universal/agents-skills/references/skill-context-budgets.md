# Skill catalog context budgets

The portable bundle and the host's discovery controls are separate contracts. Budget sizes, caps, and setting names belong to each host and change between releases. Every numeric control below is a lookup: read the host's current skills and configuration docs before you change a value or quote a limit. The answer tells you how much headroom raising the budget gives before you have to trim descriptions or disable skills.

## Diagnose the affected layer

Count canonical bundles, installed/enabled skills, and entries actually shown to the model separately. Before pruning, look up whether the host has built-in skill diagnostics that report per-skill usage and listing or context cost. Claude Code documents a doctor-style report for this; check its skills docs for the current command. Prune from observed usage, not from guesses. Include system and plugin skills in the last two inventories. Successful loading does not prove a skill survived catalog truncation or was selected correctly.

Codex initially lists names, descriptions, and paths, shortening descriptions and potentially omitting entries when the catalog is too large. Selected skills still load their full bodies. Preserve useful body instructions. A generated graph is a navigation aid; it does not prevent the host from scanning installed bundles. [Codex skills](https://learn.chatgpt.com/docs/build-skills)

## Codex: supported first step

The catalog budget is a share of model context, adjustable with `skills.max_context_tokens`. Look up the default share and the maximum override in the Codex configuration reference. Merge the key into the existing user configuration; never replace other settings or create a duplicate table:

```toml
# ~/.codex/config.toml
[skills]
max_context_tokens = <value within the documented maximum>
```

For a temporary CLI trial, pass `-c skills.max_context_tokens=<value>` to the supported invocation. Back up configuration before persistence, parse the resulting TOML, and compare the parsed before/after objects. Roll back by restoring the previous value or removing only the newly added key. A larger catalog consumes more prompt space and may still truncate descriptions. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

Start a fresh session after configuration changes without interrupting ongoing sessions. Record the exact binary, model, skill/plugin inventory, warning, listed count, and description retention. Repeat on the desktop-bundled runtime if it differs from the CLI. A renderer diagnostic is narrower evidence than a fresh desktop session with all plugins.

Optional `agents/openai.yaml` controls UI, dependencies, and invocation policy. `policy.allow_implicit_invocation: false` preserves explicit invocation; do not blanket-change invocation semantics to resolve overflow. A smaller host installation is a separate design: account for sync scripts, drift validators, router-relative references, and deployment scripts that could repopulate it.

## Other hosts

| Host | Control and verification |
|------|--------------------------|
| Claude Code | The listing character budget is a share of the context window, plus a per-entry description cap; look up both defaults. Adjust `skillListingBudgetFraction` (budget) and `skillListingMaxDescChars` (per-entry cap), both documented in the [settings reference](https://code.claude.com/docs/en/settings-reference); use `skillOverrides: {"example": "name-only"}` to retain a name without its description. Inspect `/doctor` and `/context` for listing cost, and the skill-diagnostics report for per-skill usage; manage plugin skills through `/plugin`. |
| Grok Build CLI | Discovers `~/.agents/skills` as well as its own and Claude-compatible sources. `disable-model-invocation: true` makes a skill manual; `user-invocable: false` hides it from both user and model. `allowed-tools` does not grant or restrict tools. Do not transfer Claude meanings or Codex budget settings to Grok. |

These controls belong to the host, not to the Grok or Claude model itself. Preserve the common `SKILL.md` body and test each supported host separately. [Claude Code skills](https://code.claude.com/docs/en/skills), [Grok Build skills](https://docs.x.ai/build/features/skills-plugins-marketplaces)

## Acceptance evidence

- Static bundle validation passes and full canonical bodies remain intact.
- All intended installed skills load without new errors.
- Persistent configuration contains only the intended change.
- A fresh target-host session confirms whether the original warning is resolved; report partial retention or unavailable desktop evidence explicitly.
- Trigger, non-trigger, and explicit invocation checks cover any deliberate invocation changes. Catalog retention alone does not prove task quality.
