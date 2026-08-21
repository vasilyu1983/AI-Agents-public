# MCP Security Hardening Guide

Security guidance for MCP servers. The authorization requirements below were written against the **`2025-11-25`** specification and remain correct for servers on that version.

> **Current spec is `2026-07-28`** (shipped 2026-07-28). It adds authorization hardening on top of what follows: authorization servers **SHOULD** send the `iss` parameter per [RFC 9207](https://datatracker.ietf.org/doc/html/rfc9207) and clients **MUST** validate it against the recorded issuer before redeeming the code (SEP-2468); clients **MUST** key persisted credentials by issuer and re-register when the authorization server changes (SEP-2352); OAuth 2.0 Dynamic Client Registration (RFC 7591) is **deprecated** in favor of Client ID Metadata Documents. Verify against `modelcontextprotocol.io/specification/2026-07-28` when building new servers.

## Table of Contents

- [Security Baseline](#security-baseline)
- [Threat Model](#threat-model)
- [Authorization: What Changed](#authorization-what-changed)
- [Local vs Remote Security Model](#local-vs-remote-security-model)
- [Local `stdio`](#local-stdio)
- [Local HTTP](#local-http)
- [Remote HTTP](#remote-http)
- [Prompt Injection Defense](#prompt-injection-defense)
- [Tool Surface Design](#tool-surface-design)
- [Input Validation](#input-validation)
- [Token and Identity Rules](#token-and-identity-rules)
- [Elicitation and Human Approval](#elicitation-and-human-approval)
- [Secrets Management](#secrets-management)
- [Output Bounding](#output-bounding)
- [Logging and Audit](#logging-and-audit)
- [Safe HTTP Checklist](#safe-http-checklist)
- [Safe Filesystem Checklist](#safe-filesystem-checklist)
- [Safe Database Checklist](#safe-database-checklist)
- [Security Tests You Should Actually Run](#security-tests-you-should-actually-run)
- [Current Guidance Summary](#current-guidance-summary)

## Security Baseline

Assume all three are true:

1. Tool outputs may contain hostile instructions.
2. Clients will eventually connect the server to higher-value systems than you planned for.
3. Users will copy-paste sample code into real production paths.

That means security needs to live in the **server contract**, not only in client prompts.

## Threat Model

| Threat | Typical impact | Baseline mitigation |
|-------|----------------|--------------------|
| Prompt injection through tool outputs | Coerced tool use, exfiltration, policy bypass | Treat outputs as data, not instructions; use least privilege; require approval for writes |
| Argument injection (SQL/path/command) | Data loss, RCE, exfiltration | Strict schemas, parameterized queries, allowlists, path normalization |
| Over-broad tool surfaces | Silent privilege escalation | Split read/write tools; keep capabilities narrow |
| Weak local HTTP hardening | DNS rebinding / cross-origin abuse | Bind narrowly; validate Host and Origin |
| Mis-scoped tokens | Cross-server token misuse | Validate audience/resource and scopes |
| Massive outputs | Cost spikes, context collapse | Pagination, row limits, page sizes, truncation |

## Authorization: What Changed

The current MCP spec does **not** require authorization for every HTTP server.

- If your server does **not** need auth, you can run HTTP without implementing the MCP Authorization flow.
- If your server **does** support authorization over HTTP, it should follow the MCP Authorization specification.

Use authorization when the server is remote, shared, sensitive, or user/tenant-specific. Do not add auth “because HTTP exists”.

**When you do implement OAuth over HTTP, the `2025-11-25` spec makes these MANDATORY (not optional hardening) — they are the most commonly missed requirements:**

- **OAuth 2.1 + PKCE (S256).** Clients MUST implement PKCE and use S256 when capable; if the authorization server omits `code_challenge_methods_supported`, clients MUST refuse to proceed.
- **Resource Indicators (RFC 8707).** The `resource` parameter MUST be sent on **both** authorization and token requests, regardless of whether the AS appears to support it. This binds a token to one MCP server and is the primary defense against token reuse across servers.
- **Protected Resource Metadata (RFC 9728).** Servers MUST expose `/.well-known/oauth-protected-resource`, and MUST emit a `WWW-Authenticate` header on 401 pointing clients to it. Clients MUST support both the header and the well-known path.
- **Client ID Metadata Documents** are now the primary client-registration mechanism. Dynamic Client Registration (RFC 7591) is retained for backwards compatibility only and is explicitly deprecated in the `2026-07-28-RC`.
- **Audience/resource validation, fail-closed.** Validate the token audience against this server's identifier; reject tokens minted for a different resource. Never accept a token whose audience you did not verify.

Verify each against `modelcontextprotocol.io/specification/2025-11-25/basic/authorization` before shipping — these are hard requirements, and a server that skips RFC 8707 or the well-known endpoint is non-compliant even if it "works" against a lenient client.

## Local vs Remote Security Model

### Local `stdio`

This is the safest default for:

- local filesystem helpers,
- local database proxies,
- personal development tooling,
- anything that should live only inside one user session.

Primary controls:

- scoped env vars,
- narrow tool surface,
- bounded outputs,
- approval for writes.

### Local HTTP

Use only when you genuinely need HTTP semantics. If you do:

- bind to localhost unless remote access is required,
- validate `Host` and `Origin`,
- treat DNS rebinding as a real threat,
- avoid opening broad LAN-facing ports by default.

### Remote HTTP

For shared services:

- use TLS,
- add auth only when the server needs it,
- keep scopes narrow,
- log sensitive actions,
- enforce limits server-side rather than trusting the client.

## Prompt Injection Defense

Anything read through MCP can contain instructions aimed at the model. Common sources:

- GitHub issues
- tickets
- markdown docs
- chat transcripts
- web content
- CRM notes

Server guidance:

- return structured data where possible,
- isolate untrusted text fields,
- never give one tool both broad read access and dangerous write powers unless human approval exists,
- add server-side policy checks for destructive operations.

Example mental model:

```text
Untrusted content is evidence, not policy.
The model may summarize it, but the server should not rely on the model to enforce safety.
```

## Tool Surface Design

Good:

- `list_orders`
- `get_order`
- `cancel_order_with_reason`

Risky:

- `run_sql`
- `call_any_api`
- `execute_shell`

Design rules:

- separate read and write tools,
- prefer task-specific tools over generic interpreters,
- make dangerous actions explicit in the tool name and description,
- include “Use this when…” guidance in the description so clients route correctly.

## Input Validation

Every externally callable tool should enforce:

- strict schema validation,
- type-safe parsing,
- enum/allowlist checks where possible,
- normalized paths,
- parameterized SQL,
- bounded lists and pagination arguments,
- explicit defaults for limit, timeout, and sort order.

Reject:

- ambiguous date ranges,
- raw shell fragments,
- arbitrary filesystem paths,
- unconstrained search strings that can explode result size.

## Token and Identity Rules

If your server uses authorization:

- validate audience/resource on every token,
- validate scopes on every privileged action,
- map auth identity to the smallest server-side permission set,
- rotate refresh/access tokens according to your IdP policy,
- fail closed when identity checks are missing.

Do **not** pass MCP bearer tokens through to upstream APIs. The MCP token is for the MCP server boundary, not for every downstream dependency.

## Elicitation and Human Approval

Use **elicitation** when the server must ask the human for:

- confirmation before a destructive action,
- missing business data,
- URL-based auth handoff,
- sensitive scope expansion.

This is better than hoping the model asks nicely in natural language.

## Secrets Management

Use:

- environment variables,
- workload identity,
- cloud secret managers,
- vault-style secret injection.

Do not:

- commit secrets to config files,
- embed long-lived secrets in images,
- ask the model to discover secrets from disk,
- echo secrets in logs or tool output.

## Output Bounding

Every server should bound output at the source:

- max rows for database queries,
- max files per listing,
- page size for search APIs,
- truncation for logs,
- time-window limits for observability tools.

This reduces cost, improves latency, and prevents client context collapse.

## Logging and Audit

Log at least:

- tool name,
- timestamp,
- actor or tenant identity if applicable,
- high-level target object,
- outcome,
- latency,
- whether the action was read or write.

Avoid logging:

- secrets,
- full payloads containing sensitive PII,
- bearer tokens,
- raw untrusted content unless necessary for forensics.

## Safe HTTP Checklist

```text
[ ] HTTPS enabled for remote transport
[ ] Authorization implemented only if the server needs it
[ ] Token audience/resource validation enforced
[ ] Host and Origin validation enabled on local HTTP
[ ] Destructive tools require explicit approval
[ ] Output limits enforced at the server
[ ] Secrets injected at runtime
[ ] Structured logs exist for sensitive operations
[ ] Prompt-injection test cases included
```

## Safe Filesystem Checklist

```text
[ ] Allowed roots are explicit
[ ] Paths are normalized before access
[ ] `..` traversal blocked
[ ] Symlink behavior is explicit
[ ] Write and delete tools are separate from read tools
[ ] Sensitive patterns (.env, keys, SSH, cloud creds) are blocked
```

## Safe Database Checklist

```text
[ ] Read-only role by default
[ ] Parameterized queries only
[ ] Table/schema allowlists for sensitive environments
[ ] Row limits and statement timeouts enforced
[ ] Writes isolated behind narrowly named tools
[ ] DDL/admin operations never exposed casually
```

## Security Tests You Should Actually Run

- Prompt injection in issue/ticket/document text
- Path traversal attempts
- SQL injection and malformed filters
- Oversized result requests
- Cross-tenant or wrong-audience token attempts
- Missing approval on write tools
- Host/Origin failures for local HTTP

## Current Guidance Summary

- Auth is **optional** by protocol.
- Streamable HTTP is the preferred remote transport.
- Legacy SSE exists for compatibility, not as the new default.
- URL-based auth handoffs should use elicitation rather than improvised prompt instructions.
- The server must own safety-critical checks; the model is not the security boundary.
