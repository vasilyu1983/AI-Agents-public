# Stack Sizing Patterns

*Purpose: Decide how much infrastructure belongs in one stack, using blast radius and rate-of-change as the sizing criteria.*

*Use when:* An infrastructure project has grown awkward to change, a team is deciding whether to split a stack, or someone asks "is this a monolith?"

A **stack** in Morris's terms is a collection of infrastructure resources managed as a single unit — the scope one `apply` command acts on. Sizing it is the decision that sets your blast radius.

## Table of Contents

- [Blast Radius: The Two-Part Definition](#blast-radius-the-two-part-definition)
- [The Sizing Taxonomy](#the-sizing-taxonomy)
- [Is My Stack a Monolith?](#is-my-stack-a-monolith)
- [Choosing a Size](#choosing-a-size)
- [Review Checklist](#review-checklist)
- [Sources](#sources)

---

## Blast Radius: The Two-Part Definition

Morris credits the term: **"Charity Majors popularized the term blast radius in the context of Infrastructure as Code. Her post 'Terraform, VPC, and Why You Want a tfstate File Per env' describes the scope of potential damage that a given change could inflict on your system."**

His definition has two parts, and the second is the one teams routinely forget:

> "The immediate blast radius is the scope of code that the command to apply your change includes. For example, when you run `terraform apply`, the direct blast radius includes all of the code in your project. The indirect blast radius includes other elements of the system that depend on the resources in your direct blast radius, and which might be affected by breaking those resources."

Read as a sizing rule:

- **Direct blast radius = the scope of intended change.** It is set entirely by your project boundary, not by the size of your diff. A one-line change to a monolithic stack still has the whole stack in its direct blast radius.
- **Indirect blast radius = the scope of unintended damage.** It is set by dependencies, and it is not visible in the plan output.

Splitting a stack shrinks the direct radius immediately. It shrinks the indirect radius only if the split follows real dependency boundaries — otherwise you have moved the coupling rather than removed it.

## The Sizing Taxonomy

Morris's four patterns, from largest to smallest.

### Antipattern: Monolithic Stack

An infrastructure stack that "includes too many elements, making it difficult to maintain." Morris's discriminator is not a resource count: **"What distinguishes a monolithic stack from other patterns is that the number or relationship of infrastructure elements within the stack is difficult to manage well."**

*Why they happen:* "People build monolithic stacks because the simplest way to add a new element to a system is to add it to the existing project. Each new stack adds more moving parts, which may need to be orchestrated, integrated, and tested. A single stack is simpler to manage." He concedes the honest case — "For a modestly sized collection of infrastructure elements, a monolithic stack might make sense" — but adds "more often, a monolithic stack organically grows out of control."

*When it is appropriate:* "when your system is small and simple. It's not appropriate when your system grows, taking longer to provision and update."

*Consequences:* "Changing a large stack is riskier than changing a smaller stack. More things can go wrong — it has a larger blast radius. The impact of a failed change may be broader since there are more services and applications within the stack. Larger stacks are also slower to provision and change, which makes them harder to manage."

The compounding effect is the real damage: **"As a result of the speed and risk of changing a monolithic stack, people tend to make changes less frequently and take longer to do it. This added friction can lead to higher levels of technical debt."** Note the loop — a big stack makes change risky, risk makes change rare, rarity makes the next change riskier still. This is the same dynamic as automation lag; see [gitops-workflows.md](gitops-workflows.md).

### Pattern: Application Group Stack

"Hosts multiple processes in a single instance of the stack" — the infrastructure for several related services defined together. Morris's example: a product application stack with separate services for browsing products, searching, and managing a basket, whose servers and other infrastructure "are combined in a single stack instance."

*Applicability:* "when a single team owns the infrastructure and deployment of all of the pieces of the application. An application group stack can align the boundaries of the stack to the team's responsibilities." Also useful transitionally — "sometimes useful as an incremental step from a monolithic stack to service stacks."

*Consequences:* "Grouping the infrastructure for multiple applications together also combines the time, risk, and pace of changes. The team needs to manage the risk to the entire stack for every change, even if only one part is changing. **This pattern is inefficient if some parts of the stack change more frequently than others.**"

### Pattern: Service Stack

"Manages the infrastructure for each deployable application component in a separate infrastructure stack."

*Motivation:* "Service stacks align the boundaries of infrastructure to the software that runs on it. This alignment limits the blast radius for a change to one service, which simplifies the process for scheduling changes. Service teams can own the infrastructure that relates to their software."

*Applicability:* "can work well with microservice application architectures" and "help organizations with autonomous teams to ensure each team owns its infrastructure."

*Consequences:* duplication. "If you have multiple applications, each with an infrastructure stack, there could be an unnecessary duplication of code … Duplication can encourage inconsistency, such as using different operating system versions, or different network configurations. You can mitigate this by using modules to share code."

### Pattern: Micro Stack

"Divides the infrastructure for a single service across multiple stacks" — for example "a separate stack project each for the networking, servers, and database."

*Motivation — rate of change and lifecycle:* "Different parts of a service's infrastructure may change at different rates. Or they may have different characteristics that make them easier to manage separately." His example is the server/data split: some server management methods "involve frequently destroying and rebuilding them. However, some services use persistent data in a database or disk volume. Managing the servers and data in separate stacks means they can have different life cycles, with the server stack being rebuilt much more often than the data stack."

*Consequences:* "Although smaller stacks are themselves simpler, having more moving parts adds complexity." Splitting moves work into integration between stacks; it does not eliminate it.

## Is My Stack a Monolith?

Morris is explicit that this is judgment, not measurement: **"Whether your infrastructure stack is a monolith is a matter of judgment."** He lists symptoms:

- "It's difficult to understand how the pieces of the stack fit together (they may be too messy to understand, or perhaps they don't fit well together)."
- "New people take a while learning the stack's codebase."
- "Debugging problems with the stack is hard."
- "Changes to the stack frequently cause problems."
- "You spend too much time maintaining systems and processes whose purpose is to manage the complexity of the stack."

He adds a further indicator: **"A key indicator of whether a stack is becoming monolithic is how many people are working on changes to it at any given time."** The more often multiple people are changing it concurrently, the more monolithic it is behaving — regardless of its size on disk.

**The underlying diagnostic**, drawn from the consequences above: a stack is a monolith when changing one thing forces risk onto unrelated things. That is what makes the application-group pattern "inefficient if some parts of the stack change more frequently than others," and what a monolithic stack does to every change: the direct blast radius is the whole stack no matter how small the diff.

So the question to ask is not "how many resources?" but: *when I change the thing that changes weekly, does the thing that changes yearly sit inside the same apply?* If yes, the yearly thing is absorbing weekly risk for no benefit, and the split boundary is exactly there.

## Choosing a Size

| Signal | Suggests |
|--------|----------|
| Small, simple system; one team; low change rate | monolithic stack is acceptable — do not split preemptively |
| One team owns several related services deployed together | application group stack |
| Parts of the stack change at clearly different rates | split — this is the primary sizing signal |
| Microservice architecture; autonomous service-owning teams | service stack |
| Servers rebuilt often, data persistent | micro stack — split on lifecycle |
| Many people changing one stack concurrently | it is behaving as a monolith; split |
| Split would produce heavy duplication | service stacks + shared modules, not more splitting |
| Split boundaries would not follow dependencies | do not split yet — you would move coupling, not reduce it |

The direction of travel is not one-way. Morris frames the patterns as a spectrum with monolithic and micro at opposite ends, application-group and service in between, and an application group stack as a legitimate stepping stone out of a monolith rather than a destination.

This is the same argument as component-level state splitting in [terraform-state-architecture.md](terraform-state-architecture.md) — Brikman arrives at it from the state side (a VPC that changes monthly should not share a state file with a service that deploys daily), Morris from the stack side. A stack boundary and a state boundary are the same boundary.

## Review Checklist

- [ ] The direct blast radius of a routine change is known and stated (what the apply command covers)
- [ ] The indirect blast radius is documented — what depends on this stack's outputs
- [ ] No stack contains components with clearly different change rates
- [ ] No stack contains both frequently rebuilt servers and persistent data
- [ ] Stack boundaries follow team ownership boundaries
- [ ] Number of people concurrently changing any one stack is low
- [ ] Splits proposed follow real dependency boundaries, not just size
- [ ] Duplication introduced by splitting is mitigated with shared modules
- [ ] Monolithic stacks that are genuinely small and simple are left alone

## Sources

- Morris, Kief. *Infrastructure as Code*, 2nd edition (O'Reilly, 2020), Ch5 "Building Infrastructure Stacks as Code", pp. 56–63 — "Antipattern: Monolithic Stack", the "Blast Radius" sidebar (p. 58), "Is My Stack a Monolith?" sidebar (p. 58), "Pattern: Application Group Stack" (p. 59), "Pattern: Service Stack" (pp. 60–61), "Pattern: Micro Stack" (pp. 62–63).
- Charity Majors, "Terraform, VPC, and Why You Want a tfstate File Per env" — cited by Morris as the origin of blast radius in the IaC context.

## Related

- [terraform-state-architecture.md](terraform-state-architecture.md) — the same boundary decision expressed as state isolation
- [infrastructure-testing-strategy.md](infrastructure-testing-strategy.md) — stack size determines what a single apply-level test must stand up
- [gitops-workflows.md](gitops-workflows.md) — automation lag, the friction loop that large stacks feed
- [../assets/terraform-iac/template-env-promotion.md](../assets/terraform-iac/template-env-promotion.md) — promoting versioned units across environments
