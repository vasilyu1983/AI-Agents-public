---
description: Git push, hook, review, and commit-message invariants for every coding session.
owner: skills/universal/dev-git-workflow/SKILL.md
---
- Never force-push `main`, release branches, tags, or a branch others build on. Elsewhere, use `--force-with-lease=<branch>:<expected-sha>`.
- Never use `--no-verify` unless the human asked for it in this task.
- Never let an agent approve or merge its own PR.
- Never let a commit message claim behaviour that the diff does not show.
Why and procedure: skills/universal/dev-git-workflow/SKILL.md#agent-authored-work
