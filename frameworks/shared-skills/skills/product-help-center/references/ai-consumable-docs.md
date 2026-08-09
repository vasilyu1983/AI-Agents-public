# AI-Consumable Docs

## Table of Contents

- [Contents](#contents)
- [When This Matters](#when-this-matters)
- [Human-Readable and Machine-Readable Layers](#human-readable-and-machine-readable-layers)
- [llms.txt and llms-full.txt](#llmstxt-and-llms-fulltxt)
- [MCP for Docs](#mcp-for-docs)
- [skill.md and Assistant-Specific Context](#skillmd-and-assistant-specific-context)
- [Content Formatting Rules](#content-formatting-rules)
- [Rollout Checklist](#rollout-checklist)

Patterns for making help centers and docs easier for assistants and agents to consume in 2026.

## Contents

- When AI-consumable docs matter
- Human-readable and machine-readable layers
- llms.txt and llms-full.txt
- MCP for docs
- skill.md and assistant-specific context
- Content formatting rules
- Rollout checklist

## When This Matters

Prioritize this layer when the user needs:
- documentation that is regularly consumed by AI assistants
- agent-facing access to docs, schemas, or product guidance
- better retrieval quality across external assistants and internal support AI
- cleaner separation between human navigation and machine discovery

Do not over-prescribe this layer for a simple FAQ or a very small help center.

## Human-Readable and Machine-Readable Layers

Good AI-consumable docs still start with good human docs.

Required human layer:
- clear canonical URLs
- stable titles
- one task or concept per page
- structured headings, lists, tables, and exact terms

Useful machine layer:
- markdown export or markdown-first content
- API references and schemas
- explicit metadata for version, locale, and audience
- agent-facing indexes such as `llms.txt` and `llms-full.txt`
- MCP server exposure when tools or docs should be consumable by assistants

## llms.txt and llms-full.txt

### What They Are

- `llms.txt` is an emerging convention for advertising AI-relevant site structure.
- `llms-full.txt` is a larger machine-oriented export when a site supports it.

### How To Position Them

- Treat them as additive discoverability aids.
- Do not describe them as a universal standard or replacement for good site architecture.
- Use them when the docs platform supports them cleanly or when assistant consumption is a real requirement.

### Good Contents

- top sections and canonical entry points
- version and product boundaries
- links to API reference, changelog, and troubleshooting sections
- notes on authentication or access restrictions

## MCP for Docs

Use MCP for docs when:
- assistants need structured access to documentation resources
- the same docs surface should be usable across multiple assistant clients
- the product also exposes tools or actions that assistants may call

Good use cases:
- exposing API docs and schemas as resources
- exposing product docs plus safe, scoped operational tools
- enabling assistants to browse the latest published docs through one interface

Do not recommend MCP by default when:
- plain web docs and search are enough
- the team cannot own auth, tooling policy, or maintenance

## skill.md and Assistant-Specific Context

Some docs platforms now support assistant-facing context files such as `skill.md`.

Use assistant-specific context when:
- the same documentation needs a concise operational layer for coding assistants
- the team wants to encode tool usage rules, safe workflows, or navigation hints

Keep assistant context:
- short
- explicit about tool boundaries and priorities
- aligned with the public docs or internal runbooks it references

## Content Formatting Rules

For AI consumption:
- make page scope narrow and explicit
- include exact feature names and error strings
- prefer tables for limits, plans, and capability matrices
- separate end-user instructions from internal policies
- mark outdated or version-specific content clearly

Avoid:
- mixed audiences on one page
- long marketing intros before the actual answer
- duplicated facts across many pages
- screenshots that contain the only copy of important text

## Rollout Checklist

- confirm canonical URLs and page titles
- verify markdown or machine-friendly export exists where needed
- verify `llms.txt` or equivalent index if the platform supports it
- verify MCP only if there is a real assistant-consumption need
- validate version, locale, and audience metadata
- test the docs with at least one assistant workflow before declaring success
