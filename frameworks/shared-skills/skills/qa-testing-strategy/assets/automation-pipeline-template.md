# Automation Pipeline Template

- **Triggering events:** PR open/update, nightly, release branch, hotfix path  
- **Stages:** Lint → unit → component/contract → integration → E2E → performance → security scans  
- **Parallelization:** Which suites can parallelize; shard strategy; caching plan  
- **Environment setup:** Containers/services required, seeding scripts, secrets handling  
- **Quality gates:** Required checks, coverage thresholds, allowed flake rate, blocking vs warning jobs  
- **Artifacts:** Test reports, coverage, screenshots/videos, traces, SBOMs  
- **Rollbacks:** What to do on failure; auto-revert, feature flag toggles, chat notifications  
- **Governance:** Owners, escalation path, maintenance cadence for dependencies and flaky tests  
