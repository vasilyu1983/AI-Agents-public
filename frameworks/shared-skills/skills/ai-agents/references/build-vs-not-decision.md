# When NOT to Build an Agent — Decision Framework

**Purpose**: Systematic framework for evaluating whether to build an AI agent, continue development, or kill the project. Prevents wasted investment on agent projects that should never exist.

No theory. No narrative. Only decision rules.

---

## The Default Answer is NO

Building an agent should require justification, not be the default. Most tasks don't need agents.

### The 10-Second Test

Before any agent project, answer these three questions:

| Question | If NO | If YES |
|----------|-------|--------|
| 1. Is task volume >1000/month? | **Stop** — manual is cheaper | Continue |
| 2. Is human cost >$5/task? | **Stop** — agent won't beat human cost | Continue |
| 3. Can you tolerate 1-5% error rate? | **Stop** — agents can't guarantee 100% | Continue |

**If any answer is NO, don't build an agent.**

---

## Alternatives to Agents (Usually Better)

| Problem | Agent Instinct | Better Alternative | When Agent IS Better |
|---------|---------------|-------------------|---------------------|
| Answer FAQs | RAG chatbot | Static FAQ page + search | >500 unique questions |
| Route support tickets | Classification agent | Rule-based routing | >20 categories, fuzzy boundaries |
| Generate reports | Report agent | Scheduled SQL queries + templates | Ad-hoc, natural language queries |
| Monitor systems | Alert agent | Prometheus + PagerDuty rules | Requires judgment/synthesis |
| Write code | Coding agent | IDE snippets + copilot | Multi-file refactors, novel tasks |
| Process documents | Doc extraction agent | Regex + templates | Unstructured, variable formats |
| Personalize content | Recommendation agent | Collaborative filtering | Cold start, explanation needed |

### Decision Rule

```text
Use agent ONLY when:
  (Task requires reasoning OR judgment OR multi-step planning)
  AND
  (Volume justifies development cost)
  AND
  (Error tolerance exists)
```

---

## Red Flags — Don't Build If True

### Immediate Disqualifiers

| Red Flag | Why | Alternative |
|----------|-----|-------------|
| **"Make it feel human"** | Agents are tools, not personas | Clear bot UI, fast handoff to humans |
| **"Replace X employees"** | Agents augment, not replace | Augmentation use case |
| **"Handle everything"** | Unbounded scope = unbounded failure | Narrow, well-defined tasks |
| **"Zero errors allowed"** | Agents hallucinate | Human-in-the-loop or don't automate |
| **"We have no data"** | Nothing to retrieve or learn from | Build data pipeline first |
| **"Users don't know what they want"** | Garbage prompts = garbage output | Better UX, not AI |
| **"Legal/medical/financial advice"** | Liability + accuracy requirements | Human review mandatory |

### Organizational Red Flags

| Red Flag | Problem | Resolution Before Building |
|----------|---------|---------------------------|
| No success metrics defined | Can't prove value | Define KPIs first |
| No owner for agent quality | Quality will degrade | Assign ownership |
| Engineering team at capacity | Maintenance will fail | Staff appropriately |
| Data governance unclear | Privacy/compliance risk | Resolve governance first |
| No budget for LLM costs | Will get killed when bill arrives | Secure budget commitment |

---

## The Full Decision Framework

### Stage 1: Problem Validation (Week 1)

| Checkpoint | Pass Criteria | Fail Action |
|------------|---------------|-------------|
| Problem exists | >10 users report pain point | Find real problem |
| Problem is frequent | >100 occurrences/month | Too rare for automation |
| Problem is expensive | >$5 human cost per occurrence | Too cheap to automate |
| Problem is solvable by AI | Reasoning/language task | Use traditional automation |
| Problem is well-defined | Clear input/output spec | Define scope first |

**Gate**: Must pass ALL checkpoints to proceed.

### Stage 2: Feasibility Assessment (Week 2)

| Checkpoint | Pass Criteria | Fail Action |
|------------|---------------|-------------|
| Data available | >1000 relevant examples | Build data pipeline first |
| Data quality >80% | Spot-check 50 samples | Clean data first |
| Success is measurable | Concrete metric exists | Define metrics |
| Error tolerance exists | Can accept 1-5% errors | Don't automate |
| Baseline exists | Human performance measured | Measure baseline first |

**Gate**: Must pass ALL checkpoints to proceed.

### Stage 3: Economics Validation (Week 3)

| Checkpoint | Pass Criteria | Fail Action |
|------------|---------------|-------------|
| Projected ROI >100% | (Value - Cost) / Cost | Reduce scope or abandon |
| Payback <12 months | Dev cost / monthly savings | Reduce dev cost or abandon |
| LLM cost <50% of human cost | Token estimate vs human cost | Use cheaper model or abandon |
| Maintenance sustainable | <20% of dev time ongoing | Simplify or abandon |

**Gate**: Must pass ALL checkpoints to proceed.

### Stage 4: Risk Assessment (Week 4)

| Checkpoint | Pass Criteria | Fail Action |
|------------|---------------|-------------|
| Hallucination impact <$100/incident | Risk assessment | Add guardrails or don't build |
| No regulatory blockers | Legal review | Don't build or heavy HITL |
| No reputational risk | PR review | Don't build or don't ship |
| Failure mode acceptable | Graceful degradation possible | Don't build |
| Rollback possible | Can disable instantly | Build kill switch |

