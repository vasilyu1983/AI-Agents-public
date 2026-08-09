```markdown
# Story Mapping Template

*Purpose: Copy-paste template for creating actionable user story maps—turning features and requirements into a visual backlog for GenAI/agentic or traditional projects. Suitable for agentic workflows, rapid team alignment, and edge-case planning.*

---

## When to Use

Use this template when:
- Planning a new feature, flow, or system with multiple user steps
- Aligning human and agent teams on workflow and requirements
- Breaking down complex requirements into manageable stories and increments

---

## Structure

This template contains:
1. **Big Picture Goal**
2. **Story Map Table**
3. **Edge Cases & Non-Happy Paths**
4. **Acceptance Checklist**

---

# TEMPLATE STARTS HERE

## 1. Big Picture Goal

_What is the outcome for the user or system? Why does this flow matter?_

> Example:  
> “Enable users to complete and track tasks in a dashboard, improving task completion rate and transparency.”

---

## 2. Story Map Table

_Build the story left-to-right (main steps), and top-to-bottom (details/subtasks)._

| High-Level Steps            | Step 1: Login | Step 2: View Tasks | Step 3: Complete Task | Step 4: See Status | Step 5: Get Help |
|----------------------------|---------------|--------------------|----------------------|--------------------|------------------|
| **Key Actions (row)**      | User enters credentials | Dashboard loads, shows all tasks | User marks task as complete | Status icon updates to 'Done' | User clicks FAQ |
| **Details/Subtasks**       | Validation errors shown on fail | Sort/filter tasks | Undo button enabled | Status color changes | Contact support link visible |
| **Agent/LLM Tasks**        | Pre-fill test user data | Generate UI for tasks | Suggest next task | Run accessibility check | Generate help doc |

---

## 3. Edge Cases & Non-Happy Paths

- [ ] User enters invalid credentials (handled at login)
- [ ] No tasks to display (show empty state)
- [ ] Task completion fails (display error, allow retry)
- [ ] Status doesn’t update in time (show loading, error icon)
- [ ] User can’t find help (escalate to support)

---

## 4. Acceptance Checklist

- [ ] All main user goals/steps mapped left to right
- [ ] Key actions and subtasks included for each step
- [ ] Edge cases and “unhappy” paths covered
- [ ] Agent/LLM roles and triggers listed if used
- [ ] Output ready to be converted into user stories or implementation tasks

---

# COMPLETE EXAMPLE

## 1. Big Picture Goal

Allow users to quickly complete and check off daily tasks on the dashboard, reducing task backlog and support tickets.

## 2. Story Map Table

| Steps                 | Login         | View Tasks      | Complete Task    | See Status         | Get Help        |
|-----------------------|--------------|-----------------|------------------|--------------------|-----------------|
| **Key Actions**       | Enter email & password | See today’s tasks | Click checkmark    | Status turns green| Click help      |
| **Details/Subtasks**  | Error on wrong password | Filter by date    | Undo last action   | Tooltip shows status| Contact form    |
| **Agent/LLM Tasks**   | Prefill login for demo | Generate test data | Auto-suggest task  | Accessibility test | Generate FAQ    |

## 3. Edge Cases & Non-Happy Paths

- User locked out after 3 bad logins
- No tasks = “All caught up!” message
- Network error on completion → retry
- Status doesn’t update—manual refresh
- Help link not working—show fallback instructions

## 4. Acceptance Checklist

- [x] Steps mapped, left to right
- [x] Subtasks and unhappy paths included
- [x] All agent/LLM steps visible
- [x] Ready to convert to tickets or user stories

---

## Quality Checklist

Before sharing or using:
- [ ] Story map includes all key flows and edge cases
- [ ] Subtasks/action details are actionable
- [ ] Ready for agentic or human story breakdown
- [ ] No steps or unhappy paths are missing
```
