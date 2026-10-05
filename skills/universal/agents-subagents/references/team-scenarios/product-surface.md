---
description: Product Surface — extracted from monolith for progressive disclosure.
last_verified: 2026-09-16
status: stable
---

## Product Surface

**Typical scenario**

You have a customer-facing workflow that needs implementation, UX, accessibility, and localization reviewed together.

**Claude prompt**

```text
Create an agent team using the installed `product-surface` members.

Scenario: Review a new account settings flow that includes profile editing, notifications, security controls, and localized copy.

Required context:
- target UI flow and screenshots or code paths
- target locales: English, German, Arabic

Instructions:
- software-frontend-lead checks component structure, state boundaries, and delivery approach
- software-ux-designer checks flow clarity and user friction
- software-accessibility-reviewer checks keyboard, semantic, and screen-reader barriers
- software-localisation-reviewer checks string externalization, formatting, and RTL risk
- Run in parallel and synthesize one improvement plan
- Clean up the team when done
```

**Codex prompt**

```text
Spawn frontend_lead, ux_designer, accessibility_reviewer, and localisation_reviewer in parallel.

Task: review the account settings flow for frontend quality, usability, accessibility, and localization readiness.

Return:
- biggest surface problems
- affected user flows
- smallest high-leverage improvements
```
