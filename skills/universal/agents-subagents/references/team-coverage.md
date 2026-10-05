---
description: Coverage map for team vs. member vs. direct-use selection.
last_verified: 2026-09-11
status: stable
---

# Team Coverage Map

Use this reference to decide whether a shared skill should become:

- a **team-backed workflow**
- a **member-only reusable specialist**
- a **direct-use skill**

The goal is broad reusable coverage, not turning every skill into a team.

## Table of Contents

- [Team-Backed Families](#team-backed-families)
- [Workflow-Backed Review Families](#workflow-backed-review-families)
- [Member-Only Reusable Specialists](#member-only-reusable-specialists)
- [Direct-Use Skill Families](#direct-use-skill-families)
- [Canonical Rules](#canonical-rules)

## Team-Backed Families

These families keep a dedicated repository team recipe because their members edit files, own write scopes, or need Codex parity through installed named agents. The YAML recipes select roles and launch policy; neither runtime reads them as native configuration. A family whose members only read and hand back a memo belongs in the workflow-backed table below, not here.

| Family | Team | Primary Skills |
|--------|------|----------------|
| Code review | `software-code-review-board` | `software-code-review`, `software-security-appsec`, `software-performance`, `qa-testing-strategy` |
| Feature delivery | `dev-feature-delivery` | `dev-context-engineering`, `software-clean-code-standard`, `qa-refactoring`, `software-code-review` |
| Context preparation | `dev-context-preparation` | `dev-context-engineering`, `dev-context-multi-repo`, `dev-context-code-graph`, `docs-codebase` |
| Migration planning | `dev-migration-map` | `dev-context-multi-repo`, `dev-context-code-graph`, `dev-dependency-management`, `qa-refactoring` |
| AI knowledge bot delivery | `ai-knowledge-bot-builder` | `ai-bot-builder`, `ai-context-layer`, `ai-rag`, `ai-agents` |
| Docs and knowledge | `docs-knowledge` | `docs-codebase`, `docs-ai-prd`, `docs-notes-retrieval`, `qa-docs-coverage` |
| Product surface | `product-surface` | `software-frontend`, `software-ui-ux-design`, `software-accessibility`, `software-localisation`, `qa-testing-accessibility` |

## Workflow-Backed Review Families

Bounded review panels use the canonical `expert-board` contract instead of an
installable team recipe. Claude runs it as a saved workflow; Codex runs the
generated parent-led adapter. Its `board` argument selects the panel, named
members run first, and embedded role briefs are only the unavailable-agent
fallback.

| Family | `expert-board` mode | Primary Skills |
|--------|---------------------|----------------|
| Idea and product evaluation | `idea-evaluation` | product strategy, pain-point discovery, competition, architecture, cost |
| Startup growth and market penetration | `growth` | startup growth, GTM, product analytics, product marketing |
| Startup blind-spot discovery | `founder-blindspot` | pain-point scanning, review mining, market intel, idea validation |
| Startup monetization | `monetization` | business models, product analytics, CRO, startup operations |
| Architecture and RFC review | `architecture-rfc` | solution architecture, API design, data architecture, software risk |
| Incident review | `incident` | incident response, debugging, observability, resilience |
| Release gating | `release-readiness` | testing strategy, runbook coverage, performance, rollback planning |
| Marketing diagnostics | `marketing-diagnostics` | product analytics, SEO, AEO/GEO, growth |
| Enterprise readiness | `enterprise-readiness` | compliance readiness, security, customer operations, startup operations |
| Startup strategy | `startup-strategy` | `startup-*`, `marketing-cro`, `software-ui-ux-design` |
| Growth and experimentation | `growth-experiments` | `startup-growth-execution`, `marketing-cro`, `marketing-paid-advertising`, `marketing-product-analytics` |
| Product discovery | `product-discovery` | `product-management`, `software-ux-research`, `startup-market-intel`, `marketing-product-analytics` |
| AI systems | `ai-systems` | `ai-agents`, `ai-context-layer`, `ai-rag`, `ai-coding-agents-observability-evals`, `qa-agent-testing` |
| Data and analytics | `data-analytics` | `data-analytics-engineering`, `data-sql-optimization`, `data-streaming`, `data-lake-platform`, `marketing-product-analytics` |
| Platform ops | `ops-platform` | `ops-devops-platform`, `ops-cost-optimization`, `qa-observability`, `qa-resilience` |
| Payments | `payments-platform` | `software-payments`, `startup-operating-system`, `software-security-appsec`, `qa-security-testing` |
| Mobile product | `mobile-product` | `software-mobile`, `software-ios-native`, `software-ios-design`, `software-android-native`, `software-android-design`, `qa-testing-mobile` |

## Member-Only Reusable Specialists

These domains are reusable enough to justify canonical members, but not broad enough to justify their own team right now.

| Skill Family | Why it stays member-only |
|-------------|--------------------------|
| `software-search` | Useful in larger engineering flows, but not a recurring 4-role team workflow yet |
| `software-realtime` | Often part of architecture or feature work, not a standalone team |
| `software-email-engineering` | Important specialist input, usually one reviewer inside a larger delivery team |
| `software-ai-integration` | Broad implementation specialty that plugs into feature or architecture teams |
| `software-devtools` | Reusable specialist for DX/CLI/SDK work, but not yet a common cross-functional team |
| `software-baas-platforms` | Usually a decision input for architecture or startup-strategy teams |
| `software-desktop` | Valuable specialist, but lower-frequency than web/mobile in this library |
| `software-crypto-web3` | Domain-specific specialist rather than a generic reusable team |
| `software-workflow-automation` | Usually one specialist advising an operations or product workflow |
| `dev-workflow-planning` | Better as a planner skill or orchestration aid than a standing team |
| `dev-git-workflow` | Usually a governance input inside release, migration, or platform work |
| `dev-ai-coding-metrics` | Useful as an evaluation/ROI specialist inside AI or engineering ops work |
| `startup-fundraising` | Important, but usually one advisor within a broader startup-strategy decision process |
| `startup-operating-system` | Reusable advisor, but not yet a repeated multi-role workflow |
| `marketing-pr-communications` | Distinct specialist, often composed into launch or brand work rather than a permanent team |

## Direct-Use Skill Families

These should stay as direct-use skills unless a future request proves a repeated collaborative workflow.

| Family | Default Position |
|--------|------------------|
| `document-*` | Direct-use only. File-format and automation specific. |
| `huggingface-*` | Direct-use only. Tool- and platform-specific ML workflows. |
| `project-*` | Direct-use only. Project-scoped and intentionally isolated from general teams. |
| `router-*` | Direct-use only. Routing logic, not domain teams. |
| `agents-*` except `agents-subagents` and `agents-swarm-orchestration` | Direct-use only. Meta-operational skills, not product/domain teams. |
| Platform-specific creator workflows such as `gamedev-roblox` and `gamedev-godot` | Direct-use only unless repeated delivery work proves a need for a broader game-production team. |
| Narrow utilities and format helpers | Direct-use only unless they become repeated multi-role workflows. |

## Canonical Rules

1. `agents/` is the source of truth for reusable roles.
2. `agents/teams/*/team.yaml` should reference canonical member ids, not duplicate role definitions.
3. A new team is justified only when the workflow repeatedly needs 3-5 specialists with clear handoff boundaries.
4. Debate remains an overlay, not a permanent team shape.
5. A project-specific skill should not be promoted into a general team.
6. Teams inherit skill linkage through member definitions. The skill ids should map to `skills/*`; Claude uses `skills:` directly, while Codex installs can derive `[[skills.config]]` from the same mapping when the referenced skill paths are available.

## Explicit Coverage Decisions — 2026-09-11

The following bindings apply to both canonical Claude and Codex members. A link supplies domain guidance; the member role and launch brief retain their narrower output and permission boundaries. No additional team is created.

| Skill | Member / direct use | Scope rationale |
|---|---|---|
| `research-scout` | `dev-feature-researcher` | For paper or method discovery, return applicability and reproducibility evidence using research-scout or research-arxiv-scout; preserve attribution and never treat a benchmark as product validation. |
| `research-arxiv-scout` | `dev-feature-researcher` | For paper or method discovery, return applicability and reproducibility evidence using research-scout or research-arxiv-scout; preserve attribution and never treat a benchmark as product validation. |
| `software-baas-platforms` | `software-solution-architect` | For managed backend choice, realtime state/transport, or desktop stack selection, use the matching linked skill for an architecture recommendation; implementation and packaging remain with an explicitly assigned delivery worker. |
| `software-realtime` | `software-solution-architect` | For managed backend choice, realtime state/transport, or desktop stack selection, use the matching linked skill for an architecture recommendation; implementation and packaging remain with an explicitly assigned delivery worker. |
| `software-desktop` | `software-solution-architect` | For managed backend choice, realtime state/transport, or desktop stack selection, use the matching linked skill for an architecture recommendation; implementation and packaging remain with an explicitly assigned delivery worker. |
| `software-ai-integration` | Direct use (named in the `dev-feature-implementer` launch prompt when the assigned files need it) | Stack-specific; not preloaded into the generic implementer so every launch does not pay for it. |
| `software-csharp-backend` | Direct use (named in the `dev-feature-implementer` launch prompt when the assigned files need it) | Stack-specific; not preloaded into the generic implementer so every launch does not pay for it. |
| `software-devtools` | `dev-api-designer` | Use software-devtools for SDK/client contracts, CLI interface semantics, and distribution compatibility recommendations; do not implement or publish tools. |
| `software-crypto-web3` | `software-security-reviewer` | Use software-crypto-web3 when reviewing contracts, signing/custody, or bridges; scope findings to demonstrated exploit paths and missing specialist evidence. Do not deploy contracts, sign transactions, or claim a formal audit from this review. |
| `software-ios-ai-engine` | `software-ios-specialist` | Use software-ios-ai-engine for local model capability checks, structured context, and cloud fallback review; preserve the target OS/device assumptions and read-only role. |
| `software-paas-hosting` | `ops-platform-engineer` | Use software-paas-hosting for managed compute selection and operating tradeoffs; return a recommendation without provisioning or deploying infrastructure. |
| `startup-international-expansion` | `startup-business-developer` | Use startup-international-expansion for target-market economics and entry-model comparisons; identify regulatory unknowns for qualified review and do not approve market entry or contact counterparties. |
| `startup-exit-board-governance` | Direct use | Founder/board-facing control, crisis and exit dossier spans governance and legal escalation; the lead runs the decision workflow directly and requests bounded financial/legal input without delegating board authority to a generic finance reviewer. |

Direct-use declarations and their per-skill reasons live in `../../../../scripts/checks/audit-config.json`. They are ownership decisions, not scenario exemptions or evidence of runtime deployment.
