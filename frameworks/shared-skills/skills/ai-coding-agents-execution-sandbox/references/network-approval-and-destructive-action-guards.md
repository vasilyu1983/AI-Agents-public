# Network, Approval, And Destructive-Action Guards

Sandbox design fails when network and destructive actions are treated as afterthoughts.

## Network policy

Model outbound access explicitly:

- no network
- host allowlist
- package-manager exceptions
- unrestricted after approval

Do not bundle network access into the generic “dangerous command” bucket. Package install, API calls, git fetch, and browser verification often need different policies.

## Destructive-action classes

Create explicit classes for:

- file deletion
- force reset or checkout
- privileged execution
- branch or remote mutation
- workspace cleanup outside owned roots

Each class should map to either:

- deny
- allow in safe scope
- require approval

## Guard design rules

- Detect dangerous intent before the shell runs.
- Treat shell control operators, redirection, and nested execution carefully.
- Make policy outcomes explainable to the user and traceable in telemetry.
- Re-run failed-but-important actions with explicit escalation rather than silently weakening the sandbox.

## Edge cases

- **Destructive command through helper script**: classify the effective action, not just the wrapper name.
- **Network needed after sandbox failure**: escalation should be deliberate and visible, not an automatic fallback.
- **Background worker prompts**: if workers cannot surface approval, they need a safe escalation path back to the lead or UI.
- **Prefix approvals**: keep persistent command approvals narrow enough that they do not become an accidental escape hatch.

## Practical tip

Users trust a coding agent more when “denied,” “allowed,” and “needs approval” feel mechanically consistent. That consistency is a product feature, not just a security feature.

## TLS-blind allowlists are a real exfiltration path

A network policy that allows a domain by hostname but does not terminate or inspect TLS is a connectivity control, not a content-inspection boundary — a broad allowed host can be abused via domain fronting or similar techniques to reach a different destination behind the same front. Do not describe hostname-only allowlisting as "network isolation" without that caveat. If content inspection matters for the threat model, TLS termination at the proxy (with the sandbox trusting a proxy-issued CA) is a separate, opt-in control that most default sandbox proxies do not enable. See [`claude-code-bash-sandbox-mechanics.md`](claude-code-bash-sandbox-mechanics.md) for a concrete example of this tradeoff, including how credential masking depends on the same TLS-termination control.
