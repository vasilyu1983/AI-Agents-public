# Environment Promotion Workflow Template

*Purpose: Promote a versioned infrastructure artifact through environments with per-environment state isolation, a plan review gate at each step, and rollback by re-promotion.*

## When to Use

- Moving an infrastructure change from dev → stage → prod
- Standing up a new environment from an existing, proven configuration
- Defining who approves what, and what "rollback" concretely means for infrastructure

## Core Rules (read before filling in)

1. **The promotion unit is a versioned module or artifact, not raw code.** Promote a pinned module version (`ref=v1.4.2`), not a Git branch that keeps moving. Merging a branch is not a promotion — it is a change of what "latest" means in every environment that tracks it.
2. **Each environment owns its own state and its own backend credentials.** Separate folders, separate state files, separate authentication. See [../../references/terraform-state-architecture.md](../../references/terraform-state-architecture.md).
3. **Every environment gets its own plan review.** A plan that was reviewed against stage tells you nothing about what the same code does against prod, because the two environments have different existing state.
4. **Check drift before promoting.** Promoting onto a drifted environment means the plan you review is not the change you intended.
5. **Rollback = re-promote the previous known-good version.** There is no `terraform undo`.

---

# TEMPLATE STARTS HERE

## 1. Promotion Unit

- **Artifact type:** (Terraform module tag / container image digest / packaged stack)
- **Version identifier being promoted:**
- **Source of truth for the version:** (Git tag, registry, artifact store)
- **Immutable?** yes / no — if no, state why and what compensates
- **Changelog / PR link:**

```hcl
# Environments differ ONLY in the version pin and their inputs.
module "service" {
  source = "git::https://github.com/ORG/REPO.git//modules/service?ref=v1.4.2"

  environment   = "stage"
  instance_type = var.instance_type
}
```

## 2. Environment Ladder

| Order | Environment | State backend / account | Approver | Soak time before next promote |
|-------|-------------|-------------------------|----------|-------------------------------|
| 1 | dev | | | |
| 2 | stage | | | |
| 3 | prod | | | |

- **Environments are skipped when:** (define explicitly — e.g. break-glass security patch, and who authorises it)

## 3. Per-Environment State Isolation

- [ ] Separate folder per environment (`stage/`, `prod/`, `mgmt/`, `global/`)
- [ ] Separate backend per environment (separate bucket/account, not just a separate key)
- [ ] Separate credentials/roles per environment — prod credentials are not available from the stage pipeline
- [ ] Separate state per component within the environment (network, data stores, services)
- [ ] `terraform workspace` is **not** used to separate environments (see the state-architecture reference for why)

| Environment | Backend location | State key | Credential / role | Who can apply |
|-------------|------------------|-----------|-------------------|---------------|
| stage | | | | |
| prod | | | | |

## 4. Pre-Promotion Gate

Run against the **target** environment before promoting into it.

- [ ] Drift check clean: `terraform plan -detailed-exitcode` returns 0 for the target env, or the drift is explained and accepted below
- [ ] Version currently deployed in the target recorded (this is your rollback target)
- [ ] Version passed all checks in the previous environment on the ladder
- [ ] Soak time in the previous environment elapsed
- [ ] Dependent stacks (network, data) are on compatible versions

**Drift found (if any):**

| Resource | Drift observed | Source (manual change? external controller?) | Resolution before promote |
|----------|----------------|----------------------------------------------|---------------------------|
| | | | |

## 5. Plan Review Gate (per environment)

- **Plan command:** `terraform plan -out plan.tfplan` (target env directory)
- **Reviewed by:**
- **Date/time:**

- [ ] Resource **destroy/replace** count reviewed line by line — no unintended replacements
- [ ] No data-store or stateful resource is being replaced (or the data migration plan is linked)
- [ ] Change count matches expectation from the previous environment's plan
- [ ] Plan file is **not** published as an unencrypted artifact — plan files contain secrets in plain text; share the `terraform show` text output with sensitive values marked `sensitive = true`. See [template-iac-terraform.md](template-iac-terraform.md) §7.1

**Expected changes:** _add __ / change __ / destroy ___

**Unexpected entries in the plan (must be empty to proceed):**

## 6. Apply

- **Applied by:**
- **Apply started / finished:**
- **Post-apply verification:** (smoke test, health endpoint, SLO check — name the concrete check)
- [ ] Verification passed
- [ ] Deployed version recorded in the environment inventory

## 7. Rollback

Rollback is a promotion of the previous version, run through the same gates.

- **Previous known-good version:**
- **Rollback command:** repin the module `ref` to the previous version, plan, review, apply
- [ ] Rollback plan reviewed for **irreversible** steps: dropped columns, deleted buckets, released IPs, rotated secrets — these do not roll back and need a forward fix instead
- [ ] Rollback tested at least once in a non-production environment
- **Forward-fix instead of rollback when:** (state the condition — typically any change that destroyed or migrated data)

## 8. Records

| Field | Value |
|-------|-------|
| Environment promoted to | |
| Version promoted | |
| Version replaced | |
| Approver | |
| Plan reviewed by | |
| Applied by | |
| Verification result | |

## Quality Checklist

- [ ] Promotion moves an immutable, versioned artifact — not a branch pointer
- [ ] Environment differences live in input variables, not in forked copies of the code
- [ ] Each environment has isolated state, backend, and credentials
- [ ] Drift is checked before, not discovered during, the promote
- [ ] Each environment has its own reviewed plan before apply
- [ ] Plan files are handled as secret-bearing artifacts
- [ ] The previous version is recorded so rollback has a concrete target
- [ ] Irreversible changes are identified up front and routed to forward-fix

## Related Templates

- [template-iac-terraform.md](template-iac-terraform.md) — root module structure, CI workflow, drift detection
- [template-module.md](template-module.md) — reusable child module (the thing being versioned and promoted)
- [../../references/terraform-state-architecture.md](../../references/terraform-state-architecture.md) — why file layout beats workspaces for environment isolation
- [../cicd-pipelines/template-gitops.md](../cicd-pipelines/template-gitops.md) — GitOps promotion pipeline
- [../cicd-pipelines/template-release-safety.md](../cicd-pipelines/template-release-safety.md) — release gates and rollback

## Sources

- Brikman, *Terraform: Up & Running* (3e), Ch3 "How to Manage Terraform State" — isolation via file layout, per-environment backends and access controls, component-level state splitting
- Brikman, Ch6 "Managing Secrets with Terraform" — plan and state files store secrets in plain text
- Morris, *Infrastructure as Code* (2e), Ch7/Ch20 — environment progression, minimizing automation lag, continuous application over ad hoc apply
