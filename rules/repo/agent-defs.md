---
paths:
  - "agents/claude/**"
  - "agents/codex/**"
description: Tool-scoping rules for subagent definitions in this repo.
owner: skills/universal/ai-coding-agents/SKILL.md
---
- Give each agent a minimal tool allow-list: read-only agents get Read, Grep, and Glob; edit agents add Edit, Write, and Bash.
- Enforce read-only through the permission layer or the sandbox, never through the prompt; an agent granted Bash can write files.
- Run a reviewer or scanner that needs Bash under deny rules for writing commands, or in a read-only sandbox.
Why and procedure: skills/universal/ai-coding-agents/SKILL.md#default-workflow
