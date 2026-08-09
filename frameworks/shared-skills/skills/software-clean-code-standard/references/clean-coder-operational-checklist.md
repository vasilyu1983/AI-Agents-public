# The Clean Coder Operational Checklist

Professional conduct and discipline guidelines distilled from “The Clean Coder.”

## Professional Commitments
- Say “no” clearly when scope, time, or risk make success unlikely; offer options instead of silent agreement.
- Do not promise what you cannot deliver; replace dates with evidence-based ranges and assumptions.
- Keep the codebase releasable: no breaking changes without tests and fixes in the same commit.

## Coding Discipline
- Write tests first or immediately after; never ship untested code. Keep tests fast, isolated, and reliable.
- Refactor continually to keep code clean and simple; leave every file slightly better.
- Manage technical debt deliberately: log it, estimate it, and schedule repayment instead of hiding it.

## Time and Estimation
- Break work into small tasks with clear definitions of done; estimate at that level.
- Communicate uncertainty and risks; update estimates as facts change.
- Protect slack for integration, debugging, and unexpected work; avoid heroics to mask bad plans.

## Handling Pressure and Interruptions
- Do not code when exhausted or distracted; pause and resume when focus is back.
- Under pressure, reduce scope first, not quality; keep tests green and changes small.
- Avoid multitasking; finish and integrate small slices before starting new ones.

## Collaboration and Communication
- Use pairing or swarm reviews on risky changes; switch roles (driver/navigator) and keep sessions focused.
- Ask for clarification early; document decisions, trade-offs, and constraints in code or adjacent notes.
- Give and receive feedback professionally—specific, respectful, and actionable.

## Quality and Defect Handling
- Reproduce defects, add a failing test, fix, and keep the test; avoid cosmetic “fixes” without proof.
- Prefer prevention: add checks, assertions, and monitoring around defect-prone areas.
- Maintain CI discipline: commit in small increments; do not break the build. Fix red builds before new work.

## Environment and Preparation
- Automate setup and repetitive tasks; keep tools/scripts versioned and reliable.
- Maintain a quiet, interruption-minimized environment for deep work; batch meetings and comms when possible.
- Invest in practice: katas, reading, and deliberate learning to raise baseline skill and speed safely.
