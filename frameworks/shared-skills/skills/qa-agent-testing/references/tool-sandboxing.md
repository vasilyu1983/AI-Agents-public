# Tool Sandboxing for Agent Testing

Isolation strategies for secure evaluation of agents with tool access, including MCP-style tools.

## Contents

- [Why Sandboxing Matters](#why-sandboxing-matters)
- [Tiered Strategy](#tiered-strategy)
- [Reference Implementations](#reference-implementations)
- [MCP and Tool Security Checks](#mcp-and-tool-security-checks)
- [Checklist](#checklist)

## Why Sandboxing Matters

Tool-using agents can:

- Execute code
- Read and write files
- Call external APIs
- Cross approval boundaries if tools are too permissive
- Leak secrets through tool outputs or arguments

Treat tool outputs, retrieved content, and tool metadata as untrusted input.

## Tiered Strategy

| Tier | Data Access | Network | Use Case |
|---|---|---|---|
| Tier 1 | Synthetic or mocked only | None | Unit tests and deterministic tool grading |
| Tier 2 | Sanitized fixtures or narrow staging data | Allowlist only | Integration tests |
| Tier 3 | Production-like staging | Monitored | Pre-release validation |
| Tier 4 | Live production | Explicit approvals and audit logging | Canary or live evals |

## Reference Implementations

### UK AISI Inspect

Use Inspect docs as the primary reference for isolated eval execution and sandbox design.

- Docs: `https://inspect.aisi.org.uk/`
- Sandboxing reference: `https://inspect.aisi.org.uk/sandboxing.html`
- Sandboxing Toolkit (open source): `https://github.com/UKGovernmentBEIS/aisi-sandboxing` — plugins for Docker, Kubernetes, Modal, Proxmox, and custom environments
- SandboxEscapeBench (unverified as of 2026-07-11: exact release date not independently confirmed, referenced elsewhere as ~March 2026): 18 container-escape scenarios spanning orchestration, runtime, and kernel layers; use to verify that agents cannot break out of their execution sandbox

### OpenAI Agent Safety Guidance

OpenAI’s current agent safety guidance is useful for approval and isolation patterns:

- Keep tool approvals enabled for MCP tools and risky side effects
- Use structured outputs and isolated execution to reduce prompt-injection risk
- Run trace graders and evals against tool behavior

Reference:

- `https://platform.openai.com/docs/guides/safety-best-practices#building-agents-safely`

### Runtime Isolation

Use a real sandbox runtime when possible:

- `gVisor` for lightweight workload isolation
- Container or VM isolation for stronger boundaries
- Ephemeral storage and deny-by-default egress where practical

## MCP and Tool Security Checks

The OWASP Agentic Top 10 (2026) classifies several of these as P0 risks: Tool Misuse & Exploitation (ASI02), Agent Identity & Privilege Abuse (ASI03), and Agentic Supply Chain Compromise (ASI04 — covers MCP tool verification and tool description poisoning).

Add explicit tests for:

- Malicious tool descriptions or tool docs (supply chain/description poisoning — ASI04)
- Tool-output poisoning
- Unsafe tool argument smuggling
- Secret exfiltration from env vars, files, or cached outputs
- Approval-boundary bypass attempts
- Cross-tool credential leakage
- Session-resume confusion for long-running agents
- MCP tool allowlist verification: only explicitly permitted tools should be callable

### Minimum hardening controls

- Tool allowlists
- Argument schema validation
- Deny-by-default network policy
- Ephemeral work directories where possible
- Resource limits and timeouts
- Audit logs for tool calls, approvals, retries, and side effects

## Checklist

- [ ] Tool calls run in an isolated environment or with equivalent hard boundaries
- [ ] Network access is deny-by-default or allowlisted
- [ ] Tool arguments are validated before execution
- [ ] Tool outputs are logged and treated as untrusted text
- [ ] Approval boundaries are tested explicitly
- [ ] Secrets cannot be read or exfiltrated through tool calls
- [ ] Resource limits and timeouts are enforced
- [ ] Canary or live evals require explicit auditability

## Related

- [SKILL.md](../SKILL.md) - main skill overview
- [prompt-injection-testing.md](prompt-injection-testing.md) - adversarial prompt and tool-output cases
- [regression-protocol.md](regression-protocol.md) - rerun and recovery workflow
