# k6 Load Testing Template — Moved

This template previously duplicated the dedicated `qa-testing-performance` skill and risked drift.

For k6 load/stress/soak/spike/capacity patterns, templates, and CI gates, use the dedicated skill:

- **`frameworks/shared-skills/skills/qa-testing-performance/`**

That skill owns: test-type taxonomy, percentile-over-average rule, k6 1.x and 2.x scripting differences, perf budget checker script, and CI gate design.

This stub remains so existing references in plans and PRDs resolve. Remove the link to this file from your skill instructions and point directly at `qa-testing-performance/SKILL.md` instead.
