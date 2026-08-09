# Coding Agent Regression Testing

Use this reference when an agent edits code and you care about preventing regressions, not just maximizing task completion.

## Table Of Contents

- [Why Coding Agents Need A Different Regression Pattern](#why-coding-agents-need-a-different-regression-pattern)
- [TDAD Pattern](#tdad-pattern)
- [Practical Protocol](#practical-protocol)
- [Relationship To Classic TDD](#relationship-to-classic-tdd)
- [Adjacent Methods](#adjacent-methods)
- [Adoption Rule](#adoption-rule)
- [Related References](#related-references)
- [Primary Sources](#primary-sources)

## Why Coding Agents Need A Different Regression Pattern

Coding agents fail in a specific way: they often appear successful because they complete the requested change, while silently breaking nearby behavior that existing tests did not surface in time.

This means evaluation needs at least two metrics:

- **task completion**
- **regression rate** for behavior that worked before the patch

## TDAD Pattern

TDAD (Test-Driven Agentic Development) is a research pattern for coding agents. The key idea is simple: give the agent **targeted test context** by mapping changed source files to the tests most likely to cover them.

Paper benchmark results:

| Approach | Regression Rate | What Changed |
|---|---:|---|
| No testing guidance | 6.08% | Agent decides testing on its own |
| Procedural TDD prompts only | 9.94% | "Write tests first" style prompting without impact context |
| TDAD targeted test map | 1.82% | Agent receives source-to-test dependency context |

Treat these as benchmark numbers from one paper, not universal thresholds. The useful takeaway is directional: **targeted impact context beat generic procedural TDD prompting** for coding agents.

Primary source: <https://arxiv.org/abs/2603.17973>

## Practical Protocol

### 1. Build the best available source-to-test map

Possible inputs:

- static dependency graph
- coverage data from prior runs
- ownership metadata
- import graph heuristics
- changed-path test selection rules
- repo-maintained test tags

Approximate mappings are still useful if they are better than "run whatever looks related."

### 2. Hand the agent the map with the task

Minimal task bundle:

- changed files
- likely affected tests
- verification commands
- stop conditions if those tests fail

### 3. Require test evidence before completion

The completion record should state:

- which tests were selected
- which commands ran
- whether the agent iterated after failures
- whether regression risk remains unverified

### 4. Track regression rate separately

Do not hide regression behavior inside one blended score. Log it as its own suite metric.

## Relationship To Classic TDD

This pattern is **not** anti-TDD.

Use classic TDD when:

- the work starts naturally from a failing test
- the target behavior is well-bounded
- the developer or agent can express the acceptance condition cleanly as a new test

Use TDAD-style targeted test context when:

- the agent is modifying an existing codebase
- existing tests already cover nearby behavior
- the main risk is breaking something adjacent to the requested change

In practice, the two can coexist:

- classic TDD for the new behavior
- targeted regression checks for the changed neighborhood

## Adjacent Methods

- **SpecOps** is relevant when the agent operates GUIs or real-world environments rather than source code patches. It is a test framework, not a coding workflow replacement.
- **Classic regression suites** remain necessary for smoke, security, refusal, and policy checks outside code behavior.

## Adoption Rule

Adopt the smallest version of this pattern that your repo can support:

- if you have coverage or dependency data, use it
- if you only have changed-path rules and tagged tests, start there
- if you have neither, create a lightweight maintained map for high-risk areas first

Do not wait for a perfect graph before adding targeted test context.

## Related References

- [`regression-protocol.md`](regression-protocol.md)
- [`test-case-design.md`](test-case-design.md)
- [`../../ai-agents/references/code-swe-agents.md`](../../ai-agents/references/code-swe-agents.md)

## Primary Sources

- TDAD (Test-Driven Agentic Development): <https://arxiv.org/abs/2603.17973>
- SpecOps: <https://arxiv.org/abs/2603.10268>
