```markdown
# Technical Specification Template

*Purpose: Copy-paste template for a concise, operational technical spec for GenAI/agentic or standard software projects. Use this to define system design, data flows, interfaces, and validation/monitoring plans before implementation begins.*

---

## When to Use

Use this template when:
- Detailing how a feature/requirement from the PRD will be built
- Specifying system changes for agentic/AI-driven implementations
- Aligning engineers, agents, and reviewers on architecture, APIs, data flows, and QA

---

## Structure

This template has 6 sections:
1. **Overview**
2. **Architecture & Data Flow**
3. **APIs & Interfaces**
4. **Error Handling & Edge Cases**
5. **Validation & Monitoring**
6. **Risks & Rollback**

---

# TEMPLATE STARTS HERE

## 1. Overview

_1–2 sentences: What is being built? What problem/requirement does it address?_

> Example:  
> Implement a new `/status` API endpoint that returns all user task statuses in real time, supporting the dashboard status indicator PRD goal.

---

## 2. Architecture & Data Flow

**Diagram or list showing components and data flow.**  
_Specify how agents, LLMs, or system modules interact, what data moves where, and key transformations._

> Example:
- Client → `/status` API → Task service → DB
- LLM/agent updates data via `/update-task` webhook

---

## 3. APIs & Interfaces

| Name         | Endpoint/Method          | Input                  | Output                 | Notes                |
|--------------|--------------------------|------------------------|------------------------|----------------------|
| Get Status   | `GET /status`            | `{userId}`             | `[{taskId, status}]`   | Auth required        |
| Update Task  | `POST /update-task`      | `{taskId, newStatus}`  | `{success}`            | Called by agent/LLM  |

- **Data models/schemas:**  
  - `Task`: `{taskId, status, ...}`
- **Auth/permissions:**  
  - JWT or API key, as needed

---

## 4. Error Handling & Edge Cases

**What can go wrong, and what should the system do?**

- [ ] Invalid input (missing/invalid fields)
- [ ] Unauthorized access
- [ ] Downstream service failure (DB/API timeout)
- [ ] Race conditions, concurrent updates
- [ ] Edge cases (no tasks, deleted tasks, malformed agent payloads)
- [ ] Rollback/compensating actions on failure

---

## 5. Validation & Monitoring

**How do you test, monitor, and confirm this works in production?**

- [ ] Unit & integration tests: API, data updates, error handling
- [ ] Acceptance criteria mapping (from PRD)
- [ ] Monitoring/alerts for failures, latency, status mismatches
- [ ] Log/trace agent activity and errors
- [ ] Success metrics (e.g., endpoint error rate <0.5%, p95 latency <2s)

---

## 6. Risks & Rollback

**Known risks:**
- [ ] Possible breaking changes for legacy clients?
- [ ] Agent/LLM may generate unexpected data or malformed payloads
- [ ] Data consistency or sync delays

**Rollback plan:**
- [ ] Can changes be reverted quickly (feature flag, config switch)?
- [ ] Data migration/backfill, if needed
- [ ] Alerting on issues post-deploy

---

# COMPLETE EXAMPLE

## 1. Overview

Add `/status` endpoint to support dashboard task indicators; handles live status fetches and agent updates.

## 2. Architecture & Data Flow

- Dashboard → `/status` (API server) → Task DB
- Agent system calls `/update-task` after task state changes
- Error flows logged to monitoring

## 3. APIs & Interfaces

| Name         | Endpoint/Method        | Input         | Output             | Notes                |
|--------------|------------------------|---------------|--------------------|----------------------|
| Get Status   | `GET /status`          | `userId`      | `[{id, status}]`   | JWT auth             |
| Update Task  | `POST /update-task`    | `taskId, status` | `{ok}`           | Agent-only           |

- Task: `{id, status, updatedAt}`
- Auth: Required for all endpoints

## 4. Error Handling & Edge Cases

- 400: missing/invalid input
- 401: unauthorized
- 5xx: log, auto-retry agent update if transient
- Edge: user has no tasks, deleted tasks

## 5. Validation & Monitoring

- Tests: mock agent, all error paths, data races
- Alerts: 5xx spike, status mismatch, high latency
- Metrics: Error rate <0.5%, median latency <1.5s

## 6. Risks & Rollback

- Risk: Agent sending corrupted status; will validate all fields and log rejects
- Rollback: Toggle feature flag, revert to static status if issues detected

---

## Quality Checklist

Before finalizing:
- [ ] All endpoints, data flows, and error paths documented
- [ ] Edge cases/risks are explicit
- [ ] Monitoring/rollback steps are clear
- [ ] Links to PRD and requirements included
- [ ] Copy-paste tested by team or agent
```
