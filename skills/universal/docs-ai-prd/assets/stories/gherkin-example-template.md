```markdown
# Gherkin Example Template

*Purpose: Copy-paste template for writing Given-When-Then (Gherkin) scenarios for AI/agentic or standard projects. Use for executable specs, automated acceptance tests, or to drive clear agentic story breakdowns.*

---

## When to Use

Use this template when:
- Defining acceptance criteria for features, stories, or API changes
- Aligning team and agents on expected system behaviors and edge cases
- Enabling automation (BDD, Spec by Example, agent-driven QA)

---

## Structure

Each scenario includes:
- **Title**
- **Given** (context/setup)
- **When** (action/event)
- **Then** (expected outcome)

---

# TEMPLATE STARTS HERE

## Scenario: [Feature or User Story Name]

**Given** [initial system state, user, or precondition]  
**And** [additional preconditions if needed]  
**When** [user or agent performs an action/event]  
**Then** [expected result/output/state change]  
**And** [additional outcome/validation, if any]

---

### Example 1: Dashboard Task Status

```

Scenario: User sees task status update after completion

  Given a user is logged in and sees the dashboard
  And they have a list of pending tasks
  When the user marks a task as completed
  Then the dashboard shows a green status icon for that task
  And the task moves to the "Completed" section

```

---

### Example 2: API Error Handling

```

Scenario: Agent receives error on invalid input

  Given the agent is connected to the `/update-task` API
  And sends a request with a missing `taskId`
  When the API processes the request
  Then it responds with a 400 error code
  And the error message is "Missing required field: taskId"

```

---

### Example 3: Accessibility Check

```

Scenario: Status indicator passes accessibility test

  Given the dashboard shows a status indicator for each task
  When a screen reader inspects the status icon
  Then it reads out "Task completed" or "Task pending" with correct ARIA labels

```

---

## Acceptance Checklist

- [ ] Each scenario has clear Given, When, Then steps
- [ ] Covers both happy path and at least one edge case/unhappy path
- [ ] Steps are executable (manually or by automation/agent)
- [ ] All requirements/criteria in the PRD or story are covered

---

## Quality Checklist

Before sharing or using:
- [ ] Gherkin is copy-paste ready (no placeholders, ambiguous steps)
- [ ] Scenarios reviewed for completeness and testability
- [ ] Ready for agentic, human, or automated execution
```
