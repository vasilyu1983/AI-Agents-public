```markdown
# Planning Checklist Template

*Purpose: Ready-to-use, actionable planning checklist for agentic/AI-driven or traditional software projects. Ensures every session or feature starts with clarity, risk control, and an executable plan—suitable for both human and agent workflows.*

---

## When to Use

Use this template before:
- Kicking off an agentic coding session or multi-phase project
- Starting any feature with >3 files, >2 unknowns, or architectural changes
- Major refactors, integrations, or AI-driven implementation tasks

---

## Structure

This checklist has 5 core sections:
1. **Inputs & Triggers**
2. **Goals & Outcomes**
3. **Scope & Risks**
4. **Phases & Milestones**
5. **Review & Commitment**

---

# TEMPLATE STARTS HERE

## 1. Inputs & Triggers

- [ ] Clear problem statement or PRD attached
- [ ] All stakeholders/agents identified
- [ ] Success metrics, deadlines, and business drivers listed
- [ ] Entry criteria met (see “When to use” above)
- [ ] Dependencies, prior context, or session history included

---

## 2. Goals & Outcomes

- [ ] Explicitly define desired outcomes (features, tests, deliverables)
- [ ] Success is measurable (quantified or testable)
- [ ] Non-goals or out-of-scope items listed

---

## 3. Scope & Risks

- [ ] List files/systems/components in scope
- [ ] Document known unknowns, assumptions, and external dependencies
- [ ] Identify risks (integration, agent reliability, unclear specs, etc.)
- [ ] Risk mitigation strategies or fallback options described

---

## 4. Phases & Milestones

- [ ] Break down work into increments/phases (e.g., “Phase 1: API scaffolding”)
- [ ] Assign owner (human or agent) for each phase
- [ ] Define checkpoints for review and test (QA, integration, sign-off)
- [ ] Estimated timeline for each phase

---

## 5. Review & Commitment

- [ ] Team/agent review and approval before implementation
- [ ] Commitment to update docs/context after each major phase
- [ ] QA checklists pre-attached for validation (see resources)
- [ ] Explicit sign-off or “go” before work begins

---

# COMPLETE EXAMPLE

## 1. Inputs & Triggers

- PRD: “Dashboard Status Indicator” attached
- Stakeholders: Product Owner, Agentic Dev, QA
- Success: 30% fewer support tickets by next quarter
- Deadline: Q2 release
- Dependencies: Live Task API, Color design system

## 2. Goals & Outcomes

- Add real-time status icons to dashboard
- Automated tests for all states and accessibility
- Non-goals: No mobile changes, no API redesign

## 3. Scope & Risks

- Scope: Dashboard, Task API, Agent integration
- Risks: Agent may lose context mid-session; UI edge cases
- Mitigation: Context update docs at every phase; manual QA for accessibility

## 4. Phases & Milestones

- Phase 1: Add status icons (owner: Agent)
- Phase 2: Integrate with Task API (owner: Human)
- Phase 3: Test and validate accessibility (owner: QA)
- Timeline: 2 weeks total, review after each phase

## 5. Review & Commitment

- Team review scheduled before each phase
- Docs updated in `/docs/status-dashboard.md` after every increment
- QA checklist attached for final validation
- Go decision logged in project tracker

---

## Quality Checklist

Before starting:
- [ ] All 5 sections filled and reviewed
- [ ] Inputs, risks, and milestones are specific (no “TBD”)
- [ ] QA and review steps are pre-attached
- [ ] Out-of-scope items are listed
- [ ] Docs/context are ready to update during project
```
