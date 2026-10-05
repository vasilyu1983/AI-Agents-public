# Goose Approval Patterns and Distribution-Layer Controls

Moved from the former permissions and execution-sandbox skills. Cross-platform patterns for identity-aware and ACP-bridged approvals, build-time supply-chain gates, and distribution-baked allowlists.

## Approval Patterns (Goose)

Goose exposes two approval surfaces the current skill does not model: **identity-aware approvals via an OIDC proxy**, and **ACP-bridged approvals** where approvals must round-trip across a stdio boundary to a delegating agent.

### Identity-aware approvals (OIDC proxy)

Goose ships an `oidc-proxy/` crate that bridges agent calls to external providers through an OIDC-authenticated proxy. Approvals tied to external side-effects (deploy, merge, paid API use) can be gated on the authenticated identity, not just on "the user accepted a local prompt."

- **Pattern:** treat user identity as a permission-context field alongside mode and rule sources. Certain rule classes (destructive-on-prod, financial, third-party) can require fresh auth proof, not just a prior local allow.
- **Anti-pattern:** assuming the OS user running the CLI is the authorization principal for remote/side-effecting approvals. Shared dev machines, CI agents, and teammate-session handoff all break that assumption.
- **Recipe:** add an optional `auth_proof` field to the permission context; rules can declare `require_fresh_auth: true`. For those, every N minutes or per-call, the host demands re-authentication via OIDC proxy. Record the identity with the approval outcome for audit.

### ACP-bridged approvals

When a session delegates work to an external ACP agent (see `ai-coding-agents-surfaces` agent-delegating mode, and `ai-coding-agents-provider-runtime` agent-as-provider), tool approvals requested by the delegated agent must round-trip back to the orchestrator's local UI. The skill's current worker-routing model assumes same-process workers.

- **Pattern:** approvals raised by an ACP-delegated agent travel back through the ACP control channel, are materialized as a pending approval object in the orchestrator, rendered in the orchestrator's UI, resolved locally, and the outcome is sent back through ACP to the delegated agent. Stable request IDs are required end-to-end.
- **Anti-pattern:** auto-approving everything from a "trusted" delegated agent. ACP does not bound the delegated agent's tool use; without round-trip approval, the orchestrator loses audit and policy.
- **Recipe:** add a third routing leg in the permission-routing reference: **orchestrator ↔ ACP-delegated agent**. The delegated agent's approval requests are first-class runtime objects in the orchestrator's permission context, with stable IDs, cancellation support, and cross-process cancellation on session death.


## Build-Time and Distribution-Layer Controls (sandbox)

Runtime sandboxing leaves two gaps that some runtimes (Goose among them) close outside the sandbox: build-time supply-chain gates, and allowlists baked into the distribution.

### Build-time supply-chain gates

Sandboxing stops code from misbehaving at runtime. It does not stop a compromised dependency from shipping. A dependency gate such as cargo-deny (`deny.toml`) checks licenses, advisories, and source allowlists at build time, and a static check validates declarative artifacts (recipes, plugin manifests) before they enter the shipping artifact.

- **Pattern:** pair every runtime substrate control with a build-time gate. If a tool or extension should not be allowed at runtime, it also should not appear in the shipping artifact. The sandbox is the runtime enforcement; build-time gates are the artifact enforcement.
- **Anti-pattern:** relying solely on runtime sandboxing to contain shipped-but-disallowed code. An attacker who compromises the build pipeline bypasses the runtime check entirely.
- **Recipe:** include `deny.toml`-equivalent gates (license, advisory, source allowlist) for every language ecosystem your agent uses. Statically scan shipped YAML recipes and plugin manifests for declared tools that exceed the distribution's allowlist.

### Custom-distro preconfigured allowlists

Custom distributions (see the custom-distro section of `ai-coding-agents-settings-policy`) ship with a narrowed extension/tool/provider allowlist *baked into the binary*. The runtime sandbox then enforces a tighter envelope than the open-source stable.

- **Pattern:** treat distribution-layer allowlists as a sandbox policy layer above the user's own settings. Users cannot broaden beyond what the distro allows; they can only narrow within it.
- **Anti-pattern:** ship the open-source binary to enterprise customers with a "policy file" they must install separately. Separation between binary and policy creates drift, stale-policy risk, and bypass-by-rename attacks.
- **Recipe:** add `distro_envelope: Option<ExtensionAllowlist>` as an immutable field in the merged settings source. The sandbox enforces it at execution time; the settings layer shows it as a read-only source (see `ai-coding-agents-settings-policy`).

