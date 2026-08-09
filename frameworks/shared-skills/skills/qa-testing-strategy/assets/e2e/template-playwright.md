# Playwright E2E Template — Moved

This template previously duplicated the dedicated `qa-testing-playwright` skill and risked drift.

For Playwright E2E patterns, templates, and CI integration, use the dedicated skill:

- **`frameworks/shared-skills/skills/qa-testing-playwright/`**

That skill owns: locator priority, three-tier suite topology (smoke / targeted-batch / deploy-gate), stateful app failure classification, auth setup, Page Object Model, sharding, trace/video artifacts, and CI integration.

This stub remains so existing references in plans and PRDs resolve. Remove the link to this file from your skill instructions and point directly at `qa-testing-playwright/SKILL.md` instead.
