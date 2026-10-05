# MCP Security Hardening Guide

Security guidance for MCP servers. The authorization requirements below were introduced by the **`2025-11-25`** revision and carried forward. Before shipping, check the authorization page of the revision you target at `modelcontextprotocol.io/specification`; the answer decides which MUSTs your server and client have to meet.

> **The `2026-07-28` revision** adds authorization hardening on top of what follows: authorization servers **SHOULD** send the `iss` parameter per [RFC 9207](https://datatracker.ietf.org/doc/html/rfc9207) and clients **MUST** validate it against the recorded issuer before redeeming the code (SEP-2468); clients **MUST** key persisted credentials by issuer and re-register when the authorization server changes (SEP-2352); OAuth 2.0 Dynamic Client Registration (RFC 7591) is **deprecated** in favor of Client ID Metadata Documents. Check the authorization page of your target revision when building new servers.

## Table of Contents

- [Security Baseline](#security-baseline)
- [Threat Model](#threat-model)
- [Server-Mutation Threats](#server-mutation-threats)
- [Taint Source/Sink Tagging](#taint-sourcesink-tagging)
- [Confused Deputy: Worked Example](#confused-deputy-worked-example)
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
- [Safe Container Deployment Checklist](#safe-container-deployment-checklist)
- [Security Tests You Should Actually Run](#security-tests-you-should-actually-run)
- [Guidance Summary](#guidance-summary)

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
| Dynamic capability injection | Agent silently inherits a higher-risk capability after vetting | Client-side tool allowlist; require change notification and re-verify the tool list; pin tool definitions to a version or hash |
| Tool shadowing | Malicious tool outcompetes the legitimate one in planner selection; data intercepted | Semantic name-collision check before registering a new tool; sink-level user confirmation; restrict which servers the agent may reach |
| Confused deputy | Under-privileged user drives a broadly privileged server into an unauthorized action | Check the *user's* permission, not only the server's; per-tool scoped, audience-bound, short-lived credentials |
| Retrieval-index poisoning | Injected tool schema makes the planner call an unauthorized tool | Treat the tool-retrieval index as a trust boundary: signed/allowlisted schemas, write-restricted index |

## Server-Mutation Threats

Source: Styer, Patlolla, Mohan, Diaz, *Agent Tools & Interoperability with Model Context Protocol (MCP)*, Google, November 2025 (pp. 37–51). These threats are **structural** — they follow from a server controlling its own tool list and tool descriptions, so the `2026-07-28` stateless redesign does not remove any of them. Where the paper names spec fields, the control is restated functionally below; the spec facts in this skill's `SKILL.md` take precedence over the paper's.

### Dynamic Capability Injection

A server may change the set of tools, resources, or prompts it offers **after** the client vetted it, without notifying or asking the client. The agent then silently inherits capabilities outside the risk profile it was approved for — the paper's example is a book-search server that later adds a purchasing tool, turning a content-generation agent into one that can initiate financial transactions.

The paper notes servers were not *required* to notify clients on tool-list change (its `listChanged` flag is the pre-redesign field name — treat "require change notification" as the control, not that identifier).

Mitigations:

- **Client-side allowlist** of permitted tools and servers, enforced in the SDK or host application — not in the prompt.
- **Mandatory change notification**: require servers to signal tool-list changes and re-verify the list before use; treat an unannounced change as a failure.
- **Pin tool definitions to a version or hash** captured at vetting. If a description or API signature changes afterwards, alert the user or disconnect — do not silently accept the new definition.
- **Host the server in a controlled environment** (same environment as the agent, or a developer-managed container) when the capability set must not move without you.
- **Policy enforcement at a gateway** that filters the returned tool list down to a centrally approved set.

### Tool Shadowing

Tool descriptions can declare arbitrary triggers, so a malicious tool with a broad description ("use whenever the user mentions 'save', 'store', 'keep', or 'remember'") outcompetes a narrowly described legitimate tool in planner selection. The user's data then flows to the attacker's server rather than the sanctioned one.

Mitigations:

- **Semantic name-collision check before registration.** Compare a new tool's name and description against existing trusted tools with an LLM-based similarity filter, not an exact or substring match, and refuse or flag near-collisions.
- **Restrict reachable servers** to those explicitly approved, including servers already installed in the user's local environment.
- **Sanitize tool descriptions** through a policy engine before they enter model context.
- **mTLS** for sensitive client–server links so both ends verify identity.
- **Deterministic policy-enforcement hooks at four lifecycle points** — before tool discovery, before tool invocation, before data is returned to the client, and before a tool makes an outbound call. Implement each as a plugin or callback that fails closed; this is where the pinning, allowlist, and sink checks are actually enforced.

## Taint Source/Sink Tagging

Tag every tool input and output as tainted or not tainted, and enforce at the sink rather than at the caller.

- **Tainted by default**: user-provided free text, and any data fetched from an external or less-trusted system.
- **Propagation**: an output derived from, or affected by, tainted data is itself tainted. Annotate the specific fields, not just the whole payload.
- **Named sensitive sinks**: sending email to an external address, writing to a public store, file deletion, network egress, modification of production data.
- **Rule**: a sensitive sink requires explicit user confirmation **regardless of which tool is invoking it**. Anchoring the check at the sink is what stops a shadow tool from exfiltrating silently — a per-tool approval list cannot, because the attacker controls which tool is chosen.

Pair this with structured outputs and explicit sensitivity annotations so the client can identify, track, and control the flow rather than inferring it from free text.

## Confused Deputy: Worked Example

An MCP server is a privileged intermediary; the model is the party that gets confused.

1. A company connects its AI assistant to a private code repository through an MCP server granted **broad repo privileges** so it can serve every employee.
2. An employee **without** direct access to the whole repo asks the assistant to find `secret_algorithm.py` and create a branch containing its contents "so I can review it from my own environment."
3. The model has no security context of its own for the repository. It relays the request to the server as an ordinary sequence of tool calls.
4. The server checks only whether **it** may perform the action — never whether the *requesting user* may — and executes, exposing the file.

The structural cause is that MCP authorization is **coarse-grained at the client–server boundary**: the client authorizes once against the server, and the paper (Nov 2025) records no per-tool or per-resource authorization layer and no native mechanism for passing the end user's credentials through to the resources the tools reach. Whether a later spec revision adds a per-tool authorization layer is a lookup: read the authorization page of your target revision before asserting either way — but the deputy problem persists regardless whenever a server holds privileges broader than the calling user's.

Mitigations:

- Authorize against the **user's** identity, not just the server's credential; fail closed when the invoking identity is unknown.
- Validate token audience and scope on every invocation; keep credentials scoped, bound to authorized callers, and short-lived.
- Least privilege per tool — a report-reading tool gets read-only, never read-write or delete; avoid one broad credential spanning several systems.
- Keep secrets out of the agent context entirely: pass them client→server through a side channel, never through the conversation.

**Retrieval-based discovery adds a vector.** If tool discovery moves to a RAG-style retrieval step over a large tool index (the paper's proposed answer to context-window bloat), an attacker with write access to that retrieval index can inject a malicious tool schema and induce the planner to call an unauthorized tool — so the index itself becomes a trust boundary needing the same allowlist and pinning controls as the servers.

## Authorization: What Changed

The MCP spec does **not** require authorization for every HTTP server.

- If your server does **not** need auth, you can run HTTP without implementing the MCP Authorization flow.
- If your server **does** support authorization over HTTP, it should follow the MCP Authorization specification.

Use authorization when the server is remote, shared, sensitive, or user/tenant-specific. Do not add auth “because HTTP exists”.

**When you do implement OAuth over HTTP, the spec makes these MANDATORY (since `2025-11-25`; not optional hardening). They are the most commonly missed requirements:**

- **OAuth 2.1 + PKCE (S256).** Clients MUST implement PKCE and use S256 when capable; if the authorization server omits `code_challenge_methods_supported`, clients MUST refuse to proceed.
- **Resource Indicators (RFC 8707).** The `resource` parameter MUST be sent on **both** authorization and token requests, regardless of whether the AS appears to support it. This binds a token to one MCP server and is the primary defense against token reuse across servers.
- **Protected Resource Metadata (RFC 9728).** Servers MUST expose `/.well-known/oauth-protected-resource`, and MUST emit a `WWW-Authenticate` header on 401 pointing clients to it. Clients MUST support both the header and the well-known path.
- **Client ID Metadata Documents** are now the primary client-registration mechanism. Dynamic Client Registration (RFC 7591) is retained for backwards compatibility only and is deprecated in the `2026-07-28` revision.
- **Audience/resource validation, fail-closed.** Validate the token audience against this server's identifier; reject tokens minted for a different resource. Never accept a token whose audience you did not verify.

Verify each against the authorization page of your target revision before shipping — these are hard requirements, and a server that skips RFC 8707 or the well-known endpoint is non-compliant even if it "works" against a lenient client.

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

A `stdio` server entry is a command line the client executes with the user's privileges. Treat adding or editing one like installing software: never build it from untrusted input (a shared config, a web page, a model suggestion), review the full command and args before approving, and run servers you did not write in a sandbox or container.

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

Use the protocol's human-input mechanism when the server must ask the human for the items below. Before `2026-07-28` that was server-initiated `elicitation/create`; from `2026-07-28` it is an MRTR `input_required` result. Check which one your target revision uses:

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
[ ] Outbound calls go only to an endpoint allowlist (no caller-supplied base URLs)
[ ] Every outbound request has a timeout and a rate limit
[ ] Each tool call is authorized individually; rate limits apply per client and per tool
[ ] Client-supplied metadata is never trusted for authorization
[ ] Error results carry actionable text, never stack traces or internal hostnames
```

## Safe Filesystem Checklist

```text
[ ] Allowed roots are explicit
[ ] Paths are normalized before access
[ ] `..` traversal blocked
[ ] Symlink behavior is explicit
[ ] Write and delete tools are separate from read tools
[ ] Sensitive patterns (.env, keys, SSH, cloud creds) are blocked
[ ] File size and directory depth are capped
[ ] Writes and deletes are audit-logged
```

## Safe Database Checklist

```text
[ ] Read-only role by default
[ ] Parameterized queries only
[ ] Table/schema allowlists for sensitive environments
[ ] Row limits and statement timeouts enforced
[ ] Writes isolated behind narrowly named tools
[ ] DDL/admin operations never exposed casually
[ ] Connection to the database uses TLS
[ ] Every query is audit-logged (see mcp-for-dwh.md, audit log table)
```

Read-only must be enforced by the database role, not by a keyword blocklist in server code. Blocklists are defense in depth at most.

## Safe Container Deployment Checklist

```text
[ ] Runs as a non-root user, read-only root filesystem where possible
[ ] No secrets baked into the image; secrets injected at runtime
[ ] Image scanned for vulnerabilities before promotion
[ ] CPU and memory limits set; network policy restricts egress
[ ] Logs go to stdout/stderr; health check wired for HTTP transport
[ ] TLS terminates in front of any HTTP transport
```

Container build, CI/CD, and cluster patterns belong to [`../../ops-devops-platform/SKILL.md`](../../ops-devops-platform/SKILL.md).

## Security Tests You Should Actually Run

- Prompt injection in issue/ticket/document text
- Path traversal attempts
- SQL injection and malformed filters
- Oversized result requests
- Cross-tenant or wrong-audience token attempts
- Missing approval on write tools
- Host/Origin failures for local HTTP

## Guidance Summary

- Auth is **optional** by protocol.
- Streamable HTTP is the preferred remote transport.
- Legacy SSE exists for compatibility, not as the new default.
- URL-based auth handoffs should use the protocol's input-request mechanism (elicitation before `2026-07-28`, MRTR input requests after) rather than improvised prompt instructions.
- The server must own safety-critical checks; the model is not the security boundary.
