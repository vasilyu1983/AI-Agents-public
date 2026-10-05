# Documentation Testing Guide

Decision rules for testing docs-as-code: which checks block a merge, which only warn, and how to test that examples and instructions still work. Tool installation and flag syntax are in each tool's own docs; the ready-to-use workflow is [assets/ci/docs-quality.yml](../assets/ci/docs-quality.yml).

Coverage audits, freshness tracking programs, and docs health metrics belong to [qa-docs-coverage](../../qa-docs-coverage/SKILL.md). Accessibility of docs sites belongs to [software-accessibility](../../software-accessibility/SKILL.md).

---
## Table of Contents

- [Gate Policy: Block or Warn](#gate-policy-block-or-warn)
- [Technical Accuracy](#technical-accuracy)
- [Link Validation](#link-validation)
- [Linting: Markdown and Prose](#linting-markdown-and-prose)
- [Freshness Checks](#freshness-checks)
- [Generated Reference Drift](#generated-reference-drift)
- [Minimal Accessibility Checks](#minimal-accessibility-checks)
- [Common Failures and Fixes](#common-failures-and-fixes)

---

## Gate Policy: Block or Warn

A check blocks the merge only if the author can fix the failure in the same PR and it fails for a real defect, not a flaky dependency. Everything else reports without blocking.

| Check | Default | Why |
|-------|---------|-----|
| Internal (repo-relative) links and anchors | **Block** | Fully under the author's control; a broken one is always a real defect |
| External (http/https) links | **Warn** (advisory job, scheduled full run) | Sites rate-limit, block bots, and go down transiently; blocking on them trains people to ignore or bypass the gate |
| Markdown lint (structure rules) | **Block** | Deterministic; auto-fixable |
| Prose lint (Vale) | **Block on `error`, warn on `warning`/`suggestion`** | Style suggestions are judgment calls; a blocking suggestion gets the rule disabled |
| Spelling with project vocabulary | **Block** once the vocabulary is seeded; warn before that | Without a vocabulary file, product names produce noise |
| Examples labeled runnable | **Block** | A failing runnable example is a broken product surface |
| Generated reference drift (`git diff --exit-code` after regenerating) | **Block** | The spec or code changed without the docs |
| Freshness / staleness report | **Warn** | Age alone is not a defect; route to owners |
| Readability scores | **Warn** or omit | Scores are weak proxies; do not gate on them |

Two rules make the gate trustworthy:

- **No gate may end in `|| true` or pipe through a command that swallows exit codes.** `find ... -exec cmd {} \;` exits 0 even when `cmd` fails; use `find -print0 | xargs -0 -r -n1 cmd` under `set -euo pipefail` (as the shipped workflow does). A check that cannot fail is worse than no check, because it is advertised as protection.
- **Make "advisory" explicit** with `continue-on-error: true` on a separate job, so the result stays visible in the PR instead of being silently discarded.

---

## Technical Accuracy

Prefer making examples testable at the source over testing prose after the fact:

1. **Include from tested files.** Keep example code in files that the test suite runs, and include them into docs (docs-site snippet includes, or a build step that injects the file). The doc cannot drift from code that CI executes.
2. **Doctest where the language supports it** (Python `doctest`, Rust doc tests, Go `Example` functions). These run with the normal test suite.
3. **Label every code block** as runnable or illustrative. Only runnable blocks are extracted and executed; illustrative blocks say so in prose. An unlabeled block is read as a prescription by humans and agents alike.
4. **Test setup instructions in a clean environment** (fresh container, no cached dependencies) on a schedule and before releases. Setup docs fail because of state on the author's machine, which no PR-time check can see.

Do not extract code blocks with `grep -A N` and pipe them to a shell: it truncates blocks, mixes languages, and executes illustrative snippets.

---

## Link Validation

- Split internal and external checks into separate jobs, per the gate policy above. The shipped config [assets/ci/.mlc-config.json](../assets/ci/.mlc-config.json) ignores `http(s)` and `mailto` so the blocking job checks only repo-relative links.
- Check anchors, not just files: a renamed heading breaks `file.md#old-heading` while the file still exists.
- Exclude generated output and `.archive/` from the blocking job; include them in a scheduled report if they are published.
- When a doc is retired, repair inbound links in the same PR or leave a redirect stub (see the claim retirement gate in [SKILL.md](../SKILL.md#claim-authority-and-retirement-gate)).

---

## Linting: Markdown and Prose

- Use the shipped configs: [assets/ci/.markdownlint.yaml](../assets/ci/.markdownlint.yaml) and [assets/ci/.vale.ini](../assets/ci/.vale.ini). Conventions are in [markdown-style-guide.md](markdown-style-guide.md).
- Start Vale with a small rule set and a project vocabulary (`accept.txt` for product names and terms). Turning on a full style pack at once produces hundreds of findings, and teams respond by disabling the job.
- Before adopting the template, check the [Vale action inputs](https://github.com/vale-cli/vale-action/blob/v2/action.yml) for the selected action ref: use `vale_flags` for the config and `filter_mode: nofilter` so existing errors in the selected tree remain blocking. The bundled config declares `Packages` globally; the action syncs them before linting. Enable a vocabulary only after creating its files at the [documented vocabulary path](https://docs.vale.sh/keys/vocabularies).
- Encode terminology decisions ("sign in" vs "log in") as Vale substitution rules, not as a wiki page nobody runs.

---

## Freshness Checks

- **Do not use file mtime.** In CI, checkout sets every file's mtime to the checkout time, so `find -mtime` reports nothing as stale. Use `git log -1 --format=%cI -- <file>`.
- **Correlate doc history with the code it describes.** A code path with commits after the doc's last commit is a stronger staleness signal than doc age. Map each critical doc to its code paths (front matter or CODEOWNERS-style map) and report docs whose code moved on.
- **Scan for version and date mentions** and check each against the project's current manifests and lockfiles, rather than grepping for a hard-coded list of "old" versions that itself goes stale.
- Route staleness findings to the doc's owner; do not block merges on them.

---

## Generated Reference Drift

For API references, CLI help, config references, and other docs generated from code or specs:

```yaml
- name: Verify generated docs are current
  run: |
    make docs-generate          # your generator
    git diff --exit-code docs/  # fails if the committed docs differ
```

The generated output is committed and reviewed like code; hand edits to it are overwritten, so fix the source instead.

---

## Minimal Accessibility Checks

These are cheap, deterministic, and worth running on every docs PR. Full accessibility review of a docs site is out of scope here.

- Every image has meaningful alt text (empty alt only for decorative images).
- Heading levels do not skip (markdownlint MD001 covers this).
- Link text describes the destination; no bare "click here".
- Diagrams have a text alternative or an adjacent prose explanation.

---

## Common Failures and Fixes

| Failure | Fix |
|---------|-----|
| Code examples fail after an update | Move examples into tested files and include them; run doctests in CI |
| Docs drift from the code or spec | Generate references and add the `git diff --exit-code` gate |
| Link check always green despite broken links | Remove `|| true` and `find -exec`; split internal (blocking) from external (advisory) |
| Prose lint job disabled by the team | Too many rules at once; start with errors only and a project vocabulary |
| Terminology inconsistent across pages | Vale substitution rules plus `accept.txt` vocabulary |
| Staleness report flags nothing | It is reading mtime; switch to git history |
