---
description: Curated map of all references and assets. Use when SKILL.md points here for the full list.
last_verified: 2026-09-02
status: stable
---

# Navigation Index

## Table of Contents

- [Decision, Scenarios, and Playbooks](#decision-scenarios-and-playbooks)
- [Theory Layers (foundations applied)](#theory-layers-foundations-applied)
- [Runtime, Fields, and Patterns](#runtime-fields-and-patterns)
- [Templates](#templates)
- [Members, Teams, and Automation](#members-teams-and-automation)
- [Inventory and Sources](#inventory-and-sources)

Full map of `agents-subagents/` references and assets. Use this when SKILL.md points here for the "full list."

## Decision, Scenarios, and Playbooks

- [team-selection-guide.md](team-selection-guide.md) — universal decision map, debate rules, custom team recipes (start here)
- [team-scenarios.md](team-scenarios.md) — scenario-to-team examples
- [team-prompt-patterns.md](team-prompt-patterns.md) — short-form and full-form launch prompts
- [team-coverage.md](team-coverage.md) — coverage map for team vs member vs direct use
- [universal-team-playbook.md](universal-team-playbook.md) — any-repo review cadence, intake pack, anti-patterns
- [team-lifecycle.md](team-lifecycle.md) — setup, run, and cleanup lifecycle
- [debate-quickstart.md](debate-quickstart.md) — debate setup across Claude Code, Codex, Agent Teams, plus 3-of-5, 10 debate methods, team/situation mapping
- [clarification-questions-protocol.md](clarification-questions-protocol.md) — members ask clarifying questions before fabricating detail; primary anti-slop gate
- [dynamic-team-expansion.md](dynamic-team-expansion.md) — Expertise-Gap + Expansion Request protocol: how a team pulls more members mid-task (runs after clarification)
- [game-theory-agent-teams.md](game-theory-agent-teams.md) — agent-team applied recipe layer (manifest fields, anti-patterns, checklist). Canonical 22-mechanism playbooks live in [`foundations-game-theory/assets/templates/game-theory/`](../../foundations-game-theory/assets/templates/game-theory/)
- [methods-masks-mechanisms-playbook.md](methods-masks-mechanisms-playbook.md) — operator playbook across the 10 debate methods, 7 decision masks, and 22 game-theory mechanisms: when to use, tips, traps, coefficients, composition recipes
- [mast-failure-taxonomy.md](mast-failure-taxonomy.md) — MAST cross-reference: 14 multi-agent failure modes × 3 categories with per-mode mitigations (operator-facing tip sheet lives in `traps-and-antipatterns.md`)
- [negotiation-protocol.md](negotiation-protocol.md) — ZOPA/BATNA compromise-finding for tradeoff decisions
- [multi-agent-reflexion.md](multi-agent-reflexion.md) — post-synthesis quality check via critic debate
- [purple-team-pattern.md](purple-team-pattern.md) — continuous red+blue attack-defense cycle
- [prediction-market-confidence.md](prediction-market-confidence.md) — confidence-point staking for synthesis weighting
- [context-first-protocol.md](context-first-protocol.md) — use prepared artifacts before raw repo reads (default rule for every member and team)
- [shared-context-pattern.md](shared-context-pattern.md) — pointer stub; merged into `context-first-protocol.md`
- [ooda-loop-team-cycles.md](ooda-loop-team-cycles.md) — Observe-Orient-Decide-Act applied to team review cadence and synthesis
- [principal-agent-delegation.md](principal-agent-delegation.md) — delegation boundaries, autonomy calibration, verification games
- [team-lifecycle.md](team-lifecycle.md#usefulness-review) — usefulness review: the method for deciding which teams and members to install or retire
- [team-prompt-patterns.md](team-prompt-patterns.md#ad-hoc-specialists-no-named-team) — ad-hoc specialist debate prompt when no named team fits

## Theory Layers (foundations applied)

Each file applies one `foundations-*` skill to agent orchestration. Check the
foundation's own § When to Apply gate first — its skip-conditions may route you
to a different foundation.

- [behavioral-economics-applied.md](behavioral-economics-applied.md) — cognitive biases that distort agent reasoning, member dispatch, debate dynamics, and synthesis; defensive hardening only
- [control-theory-applied.md](control-theory-applied.md) — retry/backoff, fan-out caps, circuit breakers around tool calls, termination criteria, observability requirements
- [cybernetics-vsm-applied.md](cybernetics-vsm-applied.md) — VSM role assignment, variety engineering, algedonic escalation, recursion, anti-oscillation coordination
- [decision-theory-applied.md](decision-theory-applied.md) — when to expand a team, when to stop debating, when to commit, how to break ties
- [distributed-systems-applied.md](distributed-systems-applied.md) — consensus before fan-out, idempotent tool calls, causal ordering, quorum voting, lease fencing, conflict-free shared memory
- [grounding-communication-applied.md](grounding-communication-applied.md) — handoff briefs, acceptance protocols, repair channels, presupposition audits, audience-design rewrites
- [network-science-applied.md](network-science-applied.md) — bottleneck-agent detection, topology routing, error-propagation modelling, community detection, embedding-based retrieval
- [queueing-theory-applied.md](queueing-theory-applied.md) — M/M/c concurrency caps, fork-join fan-out wave sizing, Little's Law queue depth, read-vs-write priority, USL coordination limits
- [team-theory-applied.md](team-theory-applied.md) — Marschak–Radner observation-budget sizing, organizational-form choice, value-of-communication tests, person-by-person-optimal trap
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md) — bottleneck-member identification, drum-buffer-rope dispatch sequencing, throughput accounting, policy-constraint detection
- [team-design-rationale.md](team-design-rationale.md) — theory bindings for retained team recipes and migrated expert-board modes (why each team is shaped the way it is)

## Runtime, Fields, and Patterns

- [runtime-surfaces.md](runtime-surfaces.md) — Claude Code + Codex surfaces, field mapping, SDK pointers
- [agent-tools.md](agent-tools.md) — tool, permission, MCP, memory, isolation guidance
- [agent-patterns.md](agent-patterns.md) — reviewer, implementer, researcher, verifier patterns + anti-patterns
- [harness-patterns.md](harness-patterns.md) — named harness patterns (orchestrator-worker, evaluator-optimizer, planner→generator→evaluator, manager-vs-handoff, reflection, debate-before-dispatch, blueprint) plus execution-model reference
- [skill-subagent-patterns.md](skill-subagent-patterns.md) — `skills:` preload and `context: fork` delegation
- [subagent-context-forking.md](subagent-context-forking.md) — Claude Code fork mode (`CLAUDE_CODE_FORK_SUBAGENT`, `/fork`); community-reported
- [subagents-vs-teams-architecture.md](subagents-vs-teams-architecture.md) — isolated subagents vs collaborating teams; decompose by coordination shape; community-reported
- [subagent-interruption-recovery.md](subagent-interruption-recovery.md) — recovery for interrupted or background workers
- [runtime-smoke-tests.md](runtime-smoke-tests.md) — runtime-surface confidence check
- [cost-control.md](cost-control.md) — subagent model selection, `CLAUDE_CODE_SUBAGENT_MODEL`, per-role model matrix
- [model-governance-and-maintenance.md](model-governance-and-maintenance.md) — durable per-role model policy: audit cadence, drift checks, promotion/demotion rules
- [traps-and-antipatterns.md](traps-and-antipatterns.md) — durable list of agent-design failure modes
- [initial-prompt-contract.md](initial-prompt-contract.md) — launch-prompt fields and handoff template
- [members-and-teams.md](members-and-teams.md) — canonical library structure and skill linkage rule
- [workflow-runtime.md](workflow-runtime.md) — Workflow tool runtime: gating, size guideline, caps, `agent()` options, saved-workflow locations

## Templates

Start from packaged templates before writing a new prompt:

- [agents/templates/browser-verifier.md](../../../../agents/templates/browser-verifier.md) — scoped MCP browser-verifier role
- For reviewer and implementer roles, use canonical members in [agents/claude/](../../../../agents/claude/) and [agents/codex/](../../../../agents/codex/) (e.g. `dev-feature-reviewer`, `dev-feature-implementer`, `software-security-reviewer`) — no generic templates ship for these
- [agents/templates/debate-orchestrator.md](../../../../agents/templates/debate-orchestrator.md), [agents/templates/perspective-agent.md](../../../../agents/templates/perspective-agent.md), [agents/templates/debate-synthesizer.md](../../../../agents/templates/debate-synthesizer.md)
- [agents/templates/debate-methods/](../../../../agents/templates/debate-methods/) — Six Hats, Pre-Mortem, Devil's Advocate, Steel-Manning, Dialectical, Scenario 2×2, Polarity, Courtroom, Delphi, Socratic
- [agents/templates/decision-masks/](../../../../agents/templates/decision-masks/) — Inversion, First-Principles, Regret Minimization, Second-Order

## Members, Teams, and Automation

- [agents/README.md](../../../../agents/README.md) — canonical shared member registry
- agents/teams/README.md — repository team recipes and deployment model
- [agents/workflows/](../../../../agents/workflows/) — saved Claude Code workflows (one `<id>.manifest.json` each) plus a generated Codex parent-led `<id>.codex-plan.json` for every workflow except the `validate-library` command; Claude workflows sync to `~/.claude/workflows/`, while Codex executes a plan through the `run-workflow` skill and spawn/wait/follow-up primitives
- [agents/workflows/expert-board.manifest.json](../../../../agents/workflows/expert-board.manifest.json) — canonical expert-board roster, decision controls, and property-team linkage
- [agents/workflows/expert-board.codex-plan.json](../../../../agents/workflows/expert-board.codex-plan.json) — generated Codex adapter with exact registered agent names and the same context, incident, debate, EVPI, verification, and regret gates
- [../scripts/generate_codex_expert_board_plan.py](../scripts/generate_codex_expert_board_plan.py) — regenerate or `--check` the Codex adapter against the canonical manifest and member TOMLs
- [workflow-contracts.md](workflow-contracts.md) — canonical launch, sequencing, evidence, output, and cleanup contracts for workflow and team scenarios
- [../scripts/deploy-preset.sh](../scripts/deploy-preset.sh) — install shared teams or members for Claude Code or Codex
- [../scripts/teardown-team.sh](../scripts/teardown-team.sh) — explicitly inspect and remove legacy Claude team state
- [../scripts/headless-review.sh](../scripts/headless-review.sh) — CI/CD multi-perspective code review

## Inventory and Sources

- [team-member-matrix.md](team-member-matrix.md) — reuse matrix, team→members and member→teams indexes
- [team-diagrams.md](team-diagrams.md) — auto-generated Mermaid flowchart per team (lead → members → synthesis → output, with defensive-output feedback loops)
- [startup-growth-system-diagram.md](startup-growth-system-diagram.md), [runtime-topology-diagram.md](runtime-topology-diagram.md) — system diagrams
- [../data/sources.json](../data/sources.json) — official docs and freshness links

### Maintainer note: sources duplicated across skills

Eight URLs appear in both `agents-subagents/data/sources.json` and `agents-swarm-orchestration/data/sources.json` — Claude Code subagents, Agent Teams, Codex Multi-Agents, Codex Subagents, OpenAI Agents SDK (both pages), the prompt-caching guide, and the Karpathy coding-notes thread. The duplication is intentional: each skill frames the source for a different reader (selection-side vs orchestration-side). When a URL rotates or a source is retired, update **both** files in the same commit to keep freshness aligned.
