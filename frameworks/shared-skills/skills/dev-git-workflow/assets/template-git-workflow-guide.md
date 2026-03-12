# Git Workflow Guide (Trunk-Based and GitFlow)

Use this template to standardize branching, PRs, releases, and hotfixes.

---

## Core

## 1) Choose a Model (Decision Matrix)

| Team/Product Constraint | Recommended Model |
|------------------------|-------------------|
| Continuous deploy, strong CI, feature flags available | Trunk-based |
| Many devs, many daily merges, strong CI, need fast feedback | Trunk-based (+ merge queue) |
| Scheduled releases, multiple supported versions | GitFlow |
| Low CI maturity, manual releases, strict release gates | GitFlow (temporary) |

---

## 2) Trunk-Based Workflow (Default for Modern Teams)

### Branches

- `main` (trunk): always releasable
- Short-lived branches: `feat/*`, `fix/*`, `chore/*` (lifetime hours to a few days)

### Flow

1. Branch from `main`
2. Small commits (Conventional Commits)
3. Open PR early (draft PR encouraged)
4. CI gates + review
5. Merge (squash or merge-commit; pick one)
6. Deploy from `main` (continuous) or tag releases

### Release and Hotfix

- Prefer forward fixes on `main`.
- For critical incidents: short-lived `hotfix/*` from `main`, merge back, tag if needed.

### Required Guardrails

- Branch protection on `main` (PRs only, required checks, required reviews)
- Merge queue for high-traffic repos (keeps `main` green under concurrency)
- Feature flags for incomplete work (avoid long-lived branches)

---

## 3) GitFlow Workflow (When Scheduled Releases Dominate)

### Branches

- `main`: production releases (tagged)
- `develop`: integration branch (must stay green)
- `release/*`: stabilization for a scheduled release
- `hotfix/*`: emergency fixes from `main`

### Flow

1. Feature branches off `develop`
2. Merge to `develop` behind CI gates
3. Cut `release/x.y` branch for stabilization
4. Fixes go into `release/x.y` and are merged back to `develop`
5. Merge `release/x.y` to `main`, tag release, deploy

### Risks to Manage

- Merge debt between `develop` and `main`
- Long-lived release branches drifting from trunk
- Slower feedback cycles (invest in CI to transition to trunk-based over time)

---

## 4) Merge Strategy (Pick and Enforce)

| Strategy | Pros | Cons | Recommended Use |
|----------|------|------|-----------------|
| Squash merge | Clean history, easy reverts | Loses commit granularity | Most product repos |
| Merge commit | Preserves branch context | Noisier history | Repos needing branch topology |
| Rebase merge | Linear history | Risky for shared branches | Small teams with strong git discipline |

Rules:

- Never rebase shared branches (`main`, `develop`, `release/*`) after publishing.
- Use `--force-with-lease` only on personal feature branches.

---

## 5) PR Checklist (Minimum)

- [ ] Clear description: what/why/how, testing evidence
- [ ] Small and reviewable (<400 LOC preferred; split if larger)
- [ ] CI: tests, lint, security scan where applicable
- [ ] No secrets, credentials, or sensitive data
- [ ] Rollout and rollback notes for risky changes

Template: [pull-requests/pr-template.md](pull-requests/pr-template.md)

---

## Optional: AI/Automation

- PR summaries and changelog drafts (human-verified)
- Change risk labeling based on file paths (human-approved)
- Suggested reviewers based on CODEOWNERS/history (human-confirmed)

### Bounded Claims

- Automation cannot replace ownership, review, or release approval.
