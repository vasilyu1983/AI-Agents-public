# Fitness Functions and Automated Architectural Governance

How to turn architecture principles into executable checks. Source material: Neal Ford, Rebecca Parsons, Patrick Kua, and Pramod Sadalage, *Building Evolutionary Architectures*, 2nd ed. (O'Reilly, 2022) — Chapter 2 ("Fitness Functions") and Chapter 4 ("Automating Architectural Governance").

## Table of Contents

- [What a Fitness Function Is](#what-a-fitness-function-is)
- [The Six Classification Axes](#the-six-classification-axes)
- [Litmus Tests: Not Every Test Is a Fitness Function](#litmus-tests-not-every-test-is-a-fitness-function)
- [Tooling: Dependency Rules and Linters](#tooling-dependency-rules-and-linters)
- [Herding: Cascading Thresholds That Tighten Over Time](#herding-cascading-thresholds-that-tighten-over-time)
- [Code Metrics Worth Governing](#code-metrics-worth-governing)
- [Codebases Changed by Coding Agents](#codebases-changed-by-coding-agents)
- [Applying This](#applying-this)

## What a Fitness Function Is

An architectural fitness function is an **objective measure** of some architecture characteristic. The authors are explicit that "function" does not mean "must be code":

> "Don't mistake the function part of our definition as implying that architects must express all fitness functions in code. … as with acceptance criteria in agile software development, the fitness functions for evolutionary architecture may not be implementable in software (e.g., a required manual process for regulatory reasons). An architectural fitness function is an objective measure, but architects may implement that measure in a wide variety of ways."

The value is unification. Code quality checks, DevOps metrics, security scans, and performance tests were historically treated as separate mechanisms; fitness functions name them as one category so an architect can reason about coverage of architectural concerns in a single frame.

## The Six Classification Axes

The book classifies fitness functions across "scope, cadence, result, invocation, proactivity, and coverage."

| Axis | Values | Distinction |
|---|---|---|
| **Scope** | Atomic vs. holistic | Atomic runs against a singular context and exercises one aspect (a unit test checking for package cycles). Holistic runs against a shared context and exercises a combination — designed "to ensure that combined features that work atomically don't break in real-world combinations." |
| **Cadence** | Triggered vs. continual vs. temporal | Triggered runs on an event (a pipeline stage, a developer running a test). Continual executes "constant verification," often via synthetic transactions in production. Temporal builds a time component into fitness — an encryption-library review reminder, or a *break upon upgrade* test that forces re-evaluation of a back-ported feature when the real upgrade lands. |
| **Result** | Static vs. dynamic | Static has a fixed result: binary pass/fail, a number range, set inclusion. Dynamic relies on "a shifting definition based on extra context" — e.g. allowing responsiveness to degrade as concurrent users rise, but not past a defined point. Note the authors' caveat: "dynamic and objective do not conflict — fitness functions must evaluate to an objective outcome, but that evaluation may be based on dynamic information." |
| **Invocation** | Automated vs. manual | Most run in CI/CD. Some resist automation — legal requirements, exploratory testing, or a team whose QA is still manual. Those become manual fitness functions "verified by a person-based process" and run as manual stages in the deployment pipeline. |
| **Proactivity** | Intentional vs. emergent | Intentional functions are written at project inception as part of formal governance. Emergent ones appear when an architect notices misbehavior worth governing. The two form a spectrum, and fitness functions live in the codebase and change as requirements do. |
| **Coverage** | Domain-specific? | The authors answer mostly no — see the litmus test below. |

### Holistic Is Where the Interesting Failures Live

The book's worked example: security and scalability each have atomic fitness functions. Caching makes the scalability function pass. With caching off, the security function (checking data staleness) passes. Run together, "enabling caching makes data too stale to pass the security fitness function, and the holistic test fails." You cannot test every combination, so holistic functions are selected deliberately — and the difficulty of building one is itself information about how much the characteristic is worth.

### Triggered vs. Continual Is a Trade-off, Not a Ranking

For a rule like "non-orchestrator services must not talk to each other," the book gives both implementations. Continual (services broadcast collaboration messages; a monitor or queue consumer validates them) gives immediate reaction but "adds runtime overhead … this level of observability may have a negative impact on performance, scalability, and so on." Triggered (a pipeline stage harvests logfiles on a cadence) has no runtime impact, but "teams shouldn't use a triggered version for critical governance issues such as security where the time lag may have negative impacts."

## Litmus Tests: Not Every Test Is a Fitness Function

**Test 1 — architectural, not domain.** The book states it flatly:

> "Not all tests are fitness functions, but some tests are — if the test helps verify the integrity of architectural concerns, we consider it a fitness function."

And on the domain boundary:

> "generally fitness functions are used only for abstract architectural principles, not with the problem domain."

Their example: elasticity — a site's ability to handle sudden bursts — can be discussed in purely architectural terms regardless of whether the site is a game, a catalog, or a streaming service, so it is governed by a fitness function. Verifying a change of address "requires domain knowledge and would fall to traditional verification mechanisms." The authors call this out explicitly: "Architects can use this as a litmus test to determine where the verification responsibility lies." The practical reason is anti-duplication: keep fitness functions to pure architecture concerns and let unit/E2E tests own domain logic.

**Test 2 — a metric is not a fitness function until it has a threshold and a consequence.** This is the monitoring-vs-alarm distinction, quoted verbatim:

> "Notice that using a monitoring tool does not imply that you have a fitness function, which must have objective outcomes. Rather, using a monitoring tool in which the architect has created an alarm for deviations outside the objective measure of the metric converts the mere use of monitors into a fitness function."

A dashboard showing p99 latency is monitoring. A defined objective measure plus an alarm on deviation from it is a fitness function. If nobody has said what value is unacceptable and what happens when it is exceeded, you have telemetry, not governance.

## Tooling: Dependency Rules and Linters

**ArchUnit (Java)** — "a testing tool inspired by and using some of the helpers created for JUnit. However, it is designed for testing architecture features rather than general code structure." The book calls it "the most mature of many governance-focused testing frameworks." Representative checks:

```java
// Cycle prevention (Example 2-1)
slices().matching("com.myapp.(*)..").should().beFreeOfCycles()

// Class dependency rules (Example 4-5)
classes().that().haveNameMatching(".*Bar")
    .should().onlyHaveDependentClassesThat().haveSimpleName("Bar")

// Layer governance (Example 4-8)
layeredArchitecture()
    .consideringAllDependencies()
    .layer("Controller").definedBy("..controller..")
    .layer("Service").definedBy("..service..")
    .layer("Persistence").definedBy("..persistence..")
    .whereLayer("Controller").mayNotBeAccessedByAnyLayer()
    .whereLayer("Service").mayOnlyBeAccessedByLayers("Controller")
    .whereLayer("Persistence").mayOnlyBeAccessedByLayers("Service")
```

**NetArchTest (.NET)** — ArchUnit "is obviously applicable only in the Java ecosystem. Fortunately, NetArchTest replicates the same style and basic capabilities of ArchUnit but for the .NET platform."

**Linter-as-fitness-function (everything else)** — for platforms without an ArchUnit equivalent, the book routes to the linter: "most programming languages include a linter, a utility that scans source code to find coding antipatterns and deficiencies." Because linters expose plug-in points for custom syntax rules, developers "can also write rules about what function-calling policies architects want to enforce and other governance rules." Named examples: ESLint (JavaScript/ECMAScript), Cpplint (C++), Staticcheck (Go), sql-lint (SQL). The book's own framing: "While they are not as convenient as ArchUnit, architects can still code many structural checks into virtually any codebase."

### Module-Boundary Enforcement for Modular Monoliths

A modular monolith without an enforced dependency rule decays into a big ball of mud, so the "modular monolith first" default ([modern-patterns.md § Explicit Gates](modern-patterns.md#modular-monolith-vs-microservices-explicit-gates)) needs one of these checks in CI. Check each tool's current maintenance status before adopting it.

| Stack | Tool | What it enforces |
|---|---|---|
| Java / Spring Boot | Spring Modulith (`spring-projects/spring-modulith`), ArchUnit | Application-module boundaries and allowed dependencies, verified in tests |
| .NET | NetArchTest (`BenMorris/NetArchTest`) | ArchUnit-style dependency rules; check maintenance status |
| Ruby / Rails | Packwerk (`Shopify/packwerk`) | Package dependency violations, checked statically |
| Python | import-linter (`seddonym/import-linter`) | Layer and independence contracts between packages |
| TypeScript / JavaScript | dependency-cruiser, eslint-plugin-boundaries, ArchUnitTS | Forbidden import paths, element-type boundaries, architecture tests |

Run the check as a blocking CI step on every change, and herd existing violations down with a recorded baseline (see Herding below) rather than switching the rule on at "error" for a legacy codebase.

### The Governance Principle

The reason to automate at all, quoted verbatim:

> "It's great for architects for express principles, but principles without enforcement are aspirational rather than governance."

The surrounding argument: architects have written these rules "in some wiki or other shared information repository — and they were read by no one!" Unless a fitness function validates a principle, "an architect can never have confidence that developers will follow the principles."

## Herding: Cascading Thresholds That Tighten Over Time

The problem: you set a threshold on an existing codebase where the metric has been ignored for years, and every project fails immediately. The book's answer is not to abandon the gate but to *herd* teams toward it:

> "Rather than set a hard threshold for a fitness function value, you can herd teams toward better values. For example, let's say that you decided as an organization that the absolute upper limit for CC should be 10, yet when you put that fitness function in place most of your projects fail. Instead of abandoning all hope, you can set up a cascading fitness function that issues a warning for anything past some threshold, which eventually escalates into an error over time. This gives teams time to address technical debt in a controlled, gradual way."

The ratchet has two jobs, and the second is the durable one:

> "Gradually narrowing to desired values for a variety of metrics-based fitness functions allows teams to both address existing technical debt and, by leaving the fitness functions in place, prevent future degradation. This is the essence of preventing bit rot via governance."

Practical shape: warn at the current 90th-percentile value, error at the current worst value, and step both down on a schedule. Leaving the function in place after the target is reached is what stops regression.

## Code Metrics Worth Governing

Definitional formulas, stated as the book states them.

**Afferent and efferent coupling** (Yourdon and Constantine, *Structured Design*, 1979): "Afferent coupling measures the number of incoming connections to a code artifact (component, class, function, etc.). Efferent coupling measures the outgoing connections to other code artifacts."

**Abstractness** — "the ratio of abstract artifacts (abstract classes, interfaces, etc.) to concrete artifacts (implementation classes)":

```text
A = Σma / (Σmc + Σma)      ma = abstract elements, mc = concrete elements
```

**Instability** — "the ratio of efferent coupling to the sum of both efferent and afferent coupling":

```text
I = Ce / (Ce + Ca)          Ce = efferent (outgoing), Ca = afferent (incoming)
```

Read it as volatility: "A codebase that exhibits high degrees of instability breaks more easily when changed because of high coupling." A component near 1 is highly unstable; near 0 it "may be either stable or rigid: it is stable if the module or component contains mostly abstract elements and rigid if it is composed of mostly concrete elements." That ambiguity is why I is not read alone.

**Normalized distance from the main sequence** — "one of the few holistic metrics architects have for architectural structure," derived from the other two:

```text
D = |A + I - 1|
```

Components near the idealized line "exhibit a healthy mixture of these two competing concerns." Far into the upper-right is the **zone of uselessness** ("code that is too abstract becomes difficult to use"); far into the lower-left is the **zone of pain** ("code with too much implementation and not enough abstraction becomes brittle and hard to" maintain).

**Cyclomatic complexity (CC)** — McCabe, 1976: "a code-level metric designed to provide an object measure for the complexity of code, at the function/method, class, or application level." Computed via graph theory on decision points:

```text
CC = E - N + 2        single function/method (E = edges/decisions, N = nodes)
CC = E - N + 2P       general form; P = number of connected components (fan-out calls)
```

A function with no decision statements scores 1; one conditional scores 2.

**On thresholds — attribute the number.** The commonly cited industry figure and the authors' own preference are different numbers, and the book says so directly:

> "In general, the industry thresholds for CC suggest that a value under 10 is acceptable, barring other considerations such as complex domains. We consider that threshold very high and would prefer code to fall under 5, indicating cohesive, well-factored code."

So: **CC < 10 is the common industry threshold; CC < 5 is Ford et al.'s stated preference**, not a consensus standard. Do not present 5 as the industry norm. The book also names the metric's central weakness — "the inability to distinguish between essential and accidental complexity." An algorithmically complex problem yields complex functions legitimately; the architect's job is judging "whether functions are complex because of the problem domain or because of poor coding, and alternatively, whether the code is partitioned poorly."

## Codebases Changed by Coding Agents

When a growing share of diffs comes from coding agents, the architecture has to make the safe change the easy one for a reader with a bounded context window. The architectural moves are the ones above, applied deliberately:

- **Module boundaries are context boundaries.** A change that stays inside one module should need only that module's code, its public contract and its instruction file. If an agent must read half the repository to change one feature, the boundary is wrong, for humans too.
- **Enforced dependency rules are the guardrail on generated diffs.** Put the module-boundary check above in blocking CI. An agent will satisfy a failing check; it will not reliably honour a wiki page.
- **Per-module contracts and instructions.** Keep each module's public interface explicit (types, schemas, API specs) and a short local instruction file (such as `AGENTS.md`) next to the code it governs. Route repository context-layer design to [dev-context-engineering](../../dev-context-engineering/SKILL.md).
- **Small batches.** Size agent tasks so each diff stays inside one module and one reviewable change. Cross-module changes go through the contract, as a separate step.
- **Fitness functions over review.** Encode the architecture rules reviewers keep repeating as fitness functions, so agent output is checked on every change, not only when a reviewer notices.

DORA lists "working in small batches", "version control", "platform engineering" and "AI-accessible internal data" among the capabilities that decide whether AI assistance helps delivery ([dora.dev/capabilities](https://dora.dev/capabilities/)). Measuring agent impact belongs to [dev-ai-coding-metrics](../../dev-ai-coding-metrics/SKILL.md).

## Applying This

1. **Start from characteristics, not tools.** List the architecture characteristics that actually matter for this system. Each one that matters gets a fitness function or an explicit note that it is ungoverned.
2. **Classify each one on the six axes.** The axes are a design checklist: scope tells you whether an atomic check is enough; cadence forces the triggered-vs-continual trade-off decision; invocation forces you to admit which checks stay manual.
3. **Apply both litmus tests before writing.** Is this architectural or domain? Does it have a threshold and a consequence, or is it a dashboard?
4. **Prefer the platform's native governance tool.** ArchUnit for Java, NetArchTest for .NET, the linter's plug-in API everywhere else.
5. **Herd, don't slam.** On an existing codebase, warn-then-error on a schedule, and leave the function in place afterward.
6. **Write down which fitness functions are emergent.** They are the record of what governance you learned you needed after the fact, and they are the ones most likely to be missing on the next system.

Related: [modern-patterns.md § Connascence](modern-patterns.md#connascence-a-finer-grained-coupling-vocabulary) for the coupling vocabulary these metrics quantify; [architecture-trends.md](architecture-trends.md) for platform-engineering context around where fitness functions run.
