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

Documented behavior (check the Codex AGENTS.md guide above for changes):
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
- concise `CLAUDE.md`, or a native `AGENTS.md` if the repo has no `CLAUDE.md`
- `@path` imports for large or specialized guidance
- `.claude/rules/` only where separate rule files are justified
- stale advice that recommends broad duplication or mandatory symlinks

Review questions:
- Is the loaded instruction file (`CLAUDE.md` or `AGENTS.md`) still concise enough to act as an entrypoint?
- Should some content move into imported files?
- Are imported files still present and still worth loading?
- Do the rules reflect the current toolchain and repo layout?

Two memory systems, one audit: Claude Code has both a written instruction layer (`CLAUDE.md`
and/or `AGENTS.md`) and Auto memory (notes Claude accumulates on its own from corrections and
observed preferences). An AI-instruction audit that only reads the instruction file misses the
second layer. Check whether Auto memory notes have drifted from current repo reality the same
way you would check a stale instruction-file line, and flag contradictions between the two (e.g.
an auto-memory note that recommends a workflow the current instructions explicitly override).

**Native `AGENTS.md` support (see https://code.claude.com/docs/en/memory for the minimum
Claude Code version):** Claude Code can read a repo's `AGENTS.md` directly as
project instructions, without a `CLAUDE.md`. The default **Project instructions** setting
(`claude-md-or-agents-md`) reads `AGENTS.md` only when the working directory and everything
above it has no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md`. This makes `CLAUDE.local.md`
a silent AGENTS.md-suppressor: adding one to a repo that relies on native AGENTS.md stops Claude
from reading AGENTS.md, unless **Project instructions** is set to `claude-md-and-agents-md`. An
audit of an AGENTS.md-only repo should therefore:
- confirm no stray `CLAUDE.md`/`CLAUDE.local.md` is shadowing `AGENTS.md`, and
- check the `pluginConfigs["agents-md@builtin"].options.instructionFiles` setting when both files are meant to load together.

Older Claude Code releases (and sessions with the `agents-md` plugin disabled, or some
Bedrock/telemetry-disabled sessions on older releases) read only `CLAUDE.md` files, so a repo that
depends on AGENTS.md should keep a `CLAUDE.md` that does `@AGENTS.md` as a fallback. Check the
docs page for the minimum version and re-verify these specifics before
treating them as durable, since Claude Code's instruction-loading behavior has changed release
to release.

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

[`llms.txt`](https://llmstxt.org/) is a Markdown navigation file at `/llms.txt` or a scoped path such as `/docs/llms.txt`. It can point coding assistants to maintained API guides and references without requiring them to discover every page by crawling. The file's scope is the URL path under which it is published; when several apply, the most specific path wins.

This is a proposal, not a W3C/RFC standard or a proven citation/SEO lever. If agents consume the docs, test whether the file helps them reach canonical pages; record an absent file as a gap only when the site's agent-discovery plan calls for it.

Audit checklist:
- Does the relevant site path have an `llms.txt` where agents will look for it? If this is an agreed discovery route, treat absence as a gap.
- Does that file link to current canonical pages? Stale endpoint lists defeat its purpose.
- Is there a `/llms-full.txt` with expanded detail for repos with complex APIs? Note: `llms-full.txt` is a vendor convention, not part of the llmstxt.org spec itself.
- Does an `## Optional` section hold links agents can skip on a shorter context budget, per the spec?

Example structure (per https://llmstxt.org/: H1 required; blockquote and H2 file-list sections optional; links use `- name: notes`):

```markdown
# Product Name

> One-sentence description of what the API does.

## Authentication

- [Auth guide](https://docs.example.com/auth): how to obtain and use API keys.

## Endpoints

- [API reference](https://docs.example.com/api/reference): full endpoint list and schemas.

## Optional

- [Quickstart](https://docs.example.com/quickstart): a walkthrough agents can skip if context is tight.
```

## Evidence checklist

- each external claim has a source URL and verification date
- each implementation claim maps to code, config, or decision log
- each instruction file references current paths and command names
- each imported file is reachable and still needed
- each obsolete AI-generated draft has a retirement plan
- any agreed `llms.txt` discovery path resolves to current canonical pages

## Output

Produce:
- a canonical-doc map by topic
- a list of stale or duplicate AI-generated docs
- a list of tool-instruction drift findings
- a backlog of cleanup actions with owners and dates
