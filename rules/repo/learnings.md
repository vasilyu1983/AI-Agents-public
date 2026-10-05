---
paths:
  - "skills/**/learnings*.md"
description: Entry shape, caps, and redaction rules for skill learnings files.
owner: skills/universal/agents-skills-feedback-loop/SKILL.md
---
- Write each entry as one bullet: `- [YYYY-MM-DD] <one-sentence atomic insight>`.
- Put each entry in exactly one section: Patterns That Work, Mistakes to Avoid, Domain Knowledge, Open Questions, or Consolidated Principles.
- Append through `append_learning.py`; it enforces the entry shape.
- Keep raw `learnings.md` at 150 entries or fewer and a consolidated file at 60 or fewer; refuse rather than truncate.
- Never store secrets, personal data, customer-specific facts, or unreleased client details in either file.
Why and procedure: skills/universal/agents-skills-feedback-loop/SKILL.md#core-contract
