# Pull Request Description Template

Copy the block below into `.github/pull_request_template.md` (GitHub) or `.gitlab/merge_request_templates/Default.md` (GitLab). Delete optional sections that do not apply rather than writing "N/A". The order follows the description contract in [pr-best-practices.md](../../references/pr-best-practices.md#description-contract): a reviewer should be able to stop after any section and still know the most important thing so far.

```markdown
## What and why
<!-- One or two sentences: what changes and why it is needed now. -->

Closes #

## Risk
<!-- What could break, for whom, and how would we notice? "Low: docs only" is a valid answer. -->

## How it was verified
<!-- Tests added or changed, commands run, manual checks and the environment used.
     Link the CI run rather than pasting "tests pass". -->

## Rollout and rollback
<!-- Migrations (and whether the previous version still runs against them), feature flags and
     their defaults, config or secrets required, backward compatibility, and how to undo. -->

## Where to look
<!-- The files, decisions, or trade-offs you want reviewers to scrutinize. -->

<!-- Optional sections: keep only those that apply -->

## Screenshots
<!-- UI changes: before and after. -->

## Performance
<!-- Only with measured numbers: what was measured, how, before and after. -->

## Security
<!-- Auth, input handling, secrets, permissions, or data exposure changes, and how they were checked. -->

## Stack
<!-- Stacked PRs: position (e.g. 2 of 3), base PR, and what the next layer adds. -->

## AI assistance
<!-- If the repo's policy asks for it: which parts were agent-generated and what a human verified. -->
```

## When Each Section Earns Its Place

| Section | Required when | A good answer |
|---------|---------------|---------------|
| What and why | always | states the problem and the change; links the issue |
| Risk | always | names the failure mode and the signal that would reveal it |
| How it was verified | always | points to evidence (CI run, test names, manual steps) rather than claims |
| Rollout and rollback | anything beyond a pure refactor or docs change | a person other than the author could deploy and undo it from this text |
| Where to look | PRs above trivial size | points reviewers at the one or two places a mistake would hide |
| Screenshots | visible UI change | before and after, same viewport |
| Performance | the PR claims a speedup or touches a hot path | numbers with method; no numbers means delete the section |
| Security | auth, input parsing, permissions, secrets, PII | what changed and how it was tested |
| Stack | stacked PRs | position, base, merge order |
| AI assistance | repo policy requires disclosure | parts generated, and what the human reviewed or tested |

## Common Failures

- Restating the diff ("changed file X, Y, Z") instead of the reason.
- "Tests pass" without saying which tests or linking CI.
- Rollback left empty on a PR with a migration or flag.
- A long description for a small PR; for a one-line fix, what/why and verification are enough.
