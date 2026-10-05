# README Best Practices

Decision rules for READMEs. The section skeleton is in [assets/project-management/readme-template.md](../assets/project-management/readme-template.md); this file covers what to put in it, what to keep out, and how to keep it true.

## Table of Contents

- [The README's Job](#the-readmes-job)
- [Section Order by Project Type](#section-order-by-project-type)
- [Rules for Each Core Section](#rules-for-each-core-section)
- [What Stays Out](#what-stays-out)
- [README Anti-Patterns](#readme-anti-patterns)
- [Maintenance Checklist](#maintenance-checklist)
- [README Success Criteria](#readme-success-criteria)

---

## The README's Job

The README is the navigation anchor for humans and agents: what this is, how to get it running, and where the deeper docs live. It is not the handbook. When a section grows past a screen, move it to `docs/` and link it.

## Section Order by Project Type

Always first: name and a one-line description of what it does and for whom. Then order by what the reader needs first:

| Project type | Order after the description |
|--------------|-----------------------------|
| Library / package | Install → minimal usage example → link to API reference → compatibility (supported runtime versions) |
| CLI tool | Install → the 3-5 most-used commands with examples → link to full command reference → exit codes if scripts depend on them |
| Web application | Prerequisites → local setup → configuration (env vars table) → run and test → deploy link |
| API service | What it serves → auth setup → one request/response example → link to the API reference → rate limits |
| Internal/monorepo package | Owner and support channel → how it fits the system → local dev → links to runbooks |

Contributing, license, and support go at the end for every type.

## Rules for Each Core Section

- **Description:** say what it does, not how it is built. "Stack: React + Node" is not a description.
- **Prerequisites:** name each dependency with a minimum version, and keep those versions in sync with the manifests and CI matrix; the README is the first place they drift. Never write "latest".
- **Install/setup:** commands a reader can paste in order on a clean machine. If a step needs a secret or account, say where it comes from.
- **Usage:** one complete, runnable example beats five fragments. Label anything illustrative.
- **Configuration:** a table of every environment variable or option with default and whether it is required. Generate it from the config schema if one exists.
- **Badges:** only ones that carry decision information (CI status, supported versions, license). Vanity badges push the description below the fold.
- **Table of contents:** add one once the README scrolls past a couple of screens; most renderers generate one, so check before hand-writing it.

## What Stays Out

- Features that do not exist yet ("coming soon"): readers and agents treat them as available.
- Full API reference, architecture explanations, runbooks: link to the canonical doc.
- Names of individuals as the support path ("ask Sarah"): use a team channel or CODEOWNERS.
- Status reports, roadmaps, or changelogs: link to the canonical source.

## README Anti-Patterns

- No working install path, or one that only works on the author's machine.
- Screenshots of an old UI.
- Hidden prerequisites discovered only when install fails.
- Code examples that no longer match the current API.
- Wall of text with no headings, lists, or code blocks.
- A README that duplicates `docs/` content and drifts from it.

## Maintenance Checklist

When the code, dependencies, or UI change:

- [ ] Install and setup commands run on a clean environment
- [ ] Examples run against the version pinned in the install section
- [ ] Links pass the internal link check (see [documentation-testing.md](documentation-testing.md#link-validation))
- [ ] Screenshots match the current UI
- [ ] Prerequisite versions match manifests and CI
- [ ] Configuration table matches the config schema

## README Success Criteria

A reader (human or agent) can, from the README alone:

1. Say what the project does and whether it fits their need.
2. Get it running locally by following the steps in order.
3. Find the deeper docs, the owner, and where to ask for help.
