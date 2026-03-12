# Looks Good To Me (LGTM) Review Checklist

Operational guidance from “Looks Good To Me” for constructive, high-signal reviews.

## Review Setup
- Clarify intent: bug fix vs. feature vs. refactor; skim description, risks, and test plan first.
- Keep scope tight: avoid mixed refactor + feature unless explicitly separated; push back on oversized diffs.
- Prepare context: domain assumptions, data shapes, rollout/rollback plan, monitoring expectations.

## Review Flow
- Pass 1: correctness and safety on main paths and edge cases (null/empty, limits, error handling, authz).
- Pass 2: design and responsibility boundaries; watch for tight coupling, unclear ownership, or hidden side effects.
- Pass 3: readability and maintainability; check names, function size, abstraction level consistency, and removal of dead code.
- Pass 4: tests and observability; confirm tests cover new behavior/bugs and that critical paths are logged/metriced.

## Feedback Style
- Be specific, constructive, and actionable; cite the problem and propose a concise direction.
- Separate asks from suggestions; label severity (blocker, should-fix, nit).
- Avoid personal language; focus on code and impact. Prefer questions when intent is unclear.
- Default to async clarity: include examples/snippets; minimize back-and-forth.

## Author Responsibilities
- Annotate tricky areas and risks; state known limitations and deferred work.
- Run and declare relevant tests; provide reproduction steps and data samples.
- Address feedback in code, not only in comments; summarize resolution when replying.

## Review Hygiene
- Timebox: keep sessions focused; schedule follow-ups rather than rush.
- Size: prefer ≤200–250 LOC per review; split large changes; avoid “pass-through” approvals.
- Checklist before approve: scope matches description; safety/correctness addressed; tests present and passing; observability added where needed.

## Team Calibration
- Share notable findings in retro; convert recurring issues into linters/templates.
- Pair on reviews periodically to align standards and improve signal consistency.
