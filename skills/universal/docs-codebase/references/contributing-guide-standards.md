# Contributing Guide Standards

Decision rules for `CONTRIBUTING.md`. The copy-ready skeleton is [assets/project-management/contributing-template.md](../assets/project-management/contributing-template.md); this file covers what must be true of it.

## Table of Contents

- [Scope: OSS vs Internal](#scope-oss-vs-internal)
- [Required Content](#required-content)
- [Rules That Make It Work](#rules-that-make-it-work)
- [Security Reporting](#security-reporting)
- [CONTRIBUTING.md Anti-Patterns](#contributingmd-anti-patterns)
- [Contributing Guide Checklist](#contributing-guide-checklist)

---

## Scope: OSS vs Internal

- **Open-source project:** the reader is a stranger. Lead with how to find a first issue, what the maintainers will and will not accept, and the review timeline they can expect. Link the Code of Conduct and license terms (including any CLA or DCO sign-off requirement).
- **Internal repo:** the reader is a colleague. Skip the welcome prose; lead with setup, the branch and review rules, and who owns what (CODEOWNERS). Link the team's engineering standards instead of restating them.

## Required Content

1. Development setup that runs on a clean machine, or a link to the README section that does.
2. How to run tests, lint, and type checks locally: the same commands CI runs.
3. Branch, commit-message, and PR conventions, each with one example.
4. What a PR must include: tests, docs updates, changelog entry (or the skip label), linked issue.
5. Review process: who reviews, required approvals, expected response time, and what happens to stale PRs.
6. How to report bugs and request features (link the issue templates).
7. How to report security issues privately (see below).

## Rules That Make It Work

- **Commands must match CI.** If CONTRIBUTING says `npm test` and CI runs something else, contributors pass locally and fail in CI. Reference the same script or make target CI calls.
- **Enforce what you state.** A commit convention that no hook or CI check enforces is a suggestion; either enforce it or call it a preference.
- **State response-time expectations you actually meet.** A promised 2-day first review that routinely takes two weeks costs more trust than no promise.
- **Say what you will not accept** (large unsolicited refactors, new dependencies without discussion, features without an issue). It saves contributors wasted work and maintainers awkward rejections.
- **Keep style rules in config**, not prose: link the linter and formatter configs; describe only what tooling cannot check.
- **Test the setup section** whenever toolchain or dependency versions change; outdated setup is the most common failure.

## Security Reporting

- Never ask for vulnerability reports in public issues.
- Point to `SECURITY.md` with a private channel (security advisory form or a monitored address), what to include, and the expected acknowledgement time.

## CONTRIBUTING.md Anti-Patterns

- No setup instructions, or ones that no longer work.
- Vague requirements ("write good code").
- Conventions described in prose that no tool enforces.
- A long welcome section that pushes setup below the fold.
- Duplicating the README or engineering handbook instead of linking to it.

## Contributing Guide Checklist

- [ ] Setup, test, lint commands match CI
- [ ] Branch, commit, and PR conventions with one example each
- [ ] PR requirements (tests, docs, changelog) stated
- [ ] Review process and response expectations stated
- [ ] Issue templates linked
- [ ] Private security reporting path linked
- [ ] Code of Conduct and license/CLA/DCO terms linked (OSS)
- [ ] All links pass the internal link check
