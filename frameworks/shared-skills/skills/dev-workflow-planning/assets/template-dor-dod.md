# Definition of Ready / Done (DoR/DoD) Templates

Standard checklists for ensuring work items are ready to start and truly complete.

---

## Definition of Ready (DoR)

Work items must pass this checklist before being pulled into a sprint/iteration.

### User Story DoR Checklist

- [ ] **Title**: Clear, concise, describes the outcome
- [ ] **User story format**: "As a [user], I want [goal], so that [benefit]"
- [ ] **Acceptance criteria**: 3-7 testable conditions defined
- [ ] **Sized**: Story points or T-shirt size assigned
- [ ] **Dependencies**: External dependencies identified and unblocked
- [ ] **Design**: UX/UI mockups available (if applicable)
- [ ] **Technical feasibility**: Spike completed (if high uncertainty)
- [ ] **Testable**: QA understands how to verify
- [ ] **Small enough**: Can be completed in one sprint

### Bug DoR Checklist

- [ ] **Reproduction steps**: Clear steps to reproduce
- [ ] **Expected vs actual**: Documented behavior difference
- [ ] **Environment**: Browser, OS, device, version specified
- [ ] **Severity**: Impact level assigned (Critical/High/Medium/Low)
- [ ] **Screenshots/logs**: Evidence attached
- [ ] **Assignable**: Root cause area identified

### Technical Task DoR Checklist

- [ ] **Scope**: Clear boundaries defined
- [ ] **Exit criteria**: How we know it's done
- [ ] **Approach**: Technical approach agreed
- [ ] **Dependencies**: Upstream work complete
- [ ] **Reviewable**: Someone available to review

---

## Definition of Done (DoD)

Work items must pass this checklist before being marked complete.

### Feature DoD Checklist

**Code Quality**
- [ ] Code written and follows style guide
- [ ] Code reviewed and approved
- [ ] No new linter warnings/errors
- [ ] No hardcoded secrets or credentials
- [ ] Error handling implemented

**Testing**
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Edge cases covered
- [ ] No regression in existing tests
- [ ] Manual smoke test completed (if applicable)

**Documentation**
- [ ] Code comments for complex logic
- [ ] API documentation updated (if applicable)
- [ ] README updated (if applicable)
- [ ] Changelog entry added (if applicable)

**Deployment**
- [ ] Deployed to staging environment
- [ ] Verified in staging
- [ ] Feature flag configured (if applicable)
- [ ] No breaking changes to API (or versioned)

**Acceptance**
- [ ] Acceptance criteria verified
- [ ] Product owner accepted
- [ ] No blockers for production release

### Bug Fix DoD Checklist

- [ ] Bug no longer reproducible
- [ ] Regression test added
- [ ] Root cause documented
- [ ] Related issues checked
- [ ] Fix reviewed and approved
- [ ] Deployed and verified

### Spike DoD Checklist

- [ ] Question answered with evidence
- [ ] Recommendation documented
- [ ] Next steps identified
- [ ] Time box respected
- [ ] Findings shared with team

---

## Acceptance Criteria Templates

### Format: Given/When/Then (Gherkin)

```gherkin
Feature: User login

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter valid username and password
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message

  Scenario: Failed login with invalid password
    Given I am on the login page
    When I enter valid username and invalid password
    And I click the login button
    Then I should see an error message "Invalid credentials"
    And I should remain on the login page
```

### Format: Bullet List

```markdown
## Acceptance Criteria

- [ ] User can enter email and password
- [ ] Login button is disabled until both fields have values
- [ ] Invalid credentials show error message
- [ ] Successful login redirects to dashboard
- [ ] Session expires after 30 minutes of inactivity
- [ ] "Remember me" extends session to 7 days
```

### Format: Rule-Based

```markdown
## Acceptance Criteria

**Rule 1: Email validation**
- Email must be valid format
- Email must not be already registered (for signup)
- Error message shown for invalid email

**Rule 2: Password requirements**
- Minimum 8 characters
- At least one uppercase, one lowercase, one number
- Strength indicator updates in real-time

**Rule 3: Rate limiting**
- Max 5 failed attempts per 15 minutes
- Lockout message shown on 6th attempt
- Account unlocks automatically after 15 minutes
```

---

## Estimation Guidelines

### Story Point Reference Scale

| Points | Effort | Complexity | Uncertainty | Example |
|--------|--------|------------|-------------|---------|
| **1** | Hours | Low | Known | Fix typo, update copy |
| **2** | Half day | Low | Known | Add simple field to form |
| **3** | 1-2 days | Medium | Mostly known | New CRUD endpoint |
| **5** | 3-5 days | Medium | Some unknowns | New feature with UI |
| **8** | 1 week | High | Significant unknowns | Integration with external API |
| **13** | 1-2 weeks | High | Many unknowns | **Split this story** |
| **21+** | Too big | N/A | Too high | **Definitely split** |

