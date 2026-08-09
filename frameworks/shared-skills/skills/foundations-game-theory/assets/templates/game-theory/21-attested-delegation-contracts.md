---
name: Attested Delegation Contracts
mechanism_id: 21
layer: routing
status: emerging
last_verified: 2026-05-08
sources:
  - https://arxiv.org/abs/2603.18043
---

# Attested Delegation Contracts — Routing Across Trust Boundaries

Delegation mechanism for subagents, tools, plugins, or external agent services that can self-report quality, capability, or identity.

## Problem

If a router selects delegates by self-claimed quality, strategic or misconfigured delegates can inflate their claims. The system then routes more work to the wrong delegate. This is a principal-agent problem: the orchestrator wants reliable work, while the delegate's claim is cheap.

## Solution

Route by attested capability and bounded contracts, not self-description.

A delegation contract states:

- objective and acceptance criteria
- authority boundary
- budget and deadline
- allowed tools / forbidden tools
- required evidence
- typed failure semantics
- recovery path

Attestation states what is verified by prior outcomes, tests, signatures, or operator approval. Self-claims may be logged, but they do not increase authority.

## When to Use

- Cross-runtime delegation: Codex to Claude, local agent to cloud agent, parent to plugin or MCP server.
- Marketplace-style agent selection where agents bid or advertise capabilities.
- External contractors, legal counsel, support bots, or customer-facing agents.
- Any team that routes high-stakes work to a dynamic or untrusted delegate.

## When NOT to Use

- Static local team with known members and no authority boundary.
- Low-stakes research fan-out where failure is cheap and obvious.
- Work whose quality is fully checked by a deterministic validator before use.

## Contract Template

```yaml
delegation_contract:
  delegate: <agent-or-tool-id>
  objective: <specific result>
  authority:
    may: [read, inspect, draft]
    must_not: [commit, send, deploy, pay, delete]
  budget:
    tokens: 12000
    wall_clock_minutes: 20
  acceptance:
    evidence_required: [tests, citations, diff, logs]
    verifier: <parent-or-reviewer>
  failure_policy:
    no_evidence: escalate
    timeout: retry_once_then_reassign
    low_confidence: return_partial_with_questions
  attestation:
    identity: verified_local_agent
    capability_basis: prior_passed_runs
    self_claims_allowed: false
```

## Agent-Team Pattern

Use this before auction routing or reputation-gated autonomy when the delegate pool includes agents outside the parent thread's direct control.

1. Filter delegates by attested capability.
2. Apply auction/routing only inside the eligible set.
3. Give the winner a bounded contract.
4. Verify output against acceptance criteria.
5. Update reputation only from verified outcomes.

## Anti-Patterns

- **Self-claimed quality routing**: "I am best at security review" is not evidence.
- **Unbounded authority**: delegate can write, send, or deploy because the brief forgot to forbid it.
- **Opaque failure**: timeout, refusal, low confidence, and tool denial all collapse into "failed".
- **Reputation laundering**: high reputation from easy tasks grants autonomy on unrelated high-risk work.

## Composition

- **Precedes G03 (Auction Routing)** when bidders are dynamic or untrusted.
- **Feeds G05 (Reputation-Gated Autonomy)** with verified outcomes.
- **Pairs with G14 (Per-Claim Credibility)** for evidence-level checking.
- **Pairs with principal-agent delegation** in `agents-subagents/references/principal-agent-delegation.md`.

## Sources

- arXiv 2603.18043 — *The Provenance Paradox in Multi-Agent LLM Routing: Delegation Contracts and Attested Identity in LDP*.
