# Doc Template Pack (Core, Non-AI)

Purpose: copy-paste templates for common internal docs (decision logs, meeting notes, changelog entries).

## Inputs

- Context and stakeholders
- Links to source artifacts (tickets, PRDs, PRs, dashboards)

## Outputs

- Consistent docs that are searchable, reviewable, and decision-oriented

## Core

## 1) Decision Log Entry

Title: {{DECISION_TITLE}}
Date: {{DATE}}
Owner: {{OWNER}}
Status: Proposed / Accepted / Rejected / Superseded

Decision:
- We will: {{DECISION}}

Context:
- Why now: {{WHY_NOW}}
- Constraints: {{CONSTRAINTS}}
- Options considered: {{OPTIONS}}

Decision rules:
- We choose this because: {{RATIONALE}}
- We will revisit if: {{REVISIT_TRIGGERS}}

Risks:
- {{RISK_1}}
- {{RISK_2}}

Links:
- Ticket/PRD: {{LINKS}}

## 2) Meeting Notes

Meeting: {{MEETING_NAME}}
Date/time: {{DATE_TIME}}
Owner: {{OWNER}}
Attendees: {{ATTENDEES}}

Goal:
- {{GOAL}}

Agenda:
- {{AGENDA}}

Notes (one idea per line):
- {{NOTES}}

Decisions:
- {{DECISIONS}}

Action items:
| Action | Owner | Due | Status |
|--------|-------|-----|--------|
| {{ACTION}} | {{OWNER}} | {{DATE}} | Not started |

Open questions:
- {{QUESTIONS}}

## 3) Changelog Entry

Release: {{VERSION_OR_DATE}}
Owner: {{OWNER}}

Added:
- {{ITEM}}

Changed:
- {{ITEM}}

Fixed:
- {{ITEM}}

Deprecated:
- {{ITEM}}

Security:
- {{ITEM}}

Links:
- PRs/issues: {{LINKS}}

## Decision Rules

- If a decision is made, it must be recorded with owner + rationale + revisit triggers.
- If a meeting creates action items, capture owner + due date in the notes.

## Risks

- Docs without owners go stale
- Meetings without decisions create churn
- Changelogs without links are not auditable

## Optional: AI / Automation

Use only if allowed by policy and data handling rules.

- Summarize long meeting transcripts into decisions/actions; humans verify accuracy.
- Draft changelog entries from PR titles; humans edit and ensure correctness.
