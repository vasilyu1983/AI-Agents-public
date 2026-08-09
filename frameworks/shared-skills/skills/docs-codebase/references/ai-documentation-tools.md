# AI Documentation Tools (March 2026)

Guide for choosing and using AI-aware documentation tools without overclaiming what automation can safely do.

---
## Table of Contents

- [What Changed in 2026](#what-changed-in-2026)
- [Tool Categories](#tool-categories)
- [Hosted Documentation Platforms](#hosted-documentation-platforms)
- [Docs Site Generators](#docs-site-generators)
- [Code-Aware Writing Assistants](#code-aware-writing-assistants)
- [AI-Readable Documentation](#ai-readable-documentation)
- [Minimum Standard](#minimum-standard)
- [`llms.txt` and `llms-full.txt`](#llmstxt-and-llms-fulltxt)
- [Instruction Files for Coding Assistants](#instruction-files-for-coding-assistants)
- [MCP for Documentation Workflows](#mcp-for-documentation-workflows)
- [What MCP Actually Enables](#what-mcp-actually-enables)
- [Typical Docs Workflow](#typical-docs-workflow)
- [Filesystem Server Pattern](#filesystem-server-pattern)
- [Tool Evaluation Checklist](#tool-evaluation-checklist)
- [For Any Documentation Platform](#for-any-documentation-platform)
- [For API Documentation Tools](#for-api-documentation-tools)
- [For AI Assistants in Docs Workflows](#for-ai-assistants-in-docs-workflows)
- [Recommended Adoption Path](#recommended-adoption-path)
- [Resources](#resources)


## What Changed in 2026

The strongest documentation workflows now combine:

- AI for draft generation and targeted review, not unsupervised publishing
- machine-readable delivery (`llms.txt`, `llms-full.txt`, stable URLs, predictable headings)
- platform-native instruction files (`AGENTS.md`, `CLAUDE.md`) for coding assistants
- documentation QA gates for links, style, spelling, contracts, and runnable examples
- MCP-backed context access when you need structured access to local docs, specs, tickets, or design systems

Avoid treating "AI docs" as a separate publishing channel. The goal is one canonical documentation set that is readable by humans and reliable for agents.

---

## Tool Categories

### Hosted Documentation Platforms

| Tool | Best For | Strengths | Watchouts |
|------|----------|-----------|-----------|
| **Mintlify** | Developer docs portals | Hosted DX, API docs, search, analytics | Verify current vendor-specific automation before scripting it |
| **ReadMe** | API and product docs | Interactive API reference, changelogs, metrics | Keep spec import and canonical Markdown ownership clear |
| **Apidog** | API teams that want design + testing + docs in one place | Spec, mocking, testing, docs | Avoid making the hosted portal your only source of truth |

### Docs Site Generators

| Tool | Best For | Strengths | Watchouts |
|------|----------|-----------|-----------|
| **VitePress** | Modern Markdown-first docs sites | Fast, simple, strong Markdown ergonomics, `llms.txt` support | Best when your team is comfortable with Node-based docs |
| **Astro Starlight** | Content-heavy product docs | Strong IA, Astro ecosystem, plugin flexibility | Confirm plugin choices early for search and analytics |
| **Docusaurus** | Large versioned docs portals | Mature ecosystem, versioning, React customization | Heavier setup and maintenance than VitePress |
| **MkDocs + Material** | Python and ops-oriented repos | Fast setup, solid search, familiar for infra teams | Less flexible than JS-site stacks for custom app-like docs |

### Code-Aware Writing Assistants

| Tool | Best For | Strengths | Watchouts |
|------|----------|-----------|-----------|
| **Claude Code** | Multi-file repo-aware writing and review | Strong repository context, project memory, imports via `CLAUDE.md` | Keep instructions scoped and current |
| **Codex / AGENTS.md-aware tools** | Repo-native implementation plus docs updates | `AGENTS.md` support, subdirectory scoping | Keep root and local instruction files consistent |
| **Cursor / GitHub Copilot** | Inline drafting inside IDEs | Fast edits and refactors near code | Requires stronger human review for repo-wide canonicalization |

---

## AI-Readable Documentation

### Minimum Standard

- Publish one canonical page per topic.
- Keep stable URLs and avoid duplicate near-identical pages.
- Start each page with a self-contained summary paragraph.
- Add `last_verified` on volatile vendor/platform pages.
- Keep examples complete, labeled, and runnable.

### `llms.txt` and `llms-full.txt`

Use these when your docs platform supports them directly or through a plugin.

- `llms.txt` should point agents to the best starting pages.
- `llms-full.txt` can provide a richer inventory or long-form extract for AI consumption.
- Do not dump every draft page into these files. Include only canonical pages that you would want an agent to trust.

### Instruction Files for Coding Assistants

- Use `AGENTS.md` for OpenAI/Codex-style tooling. Root files and closer subdirectory overrides both matter.
- Use `CLAUDE.md` or `.claude/CLAUDE.md` for Claude Code. Prefer `@path/to/import` for shared guidance instead of copy/paste duplication.
- Keep entry files thin. Put reusable policy or architecture context in shared docs and link or import it from the platform entry file.

---

## MCP for Documentation Workflows

### What MCP Actually Enables

MCP gives agents a structured way to reach tools and context. For docs work, that usually means:

- reading documentation trees or design-system files safely
- looking up API specs, schemas, tickets, dashboards, or runbooks
- validating examples against a live or mocked source of truth
- composing review workflows across code, docs, and external systems

MCP does **not** guarantee automatic synchronization. You still need explicit workflows, review steps, and ownership.

### Typical Docs Workflow

```text
Code/spec change
  -> agent reads the affected docs, contracts, and issue context
  -> agent proposes a docs diff
  -> human reviews wording, scope, and examples
  -> CI checks links, lint, contracts, and example validity
```

### Filesystem Server Pattern

Treat configuration as illustrative because server names and startup contracts evolve, but the official filesystem server package is now:

```json
{
  "mcpServers": {
    "docs-fs": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "./docs",
        "."
      ]
    }
  }
}
```

Use allowlisted paths only. Give agents access to the smallest set of documentation and repo paths needed for the task.

---

## Tool Evaluation Checklist

### For Any Documentation Platform

- REQUIRED: Canonical source-of-truth workflow (`.md`, OpenAPI, AsyncAPI, or imported content) that fits your repo
- REQUIRED: Preview environments or equivalent review flow before publish
- REQUIRED: Search plus production analytics or query data
- REQUIRED: Link checking, spelling/style linting, and example validation in CI
- BEST: `llms.txt` or another explicit AI-readable export
- BEST: Stable edit URLs, page metadata, and last-updated / last-verified signals

### For API Documentation Tools

- REQUIRED: OpenAPI and/or AsyncAPI import that matches your stack
- REQUIRED: Good handling of auth flows, error models, and versioned changelogs
- BEST: SDK snippets, webhook/event docs, workflow docs, and contract linting

### For AI Assistants in Docs Workflows

- REQUIRED: Repo integration with reviewable diffs
- REQUIRED: Clear handling of confidential content, secrets, and PII
- BEST: Ability to work from specs/contracts instead of prose alone
- BEST: Support for modular instruction files instead of one monolithic prompt

---

## Recommended Adoption Path

1. Make your current docs canonical and trustworthy before adding more automation.
2. Add QA gates: links, style, spelling, contracts, and example checks.
3. Publish AI-readable outputs (`AGENTS.md`, `CLAUDE.md`, `llms.txt`) for the tools you actually use.
4. Introduce AI for drafting and review, starting with low-risk docs like changelogs, onboarding updates, and API examples.
5. Add MCP only when agents need structured access to specs, tickets, or external systems beyond the repo filesystem.

---

## Resources

- **llms.txt**: https://llmstxt.org/
- **Model Context Protocol**: https://modelcontextprotocol.io/docs/develop/build-server
- **OpenAI AGENTS.md Guide**: https://developers.openai.com/codex/guides/agents-md
- **Claude Code Memory**: https://code.claude.com/docs/en/memory
- **VitePress llms.txt Support**: https://vitepress.dev/guide/llms
- **Mintlify**: https://www.mintlify.com
- **ReadMe**: https://readme.com/
- **Apidog**: https://apidog.com/

---

> Success criteria: AI tools reduce drafting and review time while canonical docs remain human-owned, testable, and current.
