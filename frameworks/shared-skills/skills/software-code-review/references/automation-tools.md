# Review Automation and Platform Workflows

Use automation to narrow review scope and catch routine issues before humans spend time on them. Do not present automation as a replacement for human judgment on correctness, security, or product intent.

## Table of Contents

- [Operating Principles](#operating-principles)
- [Platform-Native Review Surface](#platform-native-review-surface)
- [GitHub](#github)
- [GitLab](#gitlab)
- [Bitbucket](#bitbucket)
- [Third-Party AI Review Tools](#third-party-ai-review-tools)
- [CodeRabbit](#coderabbit)
- [Qodo PR-Agent](#qodo-pr-agent)
- [Amazon Q Developer](#amazon-q-developer)
- [Legacy Note: Amazon CodeGuru Reviewer](#legacy-note-amazon-codeguru-reviewer)
- [Static Analysis and Security Automation](#static-analysis-and-security-automation)
- [AI-Generated and Agent-Created PRs](#ai-generated-and-agent-created-prs)
- [What Actually Changes When the Author Is an Agent](#what-actually-changes-when-the-author-is-an-agent)
- [Merge Queues and Stacked PRs](#merge-queues-and-stacked-prs)
- [Stacked PRs vs. Trunk-Based Development](#stacked-prs-vs-trunk-based-development)
- [Recommendation Framework](#recommendation-framework)
- [Sources to Open First](#sources-to-open-first)

## Operating Principles

- Prefer native platform controls before adding bots.
- Use AI review to surface candidates, not to auto-approve changes.
- Keep required checks deterministic and fast enough for routine PRs.
- Exclude generated files, snapshots, vendored code, and large fixtures from review bots where possible.
- Pin action and workflow dependencies to stable versions; do not recommend floating refs such as `@master`.

## Platform-Native Review Surface

### GitHub

Use GitHub's native stack when the repository already lives on GitHub:

- Copilot code review for manual or automatic pull request review
- Repository and path-specific instructions for Copilot
- Excluded content and coding-guideline configuration for AI review
- Required checks, CODEOWNERS, branch protection or rulesets
- Merge queue for serialized main-branch integration

Operational guidance:

- Treat Copilot review comments as advisory until a human confirms them.
- Copilot code review moved to an agentic architecture: instead of only reading the diff, it can call tools to pull in repository context (related files, cross-file dependencies, directory structure) before commenting. This generally improves relevance but does not remove the need for human confirmation — verify what context it actually used, since agentic exploration can also surface stale or irrelevant files.
- Keep repository instructions concise and scoped to review-relevant rules; check current docs for the repository-instructions character limit, which has changed more than once.
- Some plans route pull requests to different reasoning tiers based on change complexity. Do not assume a fixed mapping of tier-to-model — verify current behavior in GitHub's docs before making claims about capability differences.
- Configure merge-queue-aware CI when required checks must run on queued changes.
- Use native code scanning or code quality features as signals, not as the whole review process.
- GitHub has also been rolling out native stacked-PR support (a `gh stack`-style CLI plus UI). Verify current availability and maturity before recommending it over Graphite or Git Town — it was in early rollout as of mid-2026 and the safest default is still "check what's GA today."

### GitLab

Use GitLab-native controls when the repository is on GitLab:

- Duo in merge requests for AI assistance
- Custom review instructions for Duo
- Merge request approvals and approval rules
- Required pipeline checks and code owners where available in the project plan

Operational guidance:

- Keep approval policy separate from AI assistance: Duo can assist, but approval rules decide merge eligibility.
- Which Duo review flow runs depends on the subscription tier; verify current tier-to-feature mapping in GitLab's docs rather than assuming a single unified "Duo review" product.
- Review instructions should encode local policy, generated-file boundaries, and stack-specific guidance.
- Use approval rules to protect sensitive areas such as auth, billing, migrations, and infrastructure.

### Bitbucket

Bitbucket Cloud has a thinner native AI surface, so treat Code Insights as the main review automation interface:

- Code Insights for annotations and reports from external tools
- Required build statuses and branch restrictions for merge safety
- External scanners can report into Bitbucket, but review ownership stays human

Operational guidance:

- Prefer tools that publish actionable annotations into Code Insights rather than only posting summary comments elsewhere.
- Keep the number of required external checks small enough that PRs remain reviewable.

## Third-Party AI Review Tools

### CodeRabbit

Use when a team wants bot comments directly in PRs and supports an external review service.

- Strengths: review summaries, issue surfacing, team-level configuration
- Risks: false positives, noisy comments, tool-specific workflow lock-in
- Recommendation: keep optional until the team has explicit noise-handling rules

### Qodo PR-Agent

Use when the team wants an AI review bot with repo-level configuration and open-source visibility.

- Ownership changed: Qodo transferred the open-source PR-Agent project to independent community governance in 2026 (new organization, external maintainer). Qodo's current commercial product is a separate offering built on top of the same lineage. Do not assume the open-source repo and Qodo's paid product have identical roadmaps or support.
- Strengths: configurable PR review workflows, Git provider integrations, auditable repo
- Risks: configuration drift, self-hosting or operational overhead depending on deployment model; verify which organization currently hosts the canonical repo before linking to it
- Recommendation: prefer the current repository or docs as the source of truth, not blog comparisons or the pre-2026 repo location

### Amazon Q Developer

Use when the team already standardizes on AWS developer tooling and wants assistant support across IDE and review workflows.

- Strengths: AWS ecosystem fit, current product surface
- Risks: broad product positioning can make review-specific capabilities easy to overstate
- Recommendation: verify the exact workflow supported before recommending it as a code-review tool

### Legacy Note: Amazon CodeGuru Reviewer

Do not recommend CodeGuru Reviewer for new adoption. AWS states it is no longer open to new customers. Keep it only as migration or estate-cleanup context.

## Static Analysis and Security Automation

Use these to reduce reviewer cognitive load, not to replace code reading:

- Linters and formatters for style, obvious correctness issues, and consistency
- Unit and integration tests for regression protection
- SAST and SCA tools such as Semgrep, SonarQube, Snyk, and native platform scanning
- Secret detection, IaC scanning, and dependency policy checks for high-risk repos

Recommended posture:

- Run fast checks on every PR.
- Keep heavyweight or flaky checks out of the critical merge path unless risk justifies them.
- Separate style failures from security or correctness failures in reporting.
- Prefer actionable annotations over generic dashboards that reviewers must open manually.

## AI-Generated and Agent-Created PRs

Apply a stricter review pass when changes are AI-generated or assembled by coding agents:

- verify that the diff matches the stated intent
- re-check hidden assumptions at boundaries, retries, null cases, and authorization paths
- inspect generated tests for assertion quality and missing negative paths
- watch for repeated helper patterns, dead abstractions, and unnecessary framework use
- review prompts, repository instructions, or agent context files when they materially shape the output

If the PR was created by an agent:

- do not trust green tests alone
- inspect configuration, migrations, and public API changes manually
- require a human owner for merge decisions

### What Actually Changes When the Author Is an Agent

The review checklist barely changes; the review *posture* does:

- The bottleneck shifts from writing code to verifying it. Expect to spend more wall-clock time reading and validating than you would for the same-sized human-authored diff, especially on the first few PRs from a given agent/workflow.
- Judge style and idiom choices against **this codebase's existing conventions**, not against a generic style guide the agent may have been trained on. An agent-written diff that is "correct" by an abstract standard but inconsistent with surrounding code creates long-term maintenance cost.
- Confident, well-formatted output is not evidence of correctness. Agents produce fluent code and comments regardless of whether the underlying logic is right — treat fluency as a red herring, not a signal.
- Volume alone is not progress. An agent can produce a large, polished-looking diff quickly; apply the same size/pace discipline (200-400 LOC, split if larger) rather than waving it through because it looks thorough.
- Prefer smaller, more frequent agent-authored PRs over one large one for the same reason large PRs are hard to review from humans — the failure mode (skimming, fatigue, missed edge cases) is identical regardless of who wrote the diff.

## Merge Queues and Stacked PRs

Use merge queues when the team has enough throughput that serial merge conflicts or broken main are the real bottleneck.

- GitHub has native merge queue support
- GitLab and Bitbucket workflows rely more heavily on approvals and CI policy, or third-party queueing tools
- Stacked PRs help only when the team is already disciplined about small changes and dependency ordering

Do not recommend stacked PR tooling by default for every team. It adds process overhead and is only worth it when:

- features regularly span multiple dependent changes
- CI cost or branch divergence is a recurring pain
- reviewers already struggle with oversized PRs

### Stacked PRs vs. Trunk-Based Development

Both aim at the same goal — small, fast-moving, reviewable changes — but they solve different bottlenecks and are not mutually exclusive:

- **Trunk-based development** (short-lived branches, frequent merges to `main`, feature flags for incomplete work) reduces integration risk and keeps `main` releasable. It works best when the team can flag-gate incomplete features and has strong CI.
- **Stacked PRs** (Graphite, Git Town, or a host's native stacking feature) solve the "one feature, several dependent reviewable changes" problem without waiting for each PR to merge before starting the next. They add tooling and mental overhead (rebase propagation, review-order discipline) that only pays off once PRs are already disciplined about size.
- These compose: a team can practice trunk-based development *and* stack PRs for a single feature, merging each stacked PR to trunk as it is approved rather than waiting for the whole stack.
- Do not adopt stacked-PR tooling to compensate for oversized, undisciplined PRs — fix the sizing problem first, or the stack itself becomes hard to review.

## Recommendation Framework

When a user asks what to adopt:

1. Start with the repository host's native controls.
2. Add deterministic scanners next.
3. Add an AI review bot only if the team has bandwidth to manage noise and trust boundaries.
4. Add merge queues or stacked PR tooling only when integration contention is already measurable.

This framework sequences *which tools to adopt*. Once an AI review bot exists (step 3), a separate question follows: which per-diff decisions inside that tool should stay deterministic rather than becoming a model call — pre-review file filtering, whether a diff needs an extra planning pass, and how to filter the tool's own false positives before a human sees them. See [deterministic-vs-llm-routing.md](deterministic-vs-llm-routing.md) for that narrower, within-a-single-review-pass layer.

## Sources to Open First

- `../data/sources.json` for verified links
- GitHub Copilot review, repository instructions, and merge queue docs
- GitLab Duo review instructions and merge request approvals docs
- Bitbucket Code Insights docs
- CodeRabbit docs or the current PR-Agent repository only when the user asks about those tools specifically — re-resolve the PR-Agent repo location before citing it, since it moved to community governance in 2026
