# OpenAI Codex Execpolicy and Network Proxy

Sources:
- OpenAI Codex repo, commit `9f42c89c0112771dc29100a6f3fc904049b2655f`
- `codex-rs/execpolicy/README.md`
- `codex-rs/network-proxy/src/config.rs`
- `codex-rs/network-proxy/src/connect_policy.rs`

Use this reference when designing allow/ask/deny rule engines, shell-prefix approvals, network sandbox policy, or policy explainability for coding-agent runtimes.

## Table of Contents

- [What To Steal](#what-to-steal)
- [Network Proxy Boundary](#network-proxy-boundary)
- [Portable Permission Contract](#portable-permission-contract)
- [Tests To Require](#tests-to-require)
- [Source Links](#source-links)

## What To Steal

### Prefix rules as executable policy

Codex has a policy language around prefix rules. A rule matches command prefixes and returns a decision with justification.

Reusable shape:

```text
prefix_rule(
  pattern,
  decision,
  justification,
  match?,
  not_match?
)
```

The important design choice is that policy is executable and testable, not a loose list of strings. Rules can be evaluated with structured output, and examples can be used as load-time tests.

Design rule:
- Store shell rules in a policy file or policy object.
- Evaluate command requests through the same engine every time.
- Emit machine-readable decision, matching rule, and justification.
- Treat policy examples as tests.

Known trap:
- Persisting raw command prefixes without a policy evaluator makes it hard to detect shadowed, unreachable, or overbroad approvals.

### Strictest decision wins

Codex's execpolicy docs describe a strictest-decision model. That is the right default when allow, ask, and deny rules overlap.

Recommended precedence:

1. deny
2. ask
3. allow

This prevents a broad allow from accidentally overriding a narrower deny.

Known trap:
- First-match-wins is easy to implement but fragile. Rule order becomes a hidden security boundary.

### Host executable helper

Codex includes a `host_executable` helper for matching the executable part of a command. Import the idea, but constrain it tightly.

Safe use:
- Match the canonical executable token after parsing.
- Avoid matching arbitrary substrings.
- Keep fallback basename matching explicit and explainable.

Known trap:
- A rule like "allow anything containing npm" is not equivalent to "allow host executable npm." String matching turns policy into guesswork.

## Network Proxy Boundary

Codex's network-proxy config separates network policy from tool approval. Useful patterns:

- Domain allow and deny lists.
- Deny precedence over allow.
- Local binding disabled by default.
- Loopback and non-public targets guarded when local binding is disabled.
- Unix socket permissions separated from domain policy.
- MITM hooks modeled as explicit proxy behavior, not hidden tool behavior.

This belongs with permissions because network reachability is a capability boundary, even when the shell command was approved.

Design rule:
- Approval to run a tool is not approval for arbitrary network egress.
- Network destination policy should be evaluated independently from command policy.
- Log blocked destination and policy source separately from shell approval state.

Known trap:
- Treating `network_access=true` as one global boolean loses the difference between "can fetch package registries" and "can connect to local services or private IPs."

## Portable Permission Contract

```text
PermissionDecision
  decision: allow | ask | deny
  source: managed | repo | user | session
  matched_rule_id
  justification
  normalized_command?
  network_destination?
  policy_layer
```

Policy load should fail or warn on:

- unreachable rules
- deny rules shadowed by broader allow rules if using first-match semantics
- broad shell prefixes without parsed executable anchors
- network allow lists without deny precedence
- local binding enabled without explicit user or org policy

## Tests To Require

- A narrower deny beats a broader allow.
- A narrower ask beats a broader allow.
- Rule examples pass at policy load time.
- Policy evaluation emits JSON or equivalent structured output.
- `host_executable` style matching does not match arbitrary substrings.
- Domain deny beats domain allow.
- Loopback/private targets are blocked when local binding is disabled.
- Network block is reported as network policy, not shell denial.

## Source Links

- [execpolicy README](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/execpolicy/README.md)
- [network proxy config](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/network-proxy/src/config.rs)
- [network connect policy](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/network-proxy/src/connect_policy.rs)
