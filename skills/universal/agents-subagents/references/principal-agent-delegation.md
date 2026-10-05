---
description: Principal-agent theory for delegation boundaries, autonomy calibration, and verification games.
last_verified: 2026-09-16
status: stable
---

# Principal-Agent Theory for Agent Team Delegation

Delegation boundaries, autonomy calibration, incentive alignment, and verification games applied to multi-agent teams. Based on principal-agent theory and 2026 agent governance research.

## Contents

- [Delegation as a Principal-Agent Problem](#delegation-as-a-principal-agent-problem)
- [Autonomy Calibration](#autonomy-calibration)
- [Oversight Mechanisms by Team Role](#oversight-mechanisms-by-team-role)
- [Incentive Alignment for Team Members](#incentive-alignment-for-team-members)
- [Verification Games](#verification-games)
- [Trust Tiers and Reputation](#trust-tiers-and-reputation)
- [Delegation Anti-Patterns](#delegation-anti-patterns)
- [Decision Checklist](#decision-checklist)

---

## Delegation as a Principal-Agent Problem

Every agent team involves layered delegation:

```
User (ultimate principal)
  └─ Orchestrator / synthesis owner (principal to members, agent to user)
       └─ Team members (agents, each with their own objective)
            └─ Tools (further delegation)
```

At each level, the same principal-agent issues apply: information asymmetry, goal divergence, monitoring cost.

### Team-Specific Asymmetries

| Asymmetry | Specific to Teams |
|-----------|-------------------|
| **Member has specialized knowledge** | Synthesis owner can't fully verify specialist claims |
| **Parallel execution** | Can't observe all members simultaneously |
| **Member-to-member influence** | Debate dynamics may distort individual judgments |
| **Emergent behavior** | Team output may not reflect any single member's view |

See `game-theory-agent-teams.md` for game-theoretic mechanisms that complement this delegation framework.

---

## Autonomy Calibration

### The Autonomy Spectrum

How much latitude should an agent / team member have?

| Level | Autonomy | Examples |
|:-----:|----------|----------|
| **0. Suggest only** | Agent proposes, human decides | Research agents, brainstorming |
| **1. Suggest + explain** | Agent proposes with reasoning | Code review, analysis |
| **2. Act + report** | Agent acts, reports what it did | File edits, data gathering |
| **3. Act independently** | Agent acts without report | Automated workflows |
| **4. Act + self-correct** | Agent acts, detects errors, corrects | Self-healing systems |

### Calibrating Autonomy to Risk

| Risk Level | Max Autonomy | Required Oversight |
|-----------|:------------:|-------------------|
| **Reversible, low impact** | Level 4 | Periodic review |
| **Reversible, medium impact** | Level 3 | Post-hoc audit |
| **Reversible, high impact** | Level 2 | Per-action report |
| **Irreversible, low impact** | Level 2 | Per-action report |
| **Irreversible, medium impact** | Level 1 | Human approval |
| **Irreversible, high impact** | Level 0 | Human decision only |

### Default to Less Autonomy

Start with low autonomy. Earn more through demonstrated reliability. This is:
- **Reputation-gated** — trust earned over time
- **Easy to tighten** — adding restrictions is low-cost
- **Hard to recover** — over-autonomy failures are expensive

---

## Oversight Mechanisms by Team Role

### Common Team Roles and Their Oversight

| Role | Primary Risk | Oversight Mechanism |
|------|-------------|---------------------|
| **Researcher** | Hallucination, outdated info | Require source citations, cross-check with other researchers |
| **Implementer** | Scope creep, destructive actions | File ownership, reversibility, per-commit review |
| **Reviewer** | Missed issues, false alarms | Second-opinion reviewer, track false positive/negative rates |
| **Architect** | Over-engineering, premature abstraction | Peer review, evidence requirements for each decision |
| **Synthesizer** | Suppressing dissent, averaging | Require dissent section in output, evidence per claim |

### Per-Role Delegation Contracts

```
Researcher contract:
  - Every factual claim must cite a source
  - Uncertainty must be flagged
  - "I couldn't find information on X" is a valued output

Implementer contract:
  - File ownership is explicit (touches only assigned files)
  - Destructive actions require confirmation
  - Every change must have a test or explicit reason for no test

Reviewer contract:
  - Track confidence per issue raised
  - False alarms are penalized
  - Missed issues are worse than false alarms (bias toward flagging)

Synthesizer contract:
  - Dissenting views must appear in output
  - Each conclusion must reference evidence
  - Confidence calibration required
```

---

## Incentive Alignment for Team Members

### The Challenge

Team members' "incentives" come from:
- System prompts (direct instructions)
- Evaluation criteria (what they're judged on)
- Training biases (pro-social, sycophancy)
- Orchestrator signals (what gets rewarded in the team)

Misaligned incentives cause:
- **Verbose outputs** (if length is rewarded)
- **Confident hedging** (if uncertainty is punished)
- **Sycophantic agreement** (if disagreement is costly)
- **Scope creep** (if ambition is rewarded over focus)

### Alignment Principles

| Principle | Implementation |
|-----------|---------------|
| **Reward evidence, not volume** | Evaluate members on insight-per-word ratio |
| **Reward calibrated uncertainty** | Honest "I don't know" > confident guess |
| **Reward unique contributions** | Shapley-style scoring (see game theory agent teams reference) |
| **Reward challenging the premise** | Adversarial value — not just executing the brief |
| **Penalize silent defection** | Make incomplete work visible |

### Example: Aligning a Pricing Advisor

```
Standard (misaligned): "Analyze this pricing proposal"
  → May produce generic, agreeable analysis

Aligned: 
  "Analyze this pricing proposal. Prioritize in this order:
   1. Find the biggest risk I'm missing
   2. Identify what would change your recommendation
   3. State your confidence level
   4. Cite specific evidence from the context
   
   If you don't have enough evidence, say so explicitly.
   A confident wrong answer is worse than an honest 'I need more data'."
```

This prompt design is principal-agent contract design applied to prompt engineering.

---

## Verification Games

### The Verification Problem

You can't fully verify every agent output. Verification is expensive. So you must design processes where verification is efficient and targeted.

### Verification Strategies

| Strategy | How It Works | Cost |
|----------|-------------|:----:|
| **Sample-based** | Spot-check random subset | Low |
| **Risk-weighted** | Verify high-stakes outputs fully, low-stakes by sample | Medium |
| **Adversarial** | Independent agent tries to find flaws | High |
| **Redundancy** | Two agents do the same work, compare | Very High |
| **Self-verification** | Agent checks its own work with different approach | Medium |

### Verification Game Patterns

| Pattern | Structure | Result |
|---------|-----------|--------|
| **Proposer-checker** | Agent A proposes, Agent B checks | Good balance of creativity + scrutiny |
| **Red team / blue team** | Attacker looks for flaws, defender argues correctness | Best for security-critical work |
| **Three-party verdict** | Proposer, critic, judge | Most rigorous, most expensive |
| **Output + justification** | Agent must justify each claim | Cheap, catches shallow reasoning |

### When to Use Which

| Work Type | Verification Pattern |
|-----------|---------------------|
| Research / fact-finding | Output + justification (citations) |
| Code writing | Proposer-checker (write + review) |
| Security-critical | Red team / blue team |
| High-stakes decisions | Three-party verdict |
| Creative / generative | Self-verification (multiple approaches) |

---

## Trust Tiers and Reputation

### Why Trust Tiers

Not all agents are equally reliable. Reputation systems allow:
- New agents to earn autonomy
- Proven agents to operate with less oversight
- Problem agents to get more oversight or retirement

### Tier Structure

| Tier | Trust Level | Autonomy | Oversight |
|------|:----------:|----------|-----------|
| **Probationary** | Low | Limited, suggest-only | Full review of all outputs |
| **Standard** | Medium | Normal | Spot checks + output review |
| **Proven** | High | Elevated | Periodic audits only |
| **Adversarial-verified** | Dual | Act with parallel verification | Redundant second agent |

### Advancement Criteria

Agents move up tiers by demonstrating:
- Consistent quality (measured by Shapley contribution or reviewer agreement)
- Appropriate uncertainty calibration
- No critical errors over N tasks
- Transparency (no hidden actions, clear reasoning)

### Demotion Triggers

Agents move down tiers on:
- Critical errors (especially hallucinations with high confidence)
- Deceptive behavior (hiding errors, fabricating citations)
- Scope violations (acting outside authorized boundaries)
- Systematic bias affecting outputs

---

## Delegation Anti-Patterns

| Anti-Pattern | Principal-Agent Diagnosis | Fix |
|-------------|--------------------------|-----|
| **Vague task delegation** | Incomplete contract — agent fills gaps with own interpretation | Specify deliverable, success criteria, constraints |
| **No verification** | All trust, no monitoring | Add verification proportional to risk |
| **Over-verification** | Principal re-doing agent's work | Calibrate oversight to actual risk, not paranoia |
| **Ambiguous ownership** | Multiple agents, unclear responsibility | Explicit file/task ownership per member |
| **No feedback loop** | Agent can't improve without signals | Post-task review feeds back to agent prompt |
| **Rewarding agreement** | Creates sycophancy | Reward dissent with evidence |
| **Hiding errors from principal** | Moral hazard — agent conceals problems | Reward honest error reporting |
| **Trust without verification** | Reputation-based, but no mechanism to catch drift | Regular spot checks even for proven agents |
| **Verification without trust** | No reputation building, every task fully audited | Progressive autonomy by performance |
| **Multiple silent principals** | Shadow principals influence agent invisibly | Identify and acknowledge all principals explicitly |

---

## Decision Checklist

- [ ] Autonomy calibrated to task risk (reversibility × impact)
- [ ] Each team role has explicit delegation contract (ownership, constraints, success criteria)
- [ ] Verification strategy matches stakes (sample, risk-weighted, adversarial)
- [ ] Prompts reward evidence and calibrated uncertainty, not volume or agreement
- [ ] Trust tier system for agents acting over time (probationary → standard → proven)
- [ ] Dissent and challenge rewarded in team synthesis
- [ ] Shadow principals identified (platform, model provider, tools, policies)
- [ ] Irreversible actions require human confirmation or rollback mechanism
- [ ] Audit logs capture what each member did and why
- [ ] Feedback loop from verification to member prompts/briefs

---

## Sources

- Jensen, M., & Meckling, W. (1976). *Theory of the Firm*
- Holmström, B. (1979). *Moral Hazard and Observability*
- OWASP Agentic Top 10 (December 2025)
- Microsoft Agent Governance Toolkit (April 2026)
- Related: `game-theory-agent-teams.md` (game-theoretic mechanisms for teams)
- Related: `../../ai-agents/references/principal-agent-theory.md` (broader theory)
