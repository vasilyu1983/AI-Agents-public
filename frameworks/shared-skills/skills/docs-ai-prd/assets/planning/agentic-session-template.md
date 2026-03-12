```markdown
# Agentic Session Template

*Purpose: Copy-paste template for structuring a full agentic (AI-powered or LLM-driven) coding session, ensuring safety, repeatability, and handoff quality. Use for autonomous coding tasks, multi-step GenAI workflows, or when running an agent as a “senior engineer.”*

---

## When to Use

Use this template to:
- Launch a new coding or refactor session with a coding agent (Claude Code, Copilot, Cursor, etc.)
- Structure any autonomous or semi-autonomous feature build, bug fix, or root-cause analysis
- Hand off session context between humans and agents, or between agentic runs

---

## Structure

This template has 7 sections:
1. **Session Trigger**
2. **Objectives & Metrics**
3. **Session Rules & Guardrails**
4. **Recon & Context Mapping**
5. **Action Plan**
6. **Execution & Checkpoints**
7. **Session Handoff & Retro**

---

# TEMPLATE STARTS HERE

## 1. Session Trigger

- [ ] What event or request started this session?  
  _(E.g., “Add real-time task status”, “Fix failing tests on main branch”, “Update docs after refactor”)_

---

## 2. Objectives & Metrics

- [ ] Clear session goals (feature delivered, bug fixed, tests passing, etc.)
- [ ] Success criteria/metrics (quantitative or checklist)
- [ ] Timebox/expected session duration (e.g., “30 min max”, “Until all tests pass”)

---

## 3. Session Rules & Guardrails

- [ ] Planning required before any code or files change? (Y/N)
- [ ] Maximum lines/files per action (e.g., “Do not change more than 5 files per step”)
- [ ] Command/execution limits (e.g., “All shell commands wrapped for safety”)
- [ ] No external writes, deletions, or destructive ops without explicit approval
- [ ] Ask for clarification if context/requirements are unclear

---

## 4. Recon & Context Mapping

- [ ] Inventory current files, dependencies, and key functions (auto-list OK)
- [ ] Map all relevant code/tests/docs (or attach outputs)
- [ ] Identify blockers, missing context, or unknowns before starting work

---

## 5. Action Plan

- [ ] List all steps/phases to complete goal (may update after recon)
    - Example:  
      1. Inventory code/tests  
      2. Update Task API  
      3. Add dashboard indicator  
      4. Run/test/validate  
      5. Update docs  
      6. Final QA/handoff
- [ ] Assign owner for each step (agent or human)
- [ ] Attach acceptance criteria to each phase if possible

---

## 6. Execution & Checkpoints

- [ ] Work proceeds in increments (1–2 steps at a time)
- [ ] After each increment: checkpoint, self-review, update context/docs
- [ ] Run tests and validate before moving to next phase
- [ ] QA checklist (see resources) completed at each major milestone

---

## 7. Session Handoff & Retro

- [ ] Summarize session outcome:  
    - What was completed?
    - Any remaining issues, risks, or TODOs?
    - Updated docs, context, or artifacts?
- [ ] List learnings, blockers, and process notes for next session or team
- [ ] Confirm all outputs are saved/shared for human or next agent

---

# COMPLETE EXAMPLE

## 1. Session Trigger

- Request: “Add accessibility warnings to dashboard for users with color vision deficiency”

## 2. Objectives & Metrics

- Objective: Add WCAG-compliant status warnings
- Metric: All status colors pass contrast tests; tests automated
- Timebox: 1 hour

## 3. Session Rules & Guardrails

- Planning required before changes: Yes
- Max 2 files per step
- All changes must be reversible via git
- No deletions without approval

## 4. Recon & Context Mapping

- Files: `dashboard.js`, `statusIndicator.css`, `test/dashboard.test.js`
- Context: PRD attached, agentic plan checkpointed in session doc

## 5. Action Plan

1. Inventory code & tests (agent)
2. Update status colors for contrast (agent)
3. Add test for color contrast (agent)
4. Human validates with screen reader tools
5. Update help docs (agent)
6. Final QA, push for review (human)

## 6. Execution & Checkpoints

- After each phase: run tests, checkpoint output, update session doc
- QA checklist at phase 4 and final step

## 7. Session Handoff & Retro

- Outcome: New status colors, passing contrast tests, help docs updated
- Risks: Need user feedback on live accessibility
- Docs: `/docs/accessibility-changelog.md` updated, next steps flagged for future

---

## Quality Checklist

Before finishing:
- [ ] All 7 sections filled and reviewed
- [ ] All outputs, docs, and artifacts checkpointed and saved
- [ ] No open blockers, unknowns, or incomplete phases remain
- [ ] Retro/notes provided for team or next agent
```
