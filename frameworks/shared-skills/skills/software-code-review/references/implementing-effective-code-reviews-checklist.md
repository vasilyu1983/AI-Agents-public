# Implementing Effective Code Reviews Checklist

Operational practices distilled from “Implementing Effective Code Reviews.”

## Process Setup
- Define review goals up front (defect discovery vs. knowledge sharing vs. risk sign-off); pick practices accordingly.
- Keep reviews small: target 200–400 LOC per review (Cisco/SmartBear peer-review research — one company's dataset, treat as a heuristic); split larger changes and avoid >2000 LOC.
- Timebox sessions to roughly 60–90 minutes; schedule follow-ups instead of marathon reviews.
- Require author pre-checks: self-review, lint/tests run, and annotated diffs explaining intent, risks, and areas needing attention.

## Reviewer Playbook
- Read context first: change summary, issue link, risk areas, and test plan.
- Check correctness paths first (happy/error/boundary), then design (responsibilities, coupling), then tests/observability.
- Verify inputs/outputs, data invariants, and error handling; ensure logs/metrics exist on critical paths.
- Demand tests for new behavior and for fixed bugs that fail before the fix.

## Author Responsibilities
- Submit focused diffs; avoid mixing refactors with features unless clearly separated and labeled.
- Annotate diffs with rationale, assumptions, risk areas, and data shape examples.
- Respond promptly and concretely to review comments; capture agreed changes in code, not just discussion.

## Tooling and Enforcement
- Enforce size/time limits in tooling; flag pass-through reviews (e.g., implausibly short durations, or paces well above ~400–450 LOC/hour) as likely rubber-stamps and prompt a second look — treat the exact cutoff as team-tunable, not a number to enforce rigidly.
- Require checklist acknowledgment before approval (size, tests run, risk reviewed, logging/metrics added where needed).
- Track review metrics (defect density vs. size, turnaround time, rework rate) to tune practices, not to game counts.

## Social and Communication
- Keep feedback specific and behavior-focused; avoid personal language.
- Prioritize safety issues first, then correctness, then design/readability; mark severities to guide fixes.
- Encourage “ask” comments for clarification and “action” comments for required changes; avoid vague requests.

## Continuous Improvement
- Run periodic retros on review effectiveness; adjust size limits, checklists, and SLAs based on data.
- Share notable findings and patterns with the team; convert recurring issues into linters or templates.
- Calibrate reviewers: pair-review occasionally to align standards and spread domain knowledge.
