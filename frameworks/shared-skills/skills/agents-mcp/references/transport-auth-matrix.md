# MCP Transport × Auth Selection Matrix

Use this matrix to pick the right transport and auth combination before configuring or building an MCP server.

## Decision Matrix

| Scenario | Transport | Auth | Notes |
|----------|-----------|------|-------|
| Local process, single user, same machine | `stdio` | None | Fastest path. Process inherits shell env; no network exposure. |
| Local process, needs per-user isolation | `stdio` | None (env vars for secrets) | Pass credentials via env; never hard-code in config. |
| Self-hosted shared service, internal network | Streamable HTTP | API key (header) | `Authorization: Bearer <token>` or `X-API-Key`. Rotate keys; do not reuse session tokens. |
| Self-hosted shared service, multi-tenant | Streamable HTTP | OAuth 2.1 PKCE | Follow the MCP authorization spec. Use short-lived access tokens. |
| Third-party vendor-hosted server | Streamable HTTP | OAuth 2.1 (vendor flow) | Vendor controls token issuance. Inspect scopes before accepting. |
| Browser-facing client, public internet | Streamable HTTP | OAuth 2.1 PKCE | PKCE mandatory for public clients. Never use implicit flow. |
| Legacy or compatibility fallback only | SSE | API key or OAuth | SSE is deprecated in newer MCP spec. Migrate to Streamable HTTP. |
| Ephemeral CI / script automation | `stdio` | None (env vars) | Use a short-lived subprocess; discard at script exit. |
| Plugin-sourced server in agent session | `stdio` or HTTP | Plugin manifest auth | Diff manifest on reload; reconnect explicitly with host-owned precedence. |

---

## Transport Comparison

| Property | `stdio` | Streamable HTTP | SSE (legacy) |
|----------|---------|----------------|--------------|
| Network exposure | None — local only | Yes | Yes |
| Multi-client support | No — one process per client | Yes | Yes |
| Latency | Minimal | Network round-trip | Network round-trip |
| Auth surface | Inherited env / none | Header / OAuth | Header / OAuth |
| Recommended for | Local tools, dev machines | Shared / remote services | Compatibility fallback |
| MCP spec status | Current | Current (preferred remote) | Deprecated — plan migration |

---

## Auth Comparison

| Auth Type | When to Use | Key Risks | Mitigation |
|-----------|-------------|-----------|------------|
| None | `stdio` local only, trusted environment | Host compromise = full access | Sandbox the process; never use on network-exposed servers |
| API key (header) | Internal shared service, low-overhead auth | Key leakage in logs or config | Rotate regularly; use secrets manager; validate `Host` header |
| OAuth 2.1 PKCE | Multi-user, browser clients, public servers | Token replay, scope creep | Short-lived tokens; strict scope list; PKCE mandatory |
| OAuth 2.1 client credentials | Server-to-server, CI automation | Credential storage risk | Vault or env-level secrets; rotate on schedule |
| Vendor OAuth flow | Third-party hosted servers | Scope over-grant, stale tokens | Review scopes at setup; clear cached auth on anomalies |

---

## Selection Flowchart

```
Is the server running on the same machine as the client?
  YES → Use stdio. No auth needed; pass secrets via env vars.
  NO  ↓

Is it a legacy server that only speaks SSE?
  YES → Use SSE + API key (plan migration to Streamable HTTP).
  NO  ↓

Is it a shared service (multiple clients or users)?
  YES ↓
    Is it a third-party vendor server?
      YES → Streamable HTTP + vendor OAuth 2.1 flow.
      NO  ↓
    Do clients include browsers or public apps?
      YES → Streamable HTTP + OAuth 2.1 PKCE.
      NO  → Streamable HTTP + API key (internal) or OAuth 2.1 client credentials (server-to-server).
  NO  → Streamable HTTP + API key is sufficient for single-tenant remote.
```

---

## Security Rules That Apply Regardless of Choice

- Validate `Host` and `Origin` headers on all HTTP-exposed servers.
- Never pass MCP auth tokens through to upstream APIs — use separate credentials per service.
- Bind local HTTP servers to `127.0.0.1`, never `0.0.0.0`, unless remote access is intentional.
- Add server-side row limits, timeouts, and logging before any write-capable tool goes live.
- Treat all tool output as untrusted input — validate before using in privileged actions.

---

## Known Pitfalls by Combination

| Combination | Common Failure Mode | Resolution |
|-------------|--------------------|-----------:|
| `stdio` + OAuth | OAuth requires a redirect URI — stdio has no HTTP listener | Use env-var tokens for stdio; OAuth is for HTTP transports only |
| SSE + no auth | Any local process can connect | Add at minimum an API key; or migrate to Streamable HTTP |
| Streamable HTTP + `Authorization` header missing | Looks like a protocol failure | Check auth header name and value; clear cached auth state once, then retry |
| OAuth token stale | Requests fail with 401 silently | Clear local cache once, re-authenticate once, stop if it still fails |
| Multi-server hub, mixed transports | Ownership and lifecycle ambiguity | Document each server's transport, auth, and write scope in `sources.json` or a manifest |

---

## References

- MCP specification (transport): `https://modelcontextprotocol.io/specification/2025-11-25`
- MCP authorization spec: `https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization`
- Health-check script: `../scripts/mcp_health_check.sh`
- Security checklist: `mcp-security.md`
