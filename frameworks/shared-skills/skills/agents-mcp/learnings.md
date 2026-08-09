# agents-mcp — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] CORRECTION of 2026-06-18 entry below: 'codex mcp add' DOES support --url (+ --bearer-token-env-var) for Streamable HTTP servers — added in openai/codex PR #4904, merged 2025-10-08, well before the earlier "stdio only" claim was written. Confirmed live against `codex mcp add --help` on codex-cli 0.144.1. The earlier bullet was already stale when authored; verify CLI facts against the installed binary's --help, not just docs pages, since docs can lag shipped CLI features.
- [2026-06-18][SUPERSEDED 2026-07-11] Codex 'codex mcp add' has no --url/--transport flag (stdio only). Remote Streamable HTTP servers need a ~/.codex/config.toml [mcp_servers.NAME] block with url=. (developers.openai.com/codex/config-reference, 2026-06-18)
## Domain Knowledge

- [2026-07-11] Anthropic donated MCP to the Agentic AI Foundation (Linux Foundation) on 2025-12-09; maintainers keep technical authority. Cite AAIF, not Anthropic, as protocol owner.
- [2026-06-18] MCP 2026-07-28-RC (publ. 2026-05-29) is a stateless redesign: no initialize handshake, no Mcp-Session-Id, MRTR replaces elicitation/sampling/roots, server/discover required. Watchlist only — do not migrate.
- [2026-06-18] MCP 2025-11-25 makes RFC 8707 resource indicators and /.well-known/oauth-protected-resource MANDATORY for HTTP auth; Client ID Metadata Docs replace Dynamic Client Registration.
- [2026-07-11] MCP 2026-07-28 finalizes on that date (not a hypothetical RC anymore, ~2.5 weeks out at authoring time): Roots/Sampling/Logging are DEPRECATED outright (not merely folded into MRTR) — migrate to tool-parameter dirs, direct provider API calls, and stderr/OTel logging. HTTP+SSE transport and OAuth Dynamic Client Registration are also formally reclassified Deprecated under the new 12-month feature lifecycle policy. (blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate)
- [2026-07-11] Claude Code's ENABLE_TOOL_SEARCH deferred tool loading has a confirmed, unresolved gap: it does not reliably defer tool schemas from Streamable HTTP / remote MCP servers, so a large HTTP gateway can load 60%+ of context upfront even with auto:N set. Anthropic closed the report as "not planned" (github.com/anthropics/claude-code issue #40314). Don't assume deferral saves tokens for HTTP fleets — measure actual usage, prefer stdio or fewer/narrower HTTP servers instead.
- [2026-07-11] TypeScript MCP SDK v2 is in beta (targets the 2026-07-28 spec, ships stable alongside it); v1.x remains the production-supported lane for at least 6 months after v2 stabilizes. Do not treat v2 as "pre-alpha, ignore it" going forward — it is close to shipping.
## Open Questions

## Consolidated Principles

