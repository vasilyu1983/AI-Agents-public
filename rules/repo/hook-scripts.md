---
paths:
  - "hooks/**"
description: Input-handling and fail-closed rules for hook scripts in this repo.
owner: skills/universal/agents-hooks/SKILL.md
---
- Parse stdin JSON explicitly, and validate every field before use.
- Resolve each path to its canonical form before you check it; do not rely on a regex alone.
- Never `eval` hook input. Quote every shell variable.
- Fail closed: a guard that cannot parse its input exits 2 (deny), never 0.
- Keep synchronous hooks fast. Redact logs and notifications.
- Match the JSON output to the schema of the event.
Why and procedure: skills/universal/agents-hooks/references/hook-security.md#critical-rules
