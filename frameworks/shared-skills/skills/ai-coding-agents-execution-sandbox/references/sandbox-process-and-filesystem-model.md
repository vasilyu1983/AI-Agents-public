# Sandbox Process And Filesystem Model

Start by defining explicit execution modes rather than one vague “sandboxed” state.

Typical modes:

- **read-only**: inspect files and run safe commands without writes
- **workspace-write**: writes allowed only inside the active workspace or allowlisted roots
- **restricted-network**: workspace-write plus outbound network denied or narrowly scoped
- **unrestricted**: full local execution after explicit approval
- **worker-reduced**: child tasks inherit a narrower subset of the parent envelope

## Filesystem boundary rules

- Resolve symlinks before policy checks.
- Check both the target path and the effective working directory.
- Keep writable roots explicit.
- Treat temporary directories as separate policy objects, not as hidden global escape hatches.
- Do not assume shell glob expansion preserves safe path boundaries.

## Process model

- Classify commands by risk before execution.
- Keep interpreters and shells under the same policy system as direct binaries.
- Prefer a central command runner so policy checks, telemetry, and cancellation live in one place.
- Make background workers inherit a reduced envelope by default.

## Edge cases

- **Path traversal through symlinked workspace content**: resolve real paths before approval or execution.
- **Relative working-directory escapes**: a safe command in the wrong cwd can become unsafe.
- **Tool wrappers**: wrapper tools must not silently bypass the command policy path.
- **Shared temp directories**: if temp is writable, document whether it is trusted, isolated, or scrubbed.

## Practical tip

If your policy language cannot explain “why this command is safe here but unsafe there,” the filesystem model is still too implicit.

## Reference implementations to check before designing your own

Do not invent execution-mode names from scratch; two shipping runtimes already name them clearly and are worth copying the shape of:

- Claude Code's Bash sandbox distinguishes sandbox mode (auto-allow vs. regular permissions) from permission mode, and defaults writes to cwd + temp while defaulting reads much broader — an asymmetry that leaks credential files unless closed explicitly. See [`claude-code-bash-sandbox-mechanics.md`](claude-code-bash-sandbox-mechanics.md).
- Codex names three sandbox modes explicitly (`read-only`, `workspace-write`, `danger-full-access`) as an axis separate from approval policy (`untrusted`, `on-request`, `never`). See [`openai-codex-sandbox-guardrails-may-2026.md`](openai-codex-sandbox-guardrails-may-2026.md).

Both products also warn that the sandbox is scoped to specific tool classes (Bash for Claude Code; the exec surface for Codex) — file-edit, fetch, and computer-use tool calls are typically governed by the separate permission system, not the process sandbox. Verify this scope boundary explicitly for any runtime you are modeling; do not assume "sandboxed" is a whole-agent property.
