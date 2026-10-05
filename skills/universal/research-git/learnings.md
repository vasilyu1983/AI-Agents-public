# research-git — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-08-31] Apply passes land content merges but skip attribution step 4: ponytail 2026-08-09 had 4/4 merges applied, 0/4 sources.json entries. After any apply, grep each target skill's data/sources.json for the source name.
## Domain Knowledge

- [2026-07-11] Skill was purely repo-content mining, no git-history verification; added git-history-forensics.md (blame -w -C -M, bisect run, range-diff, pickaxe -S/-G) so Mode B/C claims can be checked against real history, not just static config.
## Open Questions

- [2026-05-30] Untested hypothesis: research-git could feed the diamond hunt by scanning for small low-dependency open-source primitives a solo dev can wrap into an absorption-resistant app; verify when next exercised.
## Consolidated Principles

