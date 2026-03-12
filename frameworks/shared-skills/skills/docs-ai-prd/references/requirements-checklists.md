# Requirements & Validation Checklists

*Purpose: Ready-to-use checklists for gathering, documenting, and validating requirements for AI/agentic coding projects, PRDs, and software specs. Ensures completeness, clarity, and operational QA at every stage.*

## Contents

- PRD/spec completeness
- Requirements elicitation
- Agentic validation
- Edge cases
- Acceptance criteria template

---

## Core Checklists

### 1. PRD/Spec Completeness Checklist

**Use when:** Creating or reviewing a Product Requirements Document, technical spec, or user story set.

- [ ] Problem statement is clear and unambiguous
- [ ] All key user personas/stakeholders identified
- [ ] Success metrics defined (quantitative, not just qualitative)
- [ ] Requirements categorized: Functional, Nonfunctional, Data, Constraints
- [ ] Acceptance criteria for every major requirement
- [ ] Edge cases and failure modes listed
- [ ] Out of scope items stated
- [ ] Dependencies, assumptions, and risks documented
- [ ] Test/validation plan included

---

### 2. Requirements Elicitation Checklist

**Use when:** Kicking off a project, new feature, or planning session with agents.

- [ ] Gather use cases and main user goals
- [ ] Identify business objectives and constraints
- [ ] List core user stories (“As a [role], I want to [do X] so that [goal]”)
- [ ] Break down events/triggers and expected responses
- [ ] Map data objects/entities and relationships
- [ ] Capture non-functional/quality attributes (performance, security, UX, etc.)
- [ ] Check for missing or hidden stakeholders

---

### 3. Agentic Requirements Validation Checklist

**Use when:** Reviewing AI/agent-generated PRDs, specs, or requirements.

- [ ] All agent outputs match the requested format/template
- [ ] No ambiguous, missing, or “TBD” items in requirements
- [ ] Acceptance criteria are concrete and testable
- [ ] Edge cases covered (see checklist below)
- [ ] Prompt/intent matches output (no scope drift)
- [ ] All references, links, and external dependencies cited

---

### 4. Edge Case & Completeness Checklist

**Use when:** Final validation before handoff, implementation, or QA.

- [ ] All user roles/flows represented (including admin/guest/error)
- [ ] Boundary values tested (min/max/empty/invalid input)
- [ ] Failure, rollback, and timeout behaviors defined
- [ ] Integration points (APIs, external systems) listed and validated
- [ ] All checklist items above re-checked after agentic changes or compaction

---

## Quick Reference

### Requirements QA Flow

1. Draft PRD/spec → Run Completeness Checklist
2. Elicit requirements → Elicitation Checklist
3. Generate with agent → Agentic Validation Checklist
4. Validate/test output → Edge Case & Completeness Checklist
5. Handoff or implement

---

### Acceptance Criteria Template

| Requirement           | Acceptance Criteria (Testable)                |
|-----------------------|-----------------------------------------------|
| User login            | User can log in with valid credentials        |
|                      | Error message shown on invalid login          |
| Report export         | Export completes < 2s for 95% of cases        |
|                      | PDF and CSV formats available                 |

---

## Common Mistakes

AVOID: Missing acceptance criteria for key requirements  
BEST: Ensure every major requirement has a testable acceptance criterion.

AVOID: Ambiguous problem statement or scope  
BEST: Write clear problem/user value at the top and state out-of-scope items.

AVOID: No non-functional requirements or quality attributes  
BEST: Always ask for performance, usability, security, and similar attributes.

AVOID: No documented dependencies or edge cases  
BEST: Add a table or list for dependencies and “what could go wrong”.

---

> **Pro Tip:** Use these checklists before, during, and after agentic/LLM sessions—especially if context was lost or a plan was changed mid-flight. Repeat them after every major doc or PRD/spec change.
