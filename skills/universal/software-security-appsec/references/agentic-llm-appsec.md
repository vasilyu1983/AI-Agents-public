# Agentic and LLM AppSec (Design Side)

## Table of Contents

- [1. Core Design Rule: Separate Dangerous Capability Combinations](#1-core-design-rule-separate-dangerous-capability-combinations)
- [2. Threat → Control Map](#2-threat--control-map)
- [3. MCP and Tool-Server Trust](#3-mcp-and-tool-server-trust)
- [4. Tool-Argument Validation Pattern](#4-tool-argument-validation-pattern)
- [5. Approval Design](#5-approval-design)
- [6. When NOT to Over-Engineer](#6-when-not-to-over-engineer)
- [Related](#related)

Design-time threat-to-control guidance for LLM features, tool-calling agents, and MCP-connected applications. This file owns **design decisions**. Test coverage, scanners, and red-team harnesses for the same risks live in [qa-security-testing/references/owasp-top-10-coverage.md](../../qa-security-testing/references/owasp-top-10-coverage.md); do not duplicate its tables here.

Lists referenced (published by the OWASP GenAI Security Project, genai.owasp.org):

- **OWASP Top 10 for LLM Applications 2025**: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM03 Supply Chain, LLM04 Data and Model Poisoning, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08 Vector and Embedding Weaknesses, LLM09 Misinformation, LLM10 Unbounded Consumption.
- **OWASP Top 10 for Agentic Applications for 2026**: ASI01 Agent Goal Hijack, ASI02 Tool Misuse, ASI03 Identity & Privilege Abuse, ASI04 Agentic Supply Chain Vulnerabilities, ASI05 Unexpected Code Execution, ASI06 Memory & Context Poisoning, ASI07 Insecure Inter-Agent Communication, ASI08 Cascading Failures, ASI09 Human-Agent Trust Exploitation, ASI10 Rogue Agents.

Both lists change between editions. Re-check names and IDs before quoting them in a deliverable.

---

## 1. Core Design Rule: Separate Dangerous Capability Combinations

Prompt injection (LLM01, ASI01) has no reliable input filter. Design so that a successful injection cannot reach a damaging outcome.

A single model context must not combine all three of:

1. **Untrusted content** (web pages, emails, tickets, retrieved documents, tool output, other agents' messages)
2. **Access to private data** (tenant documents, credentials, PII, internal APIs)
3. **An exfiltration or mutation channel** (outbound HTTP, email/send, write APIs, code execution with network egress, rendering attacker-controlled URLs/images)

This is often called the "lethal trifecta" (Simon Willison). When a feature needs all three, split it:

| Pattern | How it breaks the combination |
|---|---|
| Quarantined reader | A model that reads untrusted content has no tools and returns only structured, schema-validated fields to the privileged planner |
| Plan-then-execute | The privileged plan is fixed before untrusted content is read; later content cannot add tool calls |
| Egress allowlist | Code-exec and fetch tools can reach only named hosts; block arbitrary URLs, DNS exfil, and markdown image beacons in rendered output |
| Human approval for the third leg | Mutations or sends require explicit, specific confirmation (see §5) |

---

## 2. Threat → Control Map

| Threat (list IDs) | Design control | Verify with |
|---|---|---|
| Prompt / goal injection (LLM01, ASI01) | Treat every non-system token as data; capability separation (§1); fixed goal/plan invariants checked before each mutating call | qa-security-testing adversarial suite |
| Excessive agency / tool misuse (LLM06, ASI02) | Least-privilege tool set per task; separate read-only and mutating tools (different servers or namespaces); JSON-schema validation of every tool argument **server-side**; allowlists for paths, hosts, SQL verbs | Tests that out-of-scope arguments are rejected by the tool, not the prompt |
| Identity and privilege abuse (ASI03) | On-behalf-of tokens narrowed to the user, tenant, and task; short TTL; never pass the agent's service credential to a tool acting for a user; authorization enforced by the downstream API, not the model | Confused-deputy tests: user A's session cannot reach tenant B via the agent |
| Supply chain (LLM03, ASI04) | Pin MCP servers, tool plugins, and model artifacts by version/digest; review tool descriptions as code (they are prompt input); provenance for model and plugin packages | SCA + provenance checks (qa-security-testing) |
| Unexpected code execution (ASI05) | Sandbox (container/microVM, seccomp, no host mounts); no default network egress; CPU/memory/time limits; ephemeral filesystem | Sandbox-escape and egress tests |
| Memory / context / RAG poisoning (LLM04, LLM08, ASI06) | Provenance tag on every memory and vector entry (source, tenant, author); tenant filter enforced in the retrieval query, not post-filtered by the model; writes to long-term memory from untrusted content require review | Cross-tenant retrieval tests |
| Improper output handling (LLM05) | Model output is untrusted input to the next sink: encode for HTML, parameterize SQL, never `eval`/shell it; strip or proxy URLs before rendering | Standard injection tests on output paths |
| Sensitive info / system prompt leakage (LLM02, LLM07) | Keep secrets and authorization logic out of prompts; assume the system prompt is public; redact PII before logging completions | Extraction probes |
| Inter-agent trust (ASI07) and cascading failures (ASI08) | Messages between agents are untrusted data with a schema; authenticate agent identities; bulkheads and circuit breakers between stages | Fault-injection between agent stages |
| Human-agent trust exploitation (ASI09) | Approval UI shows the concrete action, target, and diff, not the model's summary of it | UX review of approval prompts |
| Rogue agents / unbounded consumption (ASI10, LLM10) | Spawn-depth, lifetime, token, and spend limits; kill switch; per-tenant quotas | Limit and termination tests |

---

## 3. MCP and Tool-Server Trust

- Treat each MCP server as a third-party dependency: pin the version or digest, record the owner, and review changes to tool names and descriptions (a changed description can change agent behavior).
- Prefer remote servers that authenticate the **user** (delegated OAuth with narrow scopes) over servers holding a shared, broad service credential.
- Do not let one server's tool output instruct the agent to call another server's tools without passing back through policy checks.
- Scope servers per tenant where the data is tenant-scoped; a cross-tenant mutation server is over-broad by default.
- Log per call: user, tenant, tool, arguments hash, decision (allowed/denied/approved), and result status.

---

## 4. Tool-Argument Validation Pattern

Validate in the tool implementation, not in the prompt:

```python
from pydantic import BaseModel, Field, field_validator

ALLOWED_HOSTS = {"api.internal.example", "docs.example.com"}

class FetchArgs(BaseModel):
    url: str = Field(max_length=2048)

    @field_validator("url")
    @classmethod
    def host_allowed(cls, v: str) -> str:
        from urllib.parse import urlsplit
        u = urlsplit(v)
        if (u.scheme != "https" or u.hostname not in ALLOWED_HOSTS
                or u.username or u.password or u.port not in (None, 443)):
            raise ValueError("host not allowlisted")
        return v

def fetch_tool(raw_args: dict, ctx) -> dict:
    args = FetchArgs.model_validate(raw_args)   # rejects before any I/O
    ctx.authorize("fetch", args.url)            # server-side policy, per user/tenant
    # Custom transport contract; do not replace with a default redirect-following client.
    return ctx.safe_fetch_https(args.url, timeout=10)
```

`safe_fetch_https` must resolve the host and apply its host-specific address policy
before connecting, pin the approved address for that connection while preserving
hostname-based TLS verification, and disable automatic redirects. If redirects
are required, validate and authorize every hop and its resolved address before
following it; reject unapproved schemes, hosts, ports, and addresses. An initial
URL allowlist check alone does not constrain a redirect or DNS rebinding.
See [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) for the redirect and address-validation boundaries.

---

## 5. Approval Design

- Gate by **consequence**, not by tool name: irreversible, externally visible, costly, or cross-tenant actions need approval.
- Show the exact action (target, amount, recipients, diff). Avoid "Approve all" and session-wide blanket consent.
- Re-check authorization and quota immediately before each metered call (see the metered-action rule in SKILL.md).
- Approval must be bound to the specific call (hash of tool + arguments); a changed argument invalidates it.

---

## 6. When NOT to Over-Engineer

- A read-only assistant over public docs with no private data and no egress does not need the full split in §1; standard output encoding and rate limits suffice.
- Do not rely on "prompt-injection detector" models as the primary control; use them as telemetry.

---

## Related

- Testing and coverage tables: [qa-security-testing](../../qa-security-testing/SKILL.md)
- Agent architecture and guardrails: [ai-agents](../../ai-agents/SKILL.md)
- MCP server design: [agents-mcp](../../agents-mcp/SKILL.md)