**Gate**: Must pass ALL checkpoints to proceed.

---

## Kill Triggers (Stop Immediately)

### During Development

| Trigger | Threshold | Action |
|---------|-----------|--------|
| 3 pivots on core approach | After 3 fundamental changes | Kill project |
| Prototype accuracy <60% | After 2 weeks of tuning | Kill project |
| Scope creep >2x original | Features doubled without ROI recalc | Kill or rescope |
| Key assumption invalidated | Discovery contradicts premise | Kill project |
| Team loses faith | >50% of team thinks it won't work | Kill project |

### Post-Launch

| Trigger | Threshold | Measurement Period | Action |
|---------|-----------|-------------------|--------|
| ROI negative | <0% | After 3 months | Kill |
| Adoption <20% | Active users / eligible | After 1 month | Kill or major pivot |
| Error rate >10% | After tuning attempts | After 2 iterations | Kill |
| LLM costs >3x projection | Sustained | 2 months | Kill or restructure |
| Support tickets increasing | Week over week | 4 weeks | Kill or fix root cause |
| User satisfaction <3/5 | CSAT score | After 1 month | Kill or major fix |

---

## Decision Tree: Build vs Not

```text
START: "Should we build an agent for X?"
│
├─ Is X a reasoning/language task?
│   ├─ No → USE TRADITIONAL AUTOMATION
│   └─ Yes ↓
│
├─ Is task volume >1000/month?
│   ├─ No → DON'T BUILD (manual is cheaper)
│   └─ Yes ↓
│
├─ Is human cost >$5/task?
│   ├─ No → DON'T BUILD (agent won't beat cost)
│   └─ Yes ↓
│
├─ Can you tolerate 1-5% errors?
│   ├─ No → DON'T BUILD (or heavy HITL)
│   └─ Yes ↓
│
├─ Do you have >1000 examples?
│   ├─ No → BUILD DATA PIPELINE FIRST
│   └─ Yes ↓
│
├─ Is projected ROI >100%?
│   ├─ No → REDUCE SCOPE or DON'T BUILD
│   └─ Yes ↓
│
├─ Is hallucination cost <$100/incident?
│   ├─ No → ADD GUARDRAILS or DON'T BUILD
│   └─ Yes ↓
│
└─ BUILD THE AGENT
    │
    └─ Monitor kill triggers weekly
```

---

## Common Anti-Patterns (Avoid These)

### "The AI Hammer"

| Anti-Pattern | Example | Correct Approach |
|--------------|---------|------------------|
| AI for everything | "Let's AI-enable our settings page" | Only AI where reasoning needed |
| Agent for simple lookup | "Agent to check order status" | Database query + template |
| Agent for static content | "Agent to explain pricing" | FAQ page |
| Agent for auth/payments | "Agent to process refunds" | Secure API, not LLM |

### "The Scope Creep"

| Anti-Pattern | Example | Correct Approach |
|--------------|---------|------------------|
| "While we're at it..." | "Also handle complaints, sales, HR..." | One use case, prove ROI, then expand |
| "Make it smarter" | "Understand context from 6 months ago" | Narrow context window |
| "Proactive outreach" | "Agent should reach out when..." | Bounded, triggered actions only |

### "The Perfection Trap"

| Anti-Pattern | Example | Correct Approach |
|--------------|---------|------------------|
| "Must be 100% accurate" | "Can't ship until zero errors" | Define acceptable error rate |
| "Must pass all edge cases" | "Handle every possible input" | 80/20 rule, escalate edge cases |
| "Must be indistinguishable from human" | "Users shouldn't know it's AI" | Transparency is better |

---

## Checklist: Pre-Build Validation

Copy this checklist before starting any agent project:

```markdown
## Pre-Build Validation Checklist

### Problem Definition
- [ ] Problem clearly defined in writing
- [ ] >10 users experiencing this pain point
- [ ] Frequency: >1000 tasks/month
- [ ] Human cost: >$5/task
- [ ] Error tolerance: 1-5% acceptable

### Data Readiness
- [ ] >1000 relevant examples available
- [ ] Data quality spot-checked (>80% usable)
- [ ] Data pipeline exists or budgeted

### Economics
- [ ] ROI projection completed (target: >100%)
- [ ] LLM cost estimate (monthly + per-task)
- [ ] Development cost estimate
- [ ] Maintenance cost estimate (20-40% of dev)
- [ ] Budget secured and approved

### Risk Assessment
- [ ] Hallucination impact assessed (<$100/incident OK)
- [ ] Legal review completed (if applicable)
- [ ] Graceful degradation designed
- [ ] Kill switch mechanism planned
- [ ] Rollback procedure documented

### Organizational
- [ ] Success metrics defined
- [ ] Owner assigned
- [ ] Maintenance team identified
- [ ] Stakeholder alignment confirmed

### Final Gate
- [ ] All boxes checked above
- [ ] Alternative solutions evaluated and rejected
- [ ] Sponsor sign-off obtained

**DECISION**: [ ] BUILD  [ ] DON'T BUILD  [ ] NEED MORE INFO
```

---

## Related References

- [Agent Economics](agent-economics.md) — ROI calculations and cost framework
- [Agent Maturity & Governance](agent-maturity-governance.md) — Rollout risk assessment
- [Deployment, CI/CD & Safety](deployment-ci-cd-and-safety.md) — Production guardrails
