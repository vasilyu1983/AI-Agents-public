# Infrastructure Testing Strategy

*Purpose: Choose which infrastructure tests to run at which stage, knowing what each stage cannot catch.*

*Use when:* Designing a test suite for Terraform/OpenTofu or other IaC, deciding how much testing is enough, or diagnosing why a green pipeline still shipped broken infrastructure.

This file merges two sources that answer different halves of the question. **Brikman** (*Terraform: Up & Running* 3e, Ch9) answers *what each rung of testing can and cannot catch* for Terraform specifically. **Morris** (*Infrastructure as Code* 2e, Ch8) answers *how many tests belong at each level* and why the application-testing pyramid does not transfer to declarative infrastructure. Each idea below is attributed to its book.

## Table of Contents

- [The Two Framings](#the-two-framings)
- [Morris: Why Low-Level Declarative Tests Have Low Value](#morris-why-low-level-declarative-tests-have-low-value)
- [Morris: Progressive Testing](#morris-progressive-testing)
- [Morris: Pyramid vs Infrastructure Test Diamond](#morris-pyramid-vs-infrastructure-test-diamond)
- [Morris: The Swiss Cheese Model](#morris-the-swiss-cheese-model)
- [Brikman: The Rungs and Their Blind Spots](#brikman-the-rungs-and-their-blind-spots)
- [Brikman: End-to-End and the Persistent-Environment Problem](#brikman-end-to-end-and-the-persistent-environment-problem)
- [Putting Them Together](#putting-them-together)
- [Review Checklist](#review-checklist)
- [Sources](#sources)

---

## The Two Framings

| Question | Answered by | Short answer |
|----------|-------------|--------------|
| What can this test *not* catch? | Brikman, Ch9 | Each rung has a specific, nameable blind spot |
| How many tests at each level? | Morris, Ch8 | Fewer at the bottom than the pyramid suggests — a diamond |
| Where should a given risk be caught? | Morris, Ch8 (Swiss cheese) | Earliest layer where it is feasible, but somewhere is what matters |

They agree on the underlying principle. Morris: "The guiding principle for a progressive feedback strategy is to get fast, accurate feedback … running faster tests with a narrower scope and fewer dependencies first and then running tests that progressively add more components and integration points." Brikman's rungs are ordered by exactly that gradient.

## Morris: Why Low-Level Declarative Tests Have Low Value

This is the argument that reshapes the whole strategy, so take it first.

Declarative code declares desired state. A test of it "would simply restate the code" — assert the subnet exists, assert its address range is the value the code just set. Morris: **"A suite of low-level tests of declarative code can become a bookkeeping exercise. Every time you change the infrastructure code, you change the test to match."**

He then asks what risks such a test actually uncovers, and answers with three:

- "The infrastructure code was never applied."
- "The infrastructure code was applied, but the tool failed to apply it correctly, without returning an error."
- "Someone changed the infrastructure code but forgot to change the test to match."

And dismantles the first two. The first "may be a real one, but it doesn't require a test for every single declaration" — one test per unit of applied code suffices to reveal that it was not applied. The second "boils down to protecting yourself against a bug in the tool you're using. The tool developers should fix that bug or your team should switch to a more reliable tool."

The third risk is not a risk the test mitigates; it is a cost the test imposes.

**Consequence for practice:** do not measure infrastructure test coverage by counting assertions against resource attributes. A high count there is a maintenance liability, not evidence of safety.

## Morris: Progressive Testing

"Progressive testing involves running test suites in a sequence. The sequence builds up, starting with simpler tests that run more quickly over a smaller scope of code, then building up to more comprehensive tests over a broader set of integrated components and services."

The reason to order it this way is diagnostic cost: "When a broadly scoped test fails, you have a large surface area of components and dependencies to investigate. So you should try to find any potential area at the earliest point, with the smallest scope that you can."

A second rule keeps the suite affordable: **avoid duplicating tests at different levels.** Morris's example — if an earlier stage explicitly tests server configuration and checks that log-folder permissions are correct, "You should not have a test that checks file permissions in the stage that tests the full infrastructure stack provisioned in the cloud."

## Morris: Pyramid vs Infrastructure Test Diamond

The classic test pyramid says "you should have more tests at the lower layers, which are the earlier stages in your progression, and fewer tests in the later stages." It was "devised for application software development" — many fast unit tests at the base, integration tests in the middle, journey tests at the top.

Morris's finding: **"The testing pyramid is less valuable with declarative infrastructure codebases."** Three reasons, all his:

- "Most low-level declarative stack code … written for tools like Terraform and CloudFormation is too large for unit testing, and depends on the infrastructure platform."
- Declarative modules "are difficult to test in a useful way," both because of the low value of testing declarative code (above) and "because there is usually not much that can be usefully tested without the infrastructure."
- Therefore: "although you'll almost certainly have low-level infrastructure tests, there may not be as many as the pyramid model suggests."

The resulting shape: **"an infrastructure test suite for declarative infrastructure may end up looking more like a diamond"** — thin at the bottom, widest in the middle where components are integrated against a real platform, narrowing again at the top.

Important scope limit, stated by Morris: "The pyramid may be more relevant with an infrastructure codebase that makes heavier use of dynamic libraries written in imperative languages. These codebases have more small components that produce variable results, so there is more to test." So a Pulumi/CDK codebase with real branching logic pulls back toward a pyramid; HCL does not.

## Morris: The Swiss Cheese Model

An alternative to shape-fitting. "The idea is that a given layer of testing may have holes, like one slice of Swiss cheese, that can miss a defect or risk. But when you combine multiple layers, it looks more like a block of Swiss cheese, where no hole goes all the way through."

The practical instruction: "you focus on where to catch any given risk. You still want to catch issues in the earliest layer where it is feasible to do so, but the important thing is that it is tested somewhere in the overall model."

Morris's summary is the one worth remembering: **"The key takeaway is to test based on risk rather than based on fitting a formula."**

This is the model that makes Brikman's blind-spot analysis actionable — each rung's blind spot is a hole, and the layering question is which later rung covers it.

## Brikman: The Rungs and Their Blind Spots

Brikman orders Terraform testing by how much of the code actually executes. Each rung buys coverage with speed, stability, and credentials.

### Rung 1 — Static analysis

Reads the code without executing it. `terraform validate` is built in and "can catch syntax issues"; Brikman is explicit that "validate is limited solely to syntactic checks." Policy tools (tfsec, tflint, and policy-as-code engines) go further, enforcing rules such as blocking inbound security-group rules from `0.0.0.0/0`, or requiring a tagging convention.

*Strengths (Brikman):* fast, easy, stable — "no flaky tests" — no authentication to a real provider, no resources deployed or destroyed.

**Blind spot — it cannot see dynamic values.** In his words, static analysis can "only catch errors that can be determined from statically reading the code, without executing it." The illustration is precise: "you can detect a policy violation for static values, such as a security group hardcoded to allow inbound access from CIDR block `0.0.0.0/0`, but you can't detect policy violations from dynamic values, such as the same security group but with the inbound CIDR block being read in from a variable or file."

And the general caveat he repeats at every non-apply rung: "These tests aren't checking functionality, so it's possible for all the checks to pass and the infrastructure still doesn't work!"

### Rung 2 — Plan testing

Run `terraform plan` and analyze the output. Brikman positions it exactly: "Since you're executing the code, this is more than static analysis, but it's less than a unit or integration test, as you're not executing the code fully."

**Blind spot — plan executes reads but not writes.** Verbatim: "plan executes the read steps (e.g., fetching state, executing data sources) but not the write steps (e.g., creating or modifying resources)."

That boundary is what makes plan testing resolve the dynamic values static analysis could not — the variable has been read, the data source has returned — while still telling you nothing about whether the resource can actually be created.

*Trade-offs (Brikman, relative to the neighbouring rungs):* "not quite as fast as pure static analysis but much faster than unit or integration tests"; "not quite as easy … but much easier"; "not quite as stable … but much more stable." The new cost: **"You have to authenticate to a real provider (e.g., to a real AWS account). This is required for plan to work."** Same functional caveat: all checks can pass and the infrastructure still not work.

> Plan files written with `-out` contain secrets in plain text (Brikman Ch6). If plan testing runs in CI, do not publish the plan file as an artifact — see [../assets/terraform-iac/template-iac-terraform.md](../assets/terraform-iac/template-iac-terraform.md) §7.1.

### Rung 3 — Unit / apply testing

Deploy real infrastructure into a real account, validate it, then tear it down. Brikman's unit of testing for Terraform is not a function but a module — deploy the module, assert against the running resource, `terraform destroy`.

Server-testing tools (InSpec and similar) sit here, offering DSLs that "make it easy to validate specific properties of servers," and are well suited to "validate a checklist of requirements, especially around compliance (e.g., PCI compliance, HIPAA compliance, etc.)."

**What it buys:** "Since you actually have to run apply and you validate a real, running server, these types of tests catch far more types of errors than pure static analysis or plan testing."

**Blind spots — cost, flakiness, and scope.** Brikman: "They are not as fast. These tests only work on servers that are deployed, so you have to run the full apply (and perhaps destroy) cycle, which can take a long time." And: "They are not as stable (some flaky tests). Since you have to run apply and wait for real servers to deploy, you will hit various intermittent issues and occasionally have flaky tests." Real provider credentials are mandatory.

The scope blind spot is the one Brikman names generally: "just because individual units work correctly in isolation doesn't mean that they will work correctly when combined." Integration tests — several modules deployed together — cover that; they inherit this rung's speed and flakiness costs and add to them.

### Rung 4 — End-to-end

"End-to-end tests involve running your entire architecture — for example, your apps, your data stores, your load balancers — and validating that your system works as a whole." They "typically use real systems everywhere, without any mocks, in an architecture that mirrors production (albeit with fewer/smaller servers to save money)."

The purpose, in his framing: "just because different parts of your system work correctly doesn't mean they will work correctly when deployed in the real world."

## Brikman: End-to-End and the Persistent-Environment Problem

E2E's blind spot is not what it fails to catch but what it costs to run. Deploying an entire architecture from scratch for every test run is slow enough to stop being run.

Brikman's answer is to stop deploying from scratch. Keep a **persistent test environment** — one that stays up between runs — and have each test run deploy only the change incrementally on top of it, validating the result. This mirrors what production actually experiences: production is never built from nothing either, it is a long-lived environment receiving incremental changes. A from-scratch E2E test is therefore not only slower, it is testing a path production never takes.

The trade-off to be honest about: a persistent environment accumulates state and drifts, so it needs the same drift detection and periodic rebuild discipline as any other long-lived environment — see [gitops-workflows.md](gitops-workflows.md) and [terraform-state-architecture.md](terraform-state-architecture.md).

## Putting Them Together

Read down the blind-spot column and up the coverage column; the Swiss-cheese question is whether every hole is covered by some later slice.

| Rung | Executes | Needs cloud creds | Deploys resources | Blind spot |
|------|----------|-------------------|-------------------|------------|
| Static analysis | nothing | no | no | dynamic values; functionality entirely |
| Plan testing | reads only | yes | no | write steps; functionality entirely |
| Unit / apply | reads + writes, one module | yes | yes | cross-module integration; slow, sometimes flaky |
| Integration | reads + writes, several modules | yes | yes | whole-system behavior; slower still |
| End-to-end | whole architecture | yes | yes | cost/duration — needs a persistent environment and incremental strategy |

Practical sequencing, combining both books:

1. **Run every rung, but not in proportion to the pyramid.** Morris's diamond means the bulk of the value sits in the middle — modules applied against a real platform — not in a large base of attribute assertions.
2. **Do not count low-level declarative assertions as coverage.** Morris's bookkeeping argument. One test that the code was applied does the job those assertions were pretending to do.
3. **Assign each risk to exactly one rung** — the earliest where catching it is feasible — and do not re-test it later (Morris's no-duplication rule).
4. **Never treat a green static-analysis or plan stage as functional assurance.** Brikman says twice, at two different rungs, that all checks can pass and the infrastructure still not work. If nothing in the pipeline runs `apply`, nothing in the pipeline has tested that the infrastructure works.
5. **Budget for flakiness above the plan rung.** It is inherent to waiting on real cloud resources, not a sign of a badly written test. Retries and generous timeouts are expected, not a smell.
6. **Make E2E incremental against a persistent environment**, so it stays cheap enough to keep running and models production's actual change path.

Brikman's own advice on where to start, for a team with nothing: begin with static analysis and build up from there rather than attempting full coverage at once.

## Review Checklist

- [ ] Suite shape reviewed against the diamond, not the pyramid (unless the codebase is imperative/dynamic, where the pyramid applies)
- [ ] No large body of assertions that merely restate declarative attribute values
- [ ] Each risk assigned to one rung; no duplicate coverage across stages
- [ ] Static analysis includes policy checks, not just `terraform validate` syntax checking
- [ ] Someone can state what the static and plan stages do *not* prove
- [ ] At least one stage actually runs `apply` against a real provider before production
- [ ] Plan files in CI are not published as unencrypted artifacts
- [ ] E2E runs incrementally against a persistent environment, not from scratch
- [ ] The persistent test environment has drift detection and a rebuild cadence
- [ ] Flaky-test budget and retry policy exist for apply-level tests

## Sources

- Brikman, Yevgeniy. *Terraform: Up & Running*, 3rd edition (O'Reilly, 2022), Ch9 "How to Test Terraform Code" — manual vs automated testing, unit/integration/end-to-end definitions, static analysis and plan testing strengths and weaknesses, server testing tools, persistent-environment strategy for end-to-end tests. *Tool comparison tables in that chapter are dated to statistics the author gathered from GitHub in February 2022 and are deliberately not reproduced here.*
- Morris, Kief. *Infrastructure as Code*, 2nd edition (O'Reilly, 2020), Ch8 "Core Practice: Continuously Test and Deliver", pp. 110, 115–119 — "Challenge: Tests for Declarative Code Often Have Low Value", "Progressive Testing", "Test Pyramid", the infrastructure test diamond, and "Swiss Cheese Testing Model".

## Related

- [terraform-state-architecture.md](terraform-state-architecture.md) — state and component boundaries, which set the scope each test runs against
- [stack-sizing-patterns.md](stack-sizing-patterns.md) — stack size determines how much a single apply-level test has to stand up
- [gitops-workflows.md](gitops-workflows.md) — drift detection for persistent environments
- [../assets/terraform-iac/template-iac-terraform.md](../assets/terraform-iac/template-iac-terraform.md) — CI workflow and testing sections
