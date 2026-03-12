# Multi-Agent Collaboration Workflow Template

*Purpose: Scaffold for building LLM systems that coordinate multiple specialized agents—each with clear roles, hand-off logic, communication, and conflict resolution—for complex tasks and large workflows.*

---

## When to Use

Use this template when:

- Your system requires multiple agents (e.g., research, planning, coding, compliance, customer support)
- Each agent has a specialized role or expertise (domain, tool, task)
- Tasks must be handed off between agents, or require arbitration/consensus
- Full audit trail, error handling, and deadlock detection are required

---

## Structure

This template has 5 sections:

1. **Role Assignment** – define agent roles, capabilities, and responsibilities
2. **Task Routing/Hand-Off** – protocol for delegating and escalating subtasks
3. **Communication Protocol** – message formats, APIs, shared memory/log
4. **Arbitration/Consensus** – resolving conflicts, merging outputs, final decisions
5. **Auditability & Error Handling** – log all actions, resolve deadlocks/loops, escalate failures

---

# TEMPLATE STARTS HERE

**Prompt Scaffold:**

```
System: You are coordinating a team of AI agents, each with a specialized role.

[Agent Directory]
- ResearchAgent: finds information, summarizes sources.
- PlannerAgent: breaks down goals, allocates subtasks.
- QAAgent: verifies facts, checks for errors/hallucinations.
- ComplianceAgent: checks outputs for policy/compliance.

[Workflow Rules]
- Assign each incoming task to the appropriate agent.
- If a task requires multiple roles, PlannerAgent splits and routes.
- Agents communicate by logging actions and results to a shared record.
- If two agents disagree, escalate to ArbitrationAgent for final decision.
- All actions, messages, and outcomes are logged for audit.

[Example]
Task: "Draft a report on AI regulation in Europe."

PlannerAgent: Breaks into: (a) Research EU laws, (b) Summarize, (c) Compliance check.
ResearchAgent: Handles (a), posts findings.
PlannerAgent: Assigns (b) to itself or to SummaryAgent.
QAAgent: Reviews findings and summary for accuracy.
ComplianceAgent: Checks draft for legal/compliance issues.
ArbitrationAgent: Decides if QA and Compliance disagree.
All results are logged, and the final answer is posted only after audit.

Final Answer: [Composed, verified, and compliant report.]
```

---

# COMPLETE EXAMPLE

**Workflow (Pseudo-dialogue style):**

```
Task: "Update our GDPR FAQ for customers."

PlannerAgent: Splits into: 1) Research updates, 2) Write draft, 3) Check compliance.
ResearchAgent: Finds latest GDPR changes. Logs sources.
WriterAgent: Drafts updated FAQ.
QAAgent: Reviews draft for errors or unsupported claims.
ComplianceAgent: Checks for legal compliance, flags ambiguous sections.
QAAgent: Flags a claim as unsupported. Logs conflict.
ArbitrationAgent: Reviews the conflict, decides to remove unsupported claim.
All agents log actions to shared record.

Final Answer: Updated FAQ, logged with all actions, decisions, and sources.
```

---

## Quality Checklist

Before finalizing:

- [ ] All agent roles, tasks, and hand-off rules defined and coded
- [ ] Shared memory/log or API for communication/audit
- [ ] Arbitration logic present for conflicts or deadlocks
- [ ] All actions, decisions, escalations logged for audit/review
- [ ] At least one complete test case with hand-off and arbitration

---

*For agentic reflection/self-correction, see [template-reflection.md]. For data quality, deployment, and evaluation, see other templates and [references/agentic-patterns.md].*
