<!-- BEGIN GENERATED: rules/repo -->
<!-- Generated from rules/repo/ by scripts/checks/check-rules.py --write. Do not edit by hand. -->

### agent-defs.md

- Give each agent a minimal tool allow-list: read-only agents get Read, Grep, and Glob; edit agents add Edit, Write, and Bash.
- Enforce read-only through the permission layer or the sandbox, never through the prompt; an agent granted Bash can write files.
- Run a reviewer or scanner that needs Bash under deny rules for writing commands, or in a read-only sandbox.
Why and procedure: skills/universal/ai-coding-agents/SKILL.md#default-workflow

<!-- END GENERATED: rules/repo -->
