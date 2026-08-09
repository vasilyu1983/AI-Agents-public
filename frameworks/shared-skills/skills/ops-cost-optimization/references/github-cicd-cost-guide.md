# GitHub and CI/CD Cost Guide

Operational reference for understanding and reducing GitHub platform spend and CI/CD pipeline costs. Covers GitHub plan tiers, metered services, common waste patterns, and alternative providers.

## Table of Contents

- [GitHub Plan Tiers](#github-plan-tiers)
- [GitHub Actions](#github-actions)
- [GitHub Copilot](#github-copilot)
- [Git LFS](#git-lfs)
- [GitHub Codespaces](#github-codespaces)
- [GitHub Packages](#github-packages)
- [Common Waste Patterns](#common-waste-patterns)
- [Optimization Checklist](#optimization-checklist)
- [FinOps-as-Code: IaC Cost Guardrails](#finops-as-code-iac-cost-guardrails)
- [CI/CD Alternatives](#cicd-alternatives)
- [Deployment Platform Alternatives](#deployment-platform-alternatives)

---

## GitHub Plan Tiers

### Free

- Unlimited public and private repositories
- 2,000 Actions minutes per month (Linux runners)
- 500 MB GitHub Packages storage
- Community support only
- No required reviewers on private repos
- 120 core-hours Codespaces per month

### Team ($4/user/month)

- Everything in Free, plus:
- 3,000 Actions minutes per month
- 2 GB Packages storage
- Required reviewers, CODEOWNERS, draft PRs
- GitHub Support (standard response times)

### Enterprise ($21/user/month)

- Everything in Team, plus:
- 50,000 Actions minutes per month
- 50 GB Packages storage
- SAML SSO, audit log streaming, IP allow lists
- GitHub Advanced Security (code scanning, secret scanning, dependency review)
- GitHub Connect for hybrid cloud/server deployments

### Decision: Free vs. Team vs. Enterprise

Upgrade to Team when you need required reviewers on private repos, CODEOWNERS enforcement, or more than 2,000 Actions minutes per month.

Upgrade to Enterprise when you need SSO, compliance tooling, Advanced Security, or run a large engineering organization with governance requirements.

Stay on Free for small teams, open-source projects, and early-stage startups that fit within the included limits.

---

## GitHub Actions

### Minutes Pricing by Runner OS

GitHub-hosted runners consume included minutes at different rates depending on the OS:

| Runner OS | Minute Multiplier | Effective Cost per Minute (Pro/Team overage) |
|-----------|-------------------|----------------------------------------------|
| Linux     | 1x                | $0.008                                       |
| Windows   | 2x                | $0.016                                       |
| macOS     | 10x               | $0.08                                        |

A 10-minute macOS job consumes 100 included minutes. The same job on Linux consumes 10.

### Storage

- Artifacts and caches share a storage pool per repository.
- Free tier: 500 MB. Team: 2 GB. Enterprise: 50 GB.
- Artifacts are retained for 90 days by default. Caches are evicted after 7 days of non-use.
- Overage storage is billed at $0.25/GB/month.

### Larger Runners

GitHub offers larger hosted runners (4-core, 8-core, 16-core, 32-core, 64-core) on Linux, Windows, and macOS.

- Billed per minute at higher rates (e.g., 4-core Linux at $0.032/min, 8-core at $0.064/min).
- Useful for build-heavy workloads where faster completion reduces total cost.
- Evaluate whether a larger runner finishing in half the time is cheaper than a standard runner running twice as long.

---

## GitHub Copilot

### Plans

| Plan | Price | Notes |
|------|-------|-------|
| Individual | $10/month or $100/year | Single developer, personal account |
| Business | $19/user/month | Org-level management, policy controls, audit logs |
| Enterprise | $39/user/month | Everything in Business plus knowledge bases, fine-tuning, and Copilot in CLI |

### Cost Considerations

- Business seats are billed for every assigned user, not for active users. Unused seats cost the same as active ones.
- Audit actual usage per developer. Copilot exposes usage metrics in the org admin dashboard (completions accepted, suggestions shown).
- Developers who rarely use IDE completions may not justify the seat cost.
- Evaluate quarterly: remove seats for developers who consistently show low adoption.
- For teams under 10 developers, Individual plans may be cheaper than Business if you do not need centralized policy controls.

---

## Git LFS

### Included Allowances

- 1 GB free storage per repository
- 1 GB free bandwidth per month

### Overage Pricing

- Storage: $5 per 50 GB data pack/month
- Bandwidth: $5 per 50 GB data pack/month

### Common Waste

- Storing files in LFS that do not need it (small files, text files, files that compress well in Git)
- Tracking entire directories of build artifacts instead of using artifact storage
- Forgetting to clean up old LFS objects after removing tracked files from the repo (objects persist in LFS storage)

### Optimization

- Only use LFS for binary files over ~1 MB that change frequently (design assets, compiled binaries, large media)
- Store build artifacts in GitHub Packages, artifact storage, or external object storage instead of LFS
- Use `git lfs prune` periodically to remove local copies of old LFS objects
- For open-source projects, consider hosting large assets externally (CDN, R2) and referencing them by URL

---

## GitHub Codespaces

### Billing Model

Codespaces bills two dimensions:

1. **Compute (per hour):** Charged while the Codespace is running. Rate depends on machine type.
2. **Storage (per GB/month):** Charged for the Codespace disk image, whether running or stopped.

| Machine Type | Compute Cost/Hour |
|-------------|-------------------|
| 2-core      | $0.18             |
| 4-core      | $0.36             |
| 8-core      | $0.72             |
| 16-core     | $1.44             |
| 32-core     | $2.88             |

Storage: $0.07/GB/month.

### Common Waste

- Codespaces left running after development sessions end
- Using 8-core or 16-core machines for tasks that run fine on 2-core or 4-core
- Accumulating stopped Codespaces that still incur storage charges
- Dev containers with large base images inflating storage costs

### Optimization

- Set auto-stop timeout to 30 minutes (org-level policy or user setting)
- Default to 2-core machines; upgrade only when builds or tests require more
- Delete Codespaces after feature branches are merged
- Use lightweight dev container images (slim base images, multi-stage builds)
- Set retention policies at the org level to auto-delete stopped Codespaces after N days

---

## GitHub Packages

### Included Allowances

Per plan tier (shared across all packages in the org):

| Plan | Storage | Data Transfer |
|------|---------|---------------|
| Free | 500 MB | 1 GB/month |
| Team | 2 GB | 10 GB/month |
| Enterprise | 50 GB | 100 GB/month |

### Overage Pricing

- Storage: $0.25/GB/month
- Data transfer: $0.50/GB

### Optimization

- Delete old package versions regularly. Use the GitHub Actions `delete-package-versions` action or the API.
- Use container registries with cheaper or free storage (e.g., GitHub Container Registry for public images is free) when publishing public images.
- For private packages with high download volume, consider self-hosted registries or cloud-native registries with cheaper egress.

---

## Common Waste Patterns

Ranked by typical cost impact:

1. **macOS runners for non-Apple workloads.** Teams using macOS runners for tasks that run identically on Linux. A 10-minute Linux job costs 10 minutes; the same job on macOS costs 100 minutes. This is the single most common source of inflated Actions bills.

2. **Long-running workflows without caching.** Installing dependencies from scratch on every run instead of caching `node_modules`, `.gradle`, `pip`, or `cargo` caches. Doubles or triples workflow duration.

3. **Redundant CI runs.** Running the full test suite on every push to a feature branch when only docs or config changed. Running CI on draft PRs that are not ready for review.

4. **Unused Copilot seats.** Paying for Business seats for developers who do not use completions or who use alternative tools. No automatic seat reclamation by default.

5. **Stale Codespaces.** Stopped Codespaces accumulating storage charges. Developers forgetting to delete them after branch completion.

6. **LFS for files that don't need it.** Tracking small files, text-based configs, or auto-generated files in LFS. Each tracked file adds to storage and bandwidth costs.

7. **Artifact retention defaults.** Default 90-day artifact retention for workflows that only need artifacts for the duration of the pipeline run. Large artifacts (test reports, coverage files) accumulating across hundreds of runs.

8. **Superseded workflow runs.** Multiple concurrent CI runs for the same PR when the developer pushes several commits in quick succession. Only the latest run matters.

---

## Optimization Checklist

Apply in order of typical impact:

1. **Use Linux runners for everything that does not require macOS or Windows.** Move unit tests, linting, formatting, Docker builds, and deployment jobs to Linux. Reserve macOS for iOS/macOS builds and Windows for .NET Framework or Windows-specific testing only.

2. **Cache dependencies aggressively.** Use `actions/cache` or the built-in caching in `actions/setup-node`, `actions/setup-python`, etc. Cache lockfile hashes. Verify cache hits in workflow logs.

3. **Skip redundant CI runs.** Use path filters to skip CI when only docs, README, or non-code files change:
   ```yaml
   on:
     push:
       paths-ignore:
         - 'docs/**'
         - '*.md'
         - '.gitignore'
   ```

4. **Cancel superseded workflow runs.** Add concurrency groups to cancel in-progress runs when a new push arrives:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```

5. **Audit Copilot usage quarterly.** Review the Copilot usage dashboard in org settings. Remove seats for developers with consistently low acceptance rates or zero usage.

6. **Clean up old artifacts.** Reduce artifact retention to the minimum needed (1-7 days for CI artifacts that are only consumed within the pipeline):
   ```yaml
   - uses: actions/upload-artifact@v4
     with:
       retention-days: 3
   ```

7. **Set Codespaces auto-stop and retention policies.** Configure org-level idle timeout (30 minutes) and auto-delete for stopped Codespaces (14 days).

8. **Right-size Codespace machine types.** Default to 2-core. Provide 4-core or 8-core only for repos with heavy build requirements.

9. **Review LFS tracked files.** Remove LFS tracking for files under 1 MB or files that do not change. Migrate large static assets to external object storage.

10. **Use self-hosted runners for high-volume pipelines.** If Actions minutes consistently exceed included allowances, self-hosted runners eliminate per-minute charges. The trade-off is infrastructure maintenance.

---

## FinOps-as-Code: IaC Cost Guardrails

Shift cost awareness left into the CI pipeline so infrastructure cost increases are caught at code review, before they reach production. This is sometimes called "FinOps-as-code" — the practice of treating cost budgets as policy enforced in the pipeline, alongside security and quality checks.

### Infracost: PR-level cost diffs

Infracost is an open-source tool that integrates with Terraform, Pulumi, and other IaC tools to compute a cost estimate for each pull request and post it as a PR comment.

**What it does:**
- Parses IaC plan output to identify resource changes.
- Fetches provider pricing and estimates monthly cost for the proposed infrastructure.
- Posts a cost diff comment on the PR: current cost, proposed cost, and the delta.
- Optionally fails the CI check when cost exceeds a configured threshold.

**Example PR comment output (illustrative):**

```
Monthly cost estimate
  Before: $142/month
  After:  $218/month
  Change: +$76/month (+53%)

  Top cost drivers:
  + aws_rds_instance.primary: +$62/month (db.t3.medium → db.r6g.large)
  + aws_nat_gateway.main: +$14/month (new resource)
```

**Reference:** Infracost docs — https://www.infracost.io/docs/infracost_cloud/guardrails/

Infracost raised a $15M Series A on 2025-11-18 (led by Pruven Capital, with Y Combinator and Sequoia Capital participating) to expand FinOps-left capabilities, including budget enforcement in pipelines.

### Setting budget-threshold merge gates

Infracost supports policy-as-code guardrails that block merges when a PR exceeds a cost threshold.

**Basic guardrail setup (Infracost Cloud):**

1. Define a budget policy in the Infracost Cloud dashboard or as a `infracost.yml` config file:
   - Absolute threshold: block if monthly cost delta exceeds $X.
   - Percentage threshold: block if cost increase exceeds N% of current baseline.
   - Per-resource threshold: block if a single new resource exceeds $Y/month.

2. Connect to CI (GitHub Actions example):

```yaml
- name: Infracost diff
  uses: infracost/actions/setup@v3

- name: Run Infracost
  run: |
    infracost diff \
      --path=. \
      --format=json \
      --out-file=/tmp/infracost.json

- name: Post Infracost comment
  uses: infracost/actions/comment@v3
  with:
    path: /tmp/infracost.json
    behavior: update

- name: Check cost policy
  uses: infracost/actions/comment@v3
  with:
    path: /tmp/infracost.json
    policy-path: infracost-policy.rego   # OPA policy file
```

3. OPA (Open Policy Agent) policies let you express cost guardrails as code alongside your other policy checks:

```rego
# infracost-policy.rego — block PRs that increase cost by more than $50/month
deny[msg] {
  diff := input.diffTotalMonthlyCost
  diff > 50
  msg := sprintf("PR increases monthly cost by $%.2f. Budget threshold is $50.", [diff])
}
```

### When to use IaC cost guardrails

| Situation | Recommendation |
|-----------|---------------|
| Team deploys IaC changes frequently (weekly or more) | Add Infracost to every PR pipeline |
| Single developer, infrequent infra changes | Manual cost review before merge is sufficient |
| Cloud costs are a top-3 business concern | Set hard block thresholds; require approvals for large deltas |
| Early-stage, minimal IaC | Skip — overhead outweighs benefit; revisit at scale |

### Scope of this skill

Infracost addresses IaC-managed resources (cloud VMs, databases, load balancers, managed services). It does not cover:
- SaaS usage-based costs (Vercel, Supabase, AI APIs) — those are tracked via platform dashboards and the monitoring setup in [cost-monitoring-setup.md](cost-monitoring-setup.md).
- Runtime usage costs that are not determinable from IaC — these require observability tooling.

---

## CI/CD Alternatives

Comparison of CI/CD platforms for teams evaluating options beyond GitHub Actions.

| Platform | Free Tier | Paid Starting At | Key Strengths | Key Limitations |
|----------|-----------|-------------------|---------------|-----------------|
| GitHub Actions | 2,000 min/month (Linux) | $0.008/min overage | Native GitHub integration, marketplace of actions | macOS minutes are expensive (10x), no built-in dashboard |
| GitLab CI | 400 min/month (shared runners) | $5/user/month (Premium) | Built-in container registry, Auto DevOps, security scanning | Smaller action marketplace, heavier platform |
| Bitbucket Pipelines | 50 min/month | $0.01/min overage, $15/user/month (Standard) | Tight Jira/Atlassian integration | Very limited free tier, fewer integrations |
| CircleCI | 6,000 credits/month (~30 min on medium) | $15/month (Performance) | Strong caching, parallelism, Docker layer caching | Credit-based billing is confusing, free tier is thin |
| Buildkite | Free for up to 3 users | $15/user/month | Agent-based (self-hosted compute), fast, scales well | Requires managing your own build infrastructure |
| Self-hosted runners (GitHub) | Free minutes (runs on your infra) | Cost of infrastructure | No per-minute charges, full control over environment | You manage provisioning, security, updates, and scaling |
| Dagger | Open-source engine (free) | Cloud pricing varies | Portable pipelines (run anywhere), container-native | Newer ecosystem, smaller community |

### Decision Framework

- **Default to GitHub Actions** if you are already on GitHub and within included minutes.
- **Switch to self-hosted runners** if you consistently exceed included minutes or need specialized hardware (GPUs, ARM).
- **Consider GitLab CI** if you want built-in security scanning and are open to moving the repository.
- **Use Buildkite** if you need high-scale CI with your own compute and want minimal vendor lock-in.
- **Evaluate CircleCI** for teams that need advanced parallelism and Docker layer caching and are willing to manage credit-based billing.

---

## Deployment Platform Alternatives

For teams evaluating deployment hosting alongside CI/CD decisions.

| Platform | Free Tier | Paid Starting At | Best For |
|----------|-----------|-------------------|----------|
| Railway | $5/month credit on Hobby | $5/month + usage-based compute and bandwidth | Backend services, databases, always-on workers |
| Render | Static sites free, services from $7/month | $7/month per service | Simple web services, static sites, managed PostgreSQL |
| Netlify | 100 GB bandwidth, 300 build min/month | $19/month (Pro) | Static sites, JAMstack, serverless functions |
| Fly.io | 3 shared VMs, 160 GB outbound/month | Pay-per-use (VMs from ~$2/month) | Edge compute, global distribution, always-on containers |
| Cloudflare Pages | Unlimited bandwidth, 500 builds/month | Free (Workers Paid at $5/month) | Static sites, SSR via Workers, zero egress |

### Decision Framework

- **Railway** for backend-heavy projects that need databases, workers, and cron alongside the app. Simple pricing model. Good DX for small teams.
- **Render** for straightforward web services where you want managed infrastructure without complexity. Static sites are free.
- **Netlify** for JAMstack sites, form handling, and identity/auth add-ons. Strong ecosystem for frontend-first projects.
- **Fly.io** for globally distributed services that need low latency at the edge. Pay-per-use model suits variable traffic.
- **Cloudflare Pages** for static sites and SSR apps where bandwidth cost is a concern. Zero egress fees make it the cheapest option for high-traffic static content.
