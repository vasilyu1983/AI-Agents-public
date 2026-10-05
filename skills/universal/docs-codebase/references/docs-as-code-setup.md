# Docs-as-Code Setup Guide

Decision rules for running documentation as code: where each kind of doc lives, how to choose a site generator, and which pipeline stages are worth having. Installation and configuration syntax for a specific generator are in that generator's own docs; check them for the current version rather than copying a config from here.

## Table of Contents

- [Repository Documentation Governance](#repository-documentation-governance)
- [Choosing a Site Generator](#choosing-a-site-generator)
- [Pipeline Stages](#pipeline-stages)
- [Versioned Docs](#versioned-docs)
- [Resources](#resources)

---

## Repository Documentation Governance

Agent-readable repos need documentation placement rules as much as they need writing rules. The goal is to make the repo legible without creating a permanent pile of one-off Markdown files.

### Placement Matrix

| Location | Owns | Must Not Own |
|----------|------|--------------|
| `AGENTS.md` / `CLAUDE.md` | Hot execution policy, exact commands, hard constraints, pointers to deeper docs | Codebase catalog, reports, plans, inventories, duplicated docs |
| `README.md` | Navigation, setup entry point, short orientation | Every operational procedure or architecture detail |
| `docs/tech/` or `docs/architecture/` | Canonical technical and architecture docs | Temporary investigation notes |
| `docs/operations/` or `docs/runbooks/` | Operational procedures, incident steps, release steps | Product explanations or generic onboarding prose |
| `docs/api/` | API reference, contracts, examples | Product roadmap or debugging reports |
| `docs/specs/` or `docs/plans/` | Active specs and implementation plans | Permanent status truth after the work ships |
| `docs/reports/` | Time-bound analysis, audits, migration findings | Canonical architecture truth after integration |
| `docs/context/` or `context/` | Generated or compiled LLM context artifacts | Hand-authored source of truth without rebuild ownership |
| `.archive/` | Historical material excluded from normal context | Anything agents should normally read |
| `scripts/README.md` | Script-adjacent commands and maintenance workflow | Repo-wide onboarding or product docs |

### New Markdown Creation Test

Create a new Markdown file only when the answer to each question is yes:

1. Does no existing canonical doc already own this subject?
2. Is the target folder correct for the doc type?
3. Is the file linked from the relevant README, index, docs nav, or context hub?
4. Does the file have an owner or review path?
5. Does volatile content include `last_verified` or a refresh command?
6. Is there a lifecycle state for reports and plans: `active`, `pending-integration`, `integrated`, or `superseded`?
7. If generated, is the source artifact and rebuild command documented?

If the answer is no, update the closest canonical doc or leave the content in the task thread. Do not create root-level `SUMMARY.md`, `MIGRATION.md`, `OPTIMIZATION_NOTES.md`, or similar files unless the repo explicitly asks for that filename.

### Agent Context Pattern

For LLM-facing repo context:

- Keep the hot instruction layer short and precise.
- Put durable detail in canonical docs.
- Put large generated summaries in `docs/context/` or `context/`, built from structured artifacts.
- Keep raw evidence separate from compiled summaries.
- Prefer links and stable headings over duplicated prose.

Instruction files are loaded into every agent session, so they should contain focused, non-obvious rules and route agents to repo-local evidence instead of becoming all-purpose docs. Which runtime loads which file is owned by [agents-memory](../../agents-memory/SKILL.md).

---

## Choosing a Site Generator

Pick by constraint, then verify the current feature list of each candidate in its own docs. Do not carry a tool ranking from memory; features such as built-in versioning, search, and `llms.txt` output change between releases.

Decide in this order:

1. **Hosted or self-built?** Hosted portals suit teams without front-end capacity; the cost is that the portal tends to become the source of truth. If you go hosted, keep Markdown and specs in the repo and import from them.
2. **Match the stack the team already maintains.** A Python-heavy or ops team maintains a Python-based generator; a front-end team maintains a JS-based one. A generator nobody on the team can debug becomes the docs bottleneck.
3. **Do you need multiple published versions?** Only then weigh built-in versioning heavily (see [Versioned Docs](#versioned-docs)).
4. **Agent-readable output:** prefer a generator (or plugin) that emits per-page Markdown and an `llms.txt` index at build time, over hand-maintained copies.

Record the choice and the rejected options in an ADR so the next migration debate starts from the constraints, not from taste.

---

## Pipeline Stages

| Stage | Rule |
|-------|------|
| Author | Docs live in the repo next to the code they describe; doc changes ship in the same PR as the behavior change |
| PR checks | Blocking and advisory checks per the gate policy in [documentation-testing.md](documentation-testing.md#gate-policy-block-or-warn); ready-to-use workflow in [assets/ci/docs-quality.yml](../assets/ci/docs-quality.yml) |
| PR preview | Build and deploy a preview for every docs PR; reviewers approve the rendered page, not only the Markdown diff |
| PR template | Include "docs updated / not needed because ..." so skipping docs is a stated decision, not an omission |
| Publish | Deploy from the default branch only, by CI; no manual uploads, which fork the published site from the repo |
| Ownership | CODEOWNERS entries for critical docs paths, plus the review cadence in [assets/docs-as-code/ownership-model.md](../assets/docs-as-code/ownership-model.md) |
| Analytics | Collect search queries with no results and top exit pages; they show missing and failing pages better than page views do |

---

## Versioned Docs

- Version docs only when users run multiple product versions at once (on-prem, SDKs, public APIs with supported N-1). A hosted SaaS with one live version needs one docs version plus a changelog.
- Every published version is a maintenance burden: fixes must be backported or the old version marked unmaintained. Publish a support window and drop versions that leave it.
- Point the unversioned URL at the current stable version, and make the version switcher land on the equivalent page rather than the home page.

---

## Resources

- [Write the Docs - Docs as Code](https://www.writethedocs.org/guide/docs-as-code/)
- [Diátaxis Framework](https://diataxis.fr/) - Documentation structure guide
