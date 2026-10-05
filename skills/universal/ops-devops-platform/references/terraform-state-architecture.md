# Terraform State Architecture

*Purpose: Decide how to split Terraform state across environments and components, and why `terraform workspace` is the wrong tool for environment isolation.*

*Use when:* Designing or reviewing a Terraform/OpenTofu repository layout, choosing a backend, or answering "should we use workspaces for staging vs production?"

## Table of Contents

- [The Bulkhead Framing](#the-bulkhead-framing)
- [Why `terraform workspace` Is Disqualified for Environment Isolation](#why-terraform-workspace-is-disqualified-for-environment-isolation)
- [What Workspaces Are Actually For](#what-workspaces-are-actually-for)
- [Isolation via File Layout](#isolation-via-file-layout)
- [Component-Level State Splitting](#component-level-state-splitting)
- [Recommended Directory Layout](#recommended-directory-layout)
- [Secrets in State: Consequences for Backend Choice](#secrets-in-state-consequences-for-backend-choice)
- [Decision Table](#decision-table)
- [Review Checklist](#review-checklist)
- [Sources](#sources)

---

## The Bulkhead Framing

Brikman's argument for splitting state is a ship metaphor: "Just as a ship has bulkheads that act as barriers to prevent a leak in one part of the ship from immediately flooding all the others, you should have 'bulkheads' built into your Terraform design."

The failure this prevents is concrete. If all environments live in one set of configurations and therefore one state file, then "while trying to deploy a new version of your app in staging, you might break the app in production. Or, worse yet, you might corrupt your entire state file … and now all of your infrastructure in all environments is broken."

His framing of the contradiction is the part worth carrying: "The whole point of having separate environments is that they are isolated from one another, so if you are managing all the environments from a single set of Terraform configurations, you are breaking that isolation."

There are two mechanisms for isolating state, and Brikman assigns them to different jobs:

- **Isolation via workspaces** — "Useful for quick, isolated tests on the same configuration"
- **Isolation via file layout** — "Useful for production use cases for which you need strong separation between environments"

## Why `terraform workspace` Is Disqualified for Environment Isolation

Workspaces store state in multiple separate named paths within the *same* backend. Switching workspace "is equivalent to changing the path where your state file is stored" — and that is the whole of the isolation they provide. Brikman gives three drawbacks, which compound:

**1. Shared backend, therefore shared authentication and access control.**

> "The state files for all of your workspaces are stored in the same backend (e.g., the same S3 bucket). That means you use the same authentication and access controls for all the workspaces, which is one major reason workspaces are an unsuitable mechanism for isolating environments (e.g., isolating staging from production)."

**2. Invisible in the code and on the terminal.**

> "Workspaces are not visible in the code or on the terminal unless you run `terraform workspace` commands. When browsing the code, a module that has been deployed in one workspace looks exactly the same as a module deployed in 10 workspaces. This makes maintenance more difficult, because you don't have a good picture of your infrastructure."

**3. Error-prone — the two above combine into no defence in depth.**

> "Putting the two previous items together, the result is that workspaces can be fairly error prone. The lack of visibility makes it easy to forget what workspace you're in and accidentally deploy changes in the wrong one (e.g., accidentally running `terraform destroy` in a 'production' workspace rather than a 'staging' workspace), and because you must use the same authentication mechanism for all workspaces, you have no other layers of defense to protect against such errors."

His conclusion: "Due to these drawbacks, workspaces are not a suitable mechanism for isolating one environment from another: e.g., isolating staging from production."

Note the shape of reason 3 — it is not an independent objection. It says that reasons 1 and 2 remove the two things that would otherwise catch the mistake: you cannot see which environment you are in, and the credentials would not have stopped you anyway. That is why "we're careful" is not a mitigation.

## What Workspaces Are Actually For

Workspaces are genuinely useful for the case Brikman names: "when you already have a Terraform module deployed and you want to do some experiments with it (e.g., try to refactor the code) but you don't want your experiments to affect the state of the already-deployed infrastructure."

That is a short-lived, same-credentials, same-blast-radius scenario — an engineer testing a refactor against their own sandbox — which is exactly where the three drawbacks do not bite.

The `terraform.workspace` expression lets module behavior vary by workspace (e.g. a smaller instance type outside the default workspace to save money while experimenting). Treat that as an experimentation convenience, not as an environment-configuration mechanism: using it to encode staging-vs-production differences reintroduces every problem above.

## Isolation via File Layout

To get full isolation, Brikman requires two things together:

1. "Put the Terraform configuration files for each environment into a separate folder." — `stage/`, `prod/`, and so on.
2. "Configure a different backend for each environment, using different authentication mechanisms and access controls: e.g., each environment could live in a separate AWS account with a separate S3 bucket as a backend."

Both halves matter. Separate folders alone give you visibility but not defence; separate backends alone give you defence but not legibility. Together, "the use of separate folders makes it much clearer which environments you're deploying to, and the use of separate state files, with separate authentication mechanisms, makes it significantly less likely that a screw-up in one environment can have any impact on another."

## Component-Level State Splitting

The isolation argument does not stop at the environment boundary. Brikman extends it "down to the 'component' level, where a component is a coherent set of resources that you typically deploy together."

The driver is **rate of change**. A VPC and its subnets, routing rules, VPNs, and network ACLs change "only once every few months, at most"; a web server might deploy "multiple times per day." Managing both in one configuration means "you are unnecessarily putting your entire network topology at risk of breakage (e.g., from a simple typo in the code or someone accidentally running the wrong command) multiple times per day."

His recommendation: "separate Terraform folders (and therefore separate state files) for each environment (staging, production, etc.) and for each component (VPC, services, databases) within that environment."

This is the same principle Morris arrives at from the stack-sizing direction — see [stack-sizing-patterns.md](stack-sizing-patterns.md), where differing change rates within one stack is the diagnostic for splitting it.

## Recommended Directory Layout

Top level: one folder per environment. Brikman's typical set:

| Folder | Purpose (Brikman's definition) |
|--------|--------------------------------|
| `stage` | "An environment for pre-production workloads (i.e., testing)" |
| `prod` | "An environment for production workloads (i.e., user-facing apps)" |
| `mgmt` | "An environment for DevOps tooling (e.g., bastion host, CI server)" |
| `global` | "A place to put resources that are used across all environments (e.g., S3, IAM)" |

Within each environment, one folder per component — typically `vpc` (network topology), `services` (apps/microservices, each app optionally in its own folder), `data-storage` (data stores, each optionally in its own folder).

Within each component, the minimum file convention: `variables.tf` (input variables), `outputs.tf` (output variables), `main.tf` (resources and data sources). Terraform reads any `.tf` file in the directory, so this convention is for humans — "although Terraform may not care about filenames, your teammates probably do."

```text
stage/
  vpc/
  services/
    webserver-cluster/
      main.tf
      variables.tf
      outputs.tf
  data-storage/
    mysql/
prod/
  vpc/
  services/
  data-storage/
mgmt/
global/
  s3/
  iam/
```

Optional extensions Brikman names: `dependencies.tf` (all data sources, "to make it easier to see what external things the code depends on"), `providers.tf` (provider blocks, so you can see "what providers the code talks to and what authentication you'll have to provide"), and `main-xxx.tf` splits (`main-iam.tf`, `main-s3.tf`) when `main.tf` grows. He adds a caveat on the last one: struggling to break a very large resource count across many files "might be a sign that you should break your code into smaller modules instead."

Keep the backend `key` mapped 1:1 to the folder path (e.g. `stage/services/webserver-cluster/terraform.tfstate`), so the state layout mirrors the code layout and neither can drift from the other silently.

## Secrets in State: Consequences for Backend Choice

State is not a neutral bookkeeping file. Brikman: **"All data in Terraform state files is stored in plain text."** Concretely, "if you use the `aws_db_instance` resource to create a database, Terraform will store the username and password for the database in a state file in plain text, and you shouldn't store plain text secrets in version control."

He notes this "has been an open issue since 2014, with no clear plans for a first-class solution," and warns off the workarounds: "There are some workarounds out there that can scrub secrets from your state files, but these are brittle and likely to break with each new Terraform release, so I don't recommend them."

Two requirements follow, and they are what should drive the backend decision:

**Store state in a backend that supports encryption.** Remote backends such as S3, GCS, and Azure Blob Storage "will encrypt your state files, both in transit (e.g., via TLS) and on disk (e.g., via AES-256)." Brikman is honest about the ceiling: "It would be better still if Terraform natively supported encrypting secrets within the state file, but these remote backends reduce most of the security concerns, given that at least the state file isn't stored in plain text on disk anywhere."

**Strictly control who can access the backend.** "Since Terraform state files may contain secrets, you'll want to control who has access to your backend with at least as much care as you control access to the secrets themselves." His example: an IAM policy granting access to the production state bucket "to a small handful of trusted devs, or perhaps solely just the CI server you use to deploy to prod."

This is a second, independent argument against workspaces for environments: workspaces cannot satisfy the second requirement at all, because every workspace shares one backend and therefore one access-control boundary. Production database credentials would sit behind the same policy as staging's.

The same plaintext property applies to saved plan files — see [../assets/terraform-iac/template-iac-terraform.md](../assets/terraform-iac/template-iac-terraform.md) §7.1.

Remote backends also solve two problems unrelated to isolation: they remove manual state-handling error (Terraform loads and stores state automatically on every plan/apply), and most support locking natively, so a second `apply` waits rather than racing (`-lock-timeout=<TIME>` bounds the wait).

## Decision Table

| Situation | Use | Not |
|-----------|-----|-----|
| staging vs production | separate folders + separate backends + separate credentials | `terraform workspace` |
| engineer testing a refactor against already-deployed infra | `terraform workspace new` | a new permanent folder |
| network topology vs daily-deploying service | separate component folders and state files | one state file per environment |
| any state containing DB credentials, keys, or certs | encrypted remote backend with a tight access policy | local state, VCS-committed state, or shared-backend workspaces |
| environment-specific instance sizes | input variables per environment folder | `terraform.workspace` ternaries |

## Review Checklist

- [ ] No `terraform workspace` usage separating environments (grep for `terraform.workspace` and for workspace commands in CI)
- [ ] One folder per environment; environment name is visible in the path
- [ ] One backend per environment, in a separate account or project where possible
- [ ] Distinct credentials/roles per environment — the staging pipeline cannot authenticate to the production backend
- [ ] Components split by rate of change within each environment (network / data / services)
- [ ] Backend encrypts in transit and at rest
- [ ] Backend access policy is as tight as the policy on the secrets the state contains
- [ ] Backend supports locking; CI sets a lock timeout
- [ ] Backend `key` mirrors the folder path 1:1
- [ ] No state files in version control

## Sources

- Brikman, Yevgeniy. *Terraform: Up & Running*, 3rd edition (O'Reilly, 2022), Ch3 "How to Manage Terraform State" — bulkheads, isolation via workspaces vs file layout, component-level splitting, directory conventions, remote backend rationale.
- Brikman, Ch6 "Managing Secrets with Terraform" — plaintext state and plan files, backend encryption and access-control requirements.

## Related

- [stack-sizing-patterns.md](stack-sizing-patterns.md) — Morris's stack-sizing taxonomy and blast radius, the same split argument from the stack side
- [infrastructure-testing-strategy.md](infrastructure-testing-strategy.md) — testing the code that manages this state
- [../assets/terraform-iac/template-env-promotion.md](../assets/terraform-iac/template-env-promotion.md) — promotion workflow built on per-environment state isolation
- [gitops-workflows.md](gitops-workflows.md) — drift detection and continuous reconciliation