### Slicing Strategies

**SPIDR Framework:**
- **S**pike: Reduce uncertainty first
- **P**aths: Split by user flow variations
- **I**nterfaces: Split by input/output channels
- **D**ata: Split by data types or subsets
- **R**ules: Split by business rules

**Example: Split by Paths**
```
Before: "User can manage their profile"
After:
- User can view their profile
- User can edit their name
- User can change their email (with verification)
- User can upload profile photo
- User can delete their account
```

### Risk Buffers

| Confidence | Multiplier | When to Use |
|------------|------------|-------------|
| High | 1.0x | Well-understood, done before |
| Medium | 1.3x | Some unknowns, familiar tech |
| Low | 1.5x | New tech, external dependencies |
| Very Low | 2.0x | First time, high uncertainty |

---

## Planning Levels

### Roadmap -> Milestone -> Sprint -> Task

| Level | Horizon | Granularity | Owner |
|-------|---------|-------------|-------|
| **Roadmap** | 6-12 months | Themes, outcomes | Product |
| **Milestone** | 1-3 months | Epics, features | Product + Tech |
| **Sprint** | 1-2 weeks | User stories | Team |
| **Task** | Hours-days | Implementation steps | Developer |

### Example Hierarchy

```text
Roadmap: Q1 2025 - Improve user onboarding
|-- Milestone: Reduce time-to-value by 50%
|   |-- Epic: Guided setup wizard
|   |   |-- Story: First-time user sees wizard
|   |   |-- Story: User can skip wizard
|   |   `-- Story: Wizard tracks completion
|   `-- Epic: Interactive tutorials
|       |-- Story: Tutorial for core feature
|       `-- Story: Tutorial progress saved
`-- Milestone: Reduce churn in first week
    `-- Epic: Proactive engagement
        |-- Story: Day 2 email with tips
        `-- Story: In-app progress indicators
```

---

## Cross-Functional Coordination

### RACI Matrix Template

| Activity | Product | Engineering | Design | QA | Security |
|----------|---------|-------------|--------|----|----|
| Define requirements | **A** | C | C | I | C |
| Design solution | C | **A** | **R** | I | C |
| Implement | I | **A/R** | C | I | C |
| Review code | I | **A** | I | I | C |
| Test | C | C | I | **A/R** | I |
| Security review | I | C | I | I | **A/R** |
| Deploy | I | **A/R** | I | I | C |
| Accept | **A/R** | I | I | C | I |

**R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed

### Handoff Checklist

**Design -> Engineering**
- [ ] Mockups/wireframes complete
- [ ] Design specs documented
- [ ] Edge cases discussed
- [ ] Assets exported

**Engineering -> QA**
- [ ] Feature deployed to staging
- [ ] Test data prepared
- [ ] Acceptance criteria clear
- [ ] Known limitations documented

**QA -> Product**
- [ ] All acceptance criteria verified
- [ ] Test results documented
- [ ] Bugs filed and triaged
- [ ] Sign-off requested

---

## Do / Avoid

### GOOD: Do

- Check DoR before pulling work
- Verify DoD before marking complete
- Size stories using reference scale
- Slice large stories (>8 points)
- Document acceptance criteria upfront
- Include risk buffer in estimates
- Coordinate handoffs explicitly

### BAD: Avoid

- Starting work without clear acceptance criteria
- Declaring "done" without testing
- Estimating without understanding scope
- Working on stories too big to finish in sprint
- Skipping code review "to save time"
- Deploying without staging verification
- Assuming handoffs happen automatically

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No DoR** | Unclear requirements discovered mid-sprint | Gate sprint entry with DoR |
| **Soft DoD** | "Done" means different things | Written DoD checklist |
| **Mega-stories** | Never finish, hard to track | Slice to <8 points |
| **Missing AC** | Built wrong thing | Gherkin format AC |
| **No ownership** | Work falls through cracks | RACI for every epic |
| **Hope-based estimates** | Always late | Use reference scale + buffer |

---

## Optional: AI/Automation

> **Note**: AI can assist but should not replace human judgment on priorities and acceptance.

### AI-Assisted Planning

- Generate acceptance criteria draft from story description
- Suggest story slicing based on complexity analysis
- Identify missing edge cases in requirements

### Automation Tools

- JIRA/Linear templates with DoR/DoD checklists
- CI/CD gates that verify DoD items
- Automated test coverage reporting

### Bounded Claims

- AI-generated acceptance criteria need human review
- Story point estimates require team calibration
- Dependency mapping suggestions need validation

---

## Related Templates

- [planning-templates.md](../references/planning-templates.md) - Feature/bug/spike plans
- [session-patterns.md](../references/session-patterns.md) - Multi-session workflows

---

**Last Updated**: December 2025
