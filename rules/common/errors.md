---
description: Error-handling and outbound I/O invariants for every coding session.
owner: skills/universal/software-clean-code-standard/SKILL.md
---
- Never leave an empty catch or a silent failure; rethrow, or handle the error and log it with context (CC-ERR-01, CC-ERR-02).
- Put the operation and identifiers in the error context, never secrets or personal data (CC-ERR-02).
- Give each outbound I/O call a timeout, and cancellation where supported (CC-ERR-04).
- Keep retries bounded and safe to repeat (CC-ERR-03).
Why and procedure: skills/universal/software-clean-code-standard/references/clean-code-standard.md#error-handling-cc-err
