# Declarative Command Artifacts and Judgment Calls

Moved from the former command-runtime skill. The main SKILL.md carries the rules; this file carries the deeper patterns and the trade-off calls.

## Declarative Command Artifacts

Some runtimes (Goose recipes are one example) ship commands as **declarative artifacts**: serialized, parameterized workflows with their own dependency manifest. This is a distinct point in the design space from frontmatter-plus-prompt slash commands.

### Recipes as typed, portable commands

Such an artifact carries metadata, instructions, typed parameters (each with a key, type, requirement, and default), and its required extensions; read the runtime's current schema for the exact field names. The "command" is a versioned artifact that travels between machines with its dependencies stated.

- **Pattern:** for commands that encode reusable workflows, prefer a declarative artifact over a live registry entry. Parameters are typed, extension dependencies are pinned, and the artifact can be statically validated before being added to the registry.
- **Anti-pattern:** encoding complex workflow commands as free-form prompt text with implicit argument conventions. That blocks validation, sharing, and portability across agents and machines.
- **Recipe:** extend the typed command contract with an optional `artifact_ref` variant — the command is a reference to a recipe-style artifact. Discovery reads the artifact; validation happens at registration, not execution.

### Declared-extension commands

A declarative artifact lists its required extensions. The command cannot run if they are absent — this is an install/activation check, not a runtime tool-call failure.

- **Pattern:** commands that depend on particular tools, MCP servers, or skills should declare those dependencies in the command definition. The registry verifies dependencies at load time and surfaces unavailable commands with an actionable error (install X), not a silent "no-op."
- **Anti-pattern:** commands that hard-code `require_tool("github.pr_create")` inside their body and discover unavailability only mid-execution.
- **Recipe:** add `requires_extensions: Vec<ExtensionRef>` to the command type. Unavailable-dependency state is a first-class command availability class (beside auth-gated and feature-gated).

## Judgment Calls

These are the calls a non-expert gets wrong even after reading the patterns above, because the patterns describe *what* to build, not *when the trade-off actually bites*.

- **Bridge-safe filtering is a trust-boundary control, not a UX nicety.** A remote or mobile client that can invoke a `local-jsx` command is, in effect, being handed a slice of local code execution surface — Ink rendering, filesystem side effects, terminal-only state mutation — from a network hop away. Model the remote-safe/bridge-safe allowlist as a security boundary with the same rigor as a permission gate, not as "which commands happen to render okay on a small screen." If a command's safety depends on "the bridge client will just not send that," you have not actually gated it.
- **Precedence order is a security decision before it is a UX decision.** Write the policy per source pair, not as one global "higher trust always wins" rule. Deliberate user or project overrides of a built-in are allowed, because replacing a bundled command is a documented customization path, but they are shown, never silent. A namespaced plugin entry (`plugin:name`) never shadows an un-namespaced name. A lower-trust source (a freshly installed plugin) never silently shadows a safety-relevant command. Record every shadowing event (the name, the winning and losing sources) and show it in help output and load telemetry. "Last loaded wins" is never acceptable, because the winner then changes with load timing.
- **Context and tool inheritance are separate axes.** Claude Code's documented conversation fork inherits parent history, system prompt, tools, and model; named subagents start from their own definitions. Other runtimes may define “fork” differently. Record the effective context source and tool set at dispatch, narrow tools when the host permits it, and do not infer either axis from the command label.
- **Know when the full typed registry is overkill.** A CLI with under ~10 static commands and no plugin, skill, or remote-client story does not need source tags, availability-vs-enablement separation, or a memoization-invalidation contract — a flat match statement is more honest about the system's actual complexity and easier to audit. Reach for the full contract in this skill when you have at least two of: multiple command sources that load independently, a remote or bridge client, or model-invocable (prompt-type) commands. Building the full registry contract for a single-source, terminal-only tool is the over-engineering failure mode of this skill, and it is at least as common as the under-engineering failure modes listed above.
- **`isEnabled()` staleness is worse than a missing command.** A command that silently disappears because a feature flag flipped is confusing but recoverable — the user tries again later. A command that appears available, is dispatched, and then fails mid-execution because `isEnabled()` was stale at menu-render time but re-checked at dispatch time is a worse experience. If you cannot guarantee the enablement check is consistent between "shown in the menu" and "actually dispatched," fail closed at dispatch and surface why, rather than trusting the menu-time snapshot.

