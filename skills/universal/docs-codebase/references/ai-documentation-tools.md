# AI Documentation Tools

Guide for choosing and using AI-aware documentation tools without overclaiming what automation can safely do.

Tool names, feature support, and plugin availability change quickly. This file holds selection criteria; before recommending a specific platform or feature, check that vendor's current documentation and changelog and record the date you checked.

---
## Table of Contents

- [Principles](#principles)
- [Tool Categories](#tool-categories)
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


## Principles

Durable documentation workflows combine:

- AI for draft generation and targeted review, not unsupervised publishing
- machine-readable delivery (`llms.txt`, `llms-full.txt`, stable URLs, predictable headings)
- repo instruction files (`AGENTS.md`, `CLAUDE.md`) for coding assistants
- documentation QA gates for links, style, spelling, contracts, and runnable examples
- MCP-backed context access when you need structured access to local docs, specs, tickets, or design systems

Avoid treating "AI docs" as a separate publishing channel. The goal is one canonical documentation set that is readable by humans and reliable for agents.

---

## Tool Categories

Pick the category first, then compare current products inside it against the [evaluation checklist](#tool-evaluation-checklist). Do not carry a product ranking from memory; verify each product's current feature list.

| Category | Choose it when | Main watchout |
|----------|----------------|---------------|
| **Hosted documentation platform** | You need a developer portal with search, analytics, and API reference without running a site yourself | The hosted portal becomes the only source of truth; keep Markdown/OpenAPI in the repo and import from it |
| **Docs site generator** (Markdown-first static site) | Docs live next to code and ship through the same review and CI | Match the generator's runtime to what the team already maintains; versioned docs add real upkeep |
| **All-in-one API design + test + docs tool** | One API team owns spec, mocks, and docs | Export the spec to the repo; do not let the tool's internal model become canonical |
| **Code-aware writing assistant** | Multi-file edits where docs must track code changes | Diffs still need human review; repo-wide canonicalization needs stronger review than inline IDE drafting |

---

## AI-Readable Documentation

### Minimum Standard

- Publish one canonical page per topic.
- Keep stable URLs and avoid duplicate near-identical pages.
- Start each page with a self-contained summary paragraph.
- Add `last_verified` on volatile vendor/platform pages.
- Keep examples complete, labeled, and runnable.

### `llms.txt` and `llms-full.txt`

Use these when your docs platform supports them directly or through a plugin (check its current docs).

- `llms.txt` should point agents to the best starting pages.
- `llms-full.txt` can provide a richer inventory or long-form extract for AI consumption.
- Do not dump every draft page into these files. Include only canonical pages that you would want an agent to trust.

### Instruction Files for Coding Assistants

- Which runtime loads which instruction file, and when, is owned by [agents-memory](../../agents-memory/SKILL.md); this section covers only how docs expose content to those files.
- Keep `AGENTS.md` canonical. Use the [agents-memory loading lookup](../../agents-memory/references/loading-and-layers.md#agentsmd-in-claude-code-lookup-step) to check the team's runtime versions, providers, configuration, and loaded files. Add a `CLAUDE.md` import or symlink only when native loading is unreliable for a contributor; keep any Claude-specific content beside the import.
- Closer subdirectory instruction files override or extend the root; keep root and local files consistent.
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

Illustrative only: server package names and startup contracts change, so look up the current filesystem server in the MCP project's server list before copying this.

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
