# AI-Native SDLC Agent Template

Purpose: Delegate mechanical SDLC work to the agent while humans own intent, architecture, and release. Use for feature delivery, refactors, or hotfixes.

Inputs:
- Spec or ticket
- Repo context (paths, constraints, coding standards)
- AGENTS.md / tool scopes (allowed commands, time caps, kill switch)
- Required tests and deploy checks

Preflight:
- Set max runtime and token budget; require explicit kill switch
- Allowlist commands/tools; block package installs unless approved
- Enable logging (plan, actions, diffs, test output)
- Require PLAN.md creation or planning tool output before coding

Runbook (Delegate → Review → Own)
- Plan
  - Agent drafts PLAN.md with scope, code paths, dependencies, risks, and exit criteria
  - Human reviews/edits plan; reject until risks/edge cases captured
- Design
  - Agent maps mocks/specs to components; applies design tokens/style guides
  - Call MCP component library; list accessibility gaps
  - Human signs off on architecture changes or schema migrations
- Build
  - Agent scaffolds end-to-end: models/APIs/UI/tests/docs in one run
  - Enforce conventions (telemetry, errors, lint format, feature flags)
  - Block commits/merges; diff-only output; no secrets
- Test
  - Require failing test first; agent adds/updates tests and runs suite
  - Capture coverage delta and flaky-test notes
  - Human verifies assertions/fixtures reflect intent
- Review
  - Agent performs first-pass review focused on P0/P1 bugs and policy violations
  - Human reviews architecture, performance, safety, migrations; owns merge
- Document
  - Agent writes PR summary, file/module notes, mermaid diagram if useful
  - Human adds “why” and approvals; ensure docs ship with code
- Deploy & Maintain
  - Agent links logs/metrics via MCP; proposes hotfix with rollback plan
  - Human approves rollout; track evals/drift/regressions

Guardrails
- Time cap per run; abort on unexpected prompts or new permission requests
- No package install/network without approval; no credential edits
- Require explicit test run and results before proposing merge
- Always surface uncertainties and blocked items; never self-approve

Outputs Checklist
- PLAN.md (or planner output), code diffs, tests run + results, doc updates, PR summary, risk/edge list, next steps/rollout notes
