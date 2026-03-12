# Stakeholder Alignment for PRD Reviews

*Purpose: Operational patterns for mapping stakeholders, structuring review cycles, resolving conflicting requirements, and driving decisions to closure on PRDs and specs.*

## Contents

- Stakeholder mapping and RACI
- Async vs sync review patterns
- Conflicting requirements resolution
- Escalation paths
- Decision-log template
- Pre-review / during-review / post-review checklists
- Anti-patterns

---

## Stakeholder Mapping

### RACI for PRD Reviews

| Role | Responsible | Accountable | Consulted | Informed |
|------|:-----------:|:-----------:|:---------:|:--------:|
| Product Manager | X | X | | |
| Tech Lead / Architect | | | X | |
| Engineering Lead | X | | X | |
| Design Lead | | | X | |
| QA Lead | | | X | |
| Executive Sponsor | | X | | X |
| Legal / Compliance | | | X | |
| Customer-facing teams | | | | X |

**Use when:** Kicking off any PRD that touches more than one team or requires cross-functional sign-off.

**Rules:**
- Exactly one Accountable per PRD (the person who can unblock decisions).
- Consulted parties must respond within the review window or their silence counts as no objection.
- Informed parties receive the final version; they do not gate approval.

---

## Async vs Sync Review Patterns

### Decision Guide

| Situation | Format | Recommended Tool |
|-----------|--------|------------------|
| Minor update, <10% of PRD changed | Async comment thread | Notion, Google Docs, GitHub PR |
| New PRD, first review round | Live walkthrough (30 min) + async follow-up | Video call + shared doc |
| Conflicting feedback from 2+ stakeholders | Sync meeting with decision owner | Calendar invite, structured agenda |
| Final approval gate | Async sign-off with deadline | Notion checkbox, GitHub approve |

**Async defaults:**
- Set a review deadline (48h for standard, 24h for urgent).
- Use numbered inline comments, not DMs or side channels.
- Tag specific reviewers per section; do not assign the entire doc to everyone.

**Sync triggers:**
- Two or more Consulted parties disagree on the same requirement.
- Scope change exceeds 20% of original spec.
- Deadline is <5 business days away and feedback is incomplete.

---

## Handling Conflicting Requirements

### Prioritization Framework

When two stakeholders want incompatible things, use this decision sequence:

1. **User impact** -- Which option better serves the target persona's core job-to-be-done?
2. **Strategic alignment** -- Which option maps to the current quarter's goals or OKRs?
3. **Reversibility** -- Which option is easier to change later? Prefer the reversible path.
4. **Cost of delay** -- Which option unblocks more downstream work if shipped first?

Document the trade-off explicitly:

```markdown
### Decision: [Short title]
**Options considered:**
- A: [Description] -- favored by [Stakeholder]
- B: [Description] -- favored by [Stakeholder]

**Decision:** Option [A/B]
**Rationale:** [1-2 sentences referencing the prioritization criteria above]
**Decided by:** [Name, Role]
**Date:** YYYY-MM-DD
**Revisit trigger:** [Condition under which this decision should be reopened]
```

---

## Escalation Paths

| Stage | Who Escalates | Escalates To | Timeframe |
|-------|---------------|--------------|-----------|
| Reviewer disagrees with draft | Reviewer | PRD Author (PM) | During review window |
| Two reviewers disagree | PM | Tech Lead or Design Lead (tiebreaker) | Within 24h of conflict |
| Cross-team deadlock | PM | Executive Sponsor / VP | Within 48h |
| Compliance or legal block | PM + Legal | Executive Sponsor | Immediately |

**Rules:**
- Escalation is not failure. Unresolved ambiguity shipped to production is failure.
- Every escalation must include: the two options, the trade-off, and a recommended path.
- The escalation recipient decides or delegates within the stated timeframe.

---

## Decision-Log Template

Maintain a running decision log as a table at the bottom of the PRD or in a linked document.

| # | Decision | Options | Outcome | Owner | Date | Revisit Trigger |
|---|----------|---------|---------|-------|------|-----------------|
| 1 | Auth mechanism | OAuth2 vs API key | OAuth2 | @techlead | 2025-03-01 | If B2B-only pivot |
| 2 | MVP scope | 3 endpoints vs 5 | 3 endpoints | @pm | 2025-03-02 | Post-launch metrics |

---

## Checklists

### Pre-Review

- [ ] RACI table populated; every reviewer knows their role
- [ ] Review deadline communicated (date + time + timezone)
- [ ] PRD sections labeled with owner names for targeted feedback
- [ ] Open questions marked with `[OPEN]` tags so reviewers focus there first
- [ ] Previous decision-log entries are up to date

### During Review

- [ ] Feedback labeled by type: BLOCKER, QUESTION, SUGGESTION, NITPICK
- [ ] Conflicts surfaced immediately, not deferred to "next round"
- [ ] PM tracks all open threads; nothing is abandoned mid-conversation
- [ ] Sync meeting scheduled if async resolution stalls past 24h

### Post-Review

- [ ] All BLOCKER items resolved or escalated
- [ ] Decision log updated with outcomes from this round
- [ ] Revised PRD version shared with Informed stakeholders
- [ ] Next review round scheduled (if needed) with clear scope
- [ ] Thank reviewers and summarize what changed from their input

---

## Anti-Patterns

AVOID: **Bikeshedding** -- Spending 30 minutes debating button color while ignoring the data model.
FIX: Timebox cosmetic discussions. Route UI nitpicks to design async.

AVOID: **HiPPO (Highest Paid Person's Opinion)** -- Letting seniority override evidence.
FIX: Require every decision to reference user data, OKR alignment, or cost analysis.

AVOID: **Scope creep during review** -- Reviewers adding "while we're at it" requirements.
FIX: Log new ideas in a parking-lot section. Evaluate them in the next planning cycle, not mid-review.

AVOID: **Silent approval** -- No response treated as agreement without explicit policy.
FIX: State upfront: "No response by [deadline] = no objection." Put it in the review request.

AVOID: **Review without context** -- Sending a 20-page PRD with "please review."
FIX: Write a 3-sentence summary of what changed and what kind of feedback you need.

---

## Related Resources

- [Requirements Checklists](requirements-checklists.md) -- Validation checklists for PRD completeness
- [Traditional PRD Writing Guide](traditional-prd-writing.md) -- PRD structure and best practices
- [PM Team Collaboration Guide](pm-team-collaboration.md) -- Cross-functional team workflows
