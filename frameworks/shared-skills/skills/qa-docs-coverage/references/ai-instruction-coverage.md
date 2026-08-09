# AI Instruction Coverage

Use this reference when the audit includes repository instruction files, large AI-generated docs folders, or cross-tool memory layers.

## Table of Contents

- [When to use it](#when-to-use-it)
- [Audit goals](#audit-goals)
- [Codex / OpenAI audit](#codex-openai-audit)
- [Claude Code audit](#claude-code-audit)
- [AI-generated docs folder audit](#ai-generated-docs-folder-audit)
- [Minimum QA gate](#minimum-qa-gate)
- [llms.txt and agent-readable docs](#llmstxt-and-agent-readable-docs)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Quickstart](#quickstart)
- [Evidence checklist](#evidence-checklist)
- [Output](#output)

## When to use it

- The repo contains `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `.claude/rules/`, or similar tool-specific instruction files.
- The repo has a large `docs/` folder with research notes, generated specs, migration drafts, or phased implementation documents.
- You need to verify that AI-facing docs match current tool behavior instead of repeating old platform assumptions.

## Audit goals

- Find one canonical instruction layer for each active tool.
- Remove or archive duplicate and superseded AI-generated drafts.
- Verify that instruction files point to current repo structure, commands, and workflows.
- Confirm that imported or nested instruction files still exist and add value.

## Codex / OpenAI audit

Primary reference:
- OpenAI AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md

Current behavior (verified 2026-06-09):
- Discovery walks from git root to current working directory; at each level Codex checks `AGENTS.override.md` first, then `AGENTS.md`, then any configured `project_doc_fallback_filenames`
- Files concatenate root-down; later (closer) files override earlier guidance
- Combined size cap: 32 KiB by default (`project_doc_max_bytes` in `~/.codex/config.toml`)
- Discovery happens once per Codex run; changing AGENTS.md mid-session invalidates the cached prefix

Check for:
- root `AGENTS.md` with repo-wide standards
- nested `AGENTS.md` only where a subtree truly needs extra rules
- `AGENTS.override.md` only where explicit local override behavior is intended
- stale claims about one mandatory file layout across all tools
- combined file size approaching the 32 KiB cap (audit with `wc -c`)

Review questions:
- Does the root file still describe the actual repo layout and standards?
- Are nested files additive and scoped, or do they duplicate the root file?
- Do overrides replace rules intentionally, or have they become drift?
- Are file references and commands still valid?

## Claude Code audit

Primary references:
- Anthropic memory docs: https://code.claude.com/docs/en/memory
- Anthropic best practices: https://code.claude.com/docs/en/best-practices

Check for:
- concise `CLAUDE.md`
- `@path` imports for large or specialized guidance
- `.claude/rules/` only where separate rule files are justified
- stale advice that recommends broad duplication or mandatory symlinks

Review questions:
- Is `CLAUDE.md` still concise enough to act as an entrypoint?
- Should some content move into imported files?
- Are imported files still present and still worth loading?
- Do the rules reflect the current toolchain and repo layout?

Two memory systems, one audit: as of 2026 Claude Code has both `CLAUDE.md` (instructions the
user writes) and Auto memory (notes Claude accumulates on its own from corrections and observed
preferences). An AI-instruction audit that only reads `CLAUDE.md` misses the second layer. Check
whether Auto memory notes have drifted from current repo reality the same way you would check a
stale `CLAUDE.md` line, and flag contradictions between the two (e.g. an auto-memory note that
recommends a workflow the current `CLAUDE.md` explicitly overrides).

## AI-generated docs folder audit

Canonical metadata for non-final docs:
- `status`
- `owner`
- `last_verified`
- `source_links`
- `integrates_into`
- `delete_by`

Recommended workflow:
1. Inventory docs by topic and type.
2. Pick one canonical file for each topic.
3. Mark all other files as draft, integrated, or obsolete.
4. Verify every external claim and tool-specific behavior against current primary sources.
5. Delete or archive integrated drafts on schedule.

## Minimum QA gate

Block merges when:
- a changed feature has no canonical doc
- an integrated draft is past `delete_by`
- a critical instruction file points to missing paths or invalid commands
- `AGENTS.md` or `CLAUDE.md` is clearly stale for the active toolchain

Warn instead of block when:
- non-critical drafts are old but still isolated
- duplicate docs exist without affecting the canonical path
- P2 and P3 instruction gaps are identified but not yet harmful

## llms.txt and agent-readable docs

`llms.txt` (https://llms.txt) is a plain Markdown file placed at `/llms.txt` on a docs site. It gives coding assistants, MCP-connected tools, and IDE agents (Cursor, Continue, Cline) a structured summary of your API — endpoints, auth methods, response schemas — without having to crawl the full site.

Status as of 2026: adopted by Stripe, Cloudflare, and Vercel, among others; not a W3C/RFC standard. Adoption-rate claims diverge sharply by measurement method — one crawl (BuiltWith) reports 844,000+ sites, while independent 2026 crawls of the Tranco top-10k find roughly 5-10% adoption, and at least one 2026 analysis found no measurable correlation between having `llms.txt` and being cited by LLMs. Treat any single adoption or effectiveness number as unverified as of 2026-07-11 — cite the source and methodology in a report rather than repeating a bare figure. Its absence remains a legitimate coverage gap for an agent-facing API on the "is this discoverable to a coding agent" criterion; do not oversell it as a citation or SEO lever.

Audit checklist:
- Does the repo or docs site have a `/llms.txt`? If the API is consumed by agents or IDEs, treat absence as a gap.
- Is `/llms.txt` current? Stale endpoint lists defeat its purpose.
- Is there a `/llms-full.txt` with expanded detail for repos with complex APIs?
- Are there `<url type="optional">` entries pointing to reference pages agents can fetch on demand?

Example minimal structure:

```markdown
# Product Name

> One-sentence description of what the API does.

## Authentication
<url>https://docs.example.com/auth</url>

## Endpoints
<url>https://docs.example.com/api/reference</url>

## Quickstart
<url type="optional">https://docs.example.com/quickstart</url>
```

## Evidence checklist

- each external claim has a source URL and verification date
- each implementation claim maps to code, config, or decision log
- each instruction file references current paths and command names
- each imported file is reachable and still needed
- each obsolete AI-generated draft has a retirement plan
- `/llms.txt` exists and is current for any externally consumed API

## Output

Produce:
- a canonical-doc map by topic
- a list of stale or duplicate AI-generated docs
- a list of tool-instruction drift findings
- a backlog of cleanup actions with owners and dates
