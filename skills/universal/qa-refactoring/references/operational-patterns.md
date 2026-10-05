# Operational Patterns and Standards

## Contents

- [Pattern: Reuse-Before-Write Ladder](#pattern-reuse-before-write-ladder)

This file previously restated refactoring-catalog.md, code-smells-guide.md,
tech-debt-management.md, a fabricated set of ESLint/SonarQube quality-gate
config, and generic AI-tooling marketing copy. That material duplicated
sibling reference files (and, for the config block, contained fabricated
properties — see [references/mutation-testing.md](mutation-testing.md) and
the quality-gate guidance in [../assets/quality-gates/platform-agnostic/sonarqube-setup.md](../assets/quality-gates/platform-agnostic/sonarqube-setup.md)
and [../assets/quality-gates/javascript/eslint-config.js](../assets/quality-gates/javascript/eslint-config.js)
for the corrected versions). It was removed 2026-09-23 during a maturity
audit; only the Reuse-Before-Write Ladder below was unique expert content.

For refactoring catalogs, quality gates, and legacy modernization, use:

- [references/refactoring-catalog.md](refactoring-catalog.md)
- [references/code-smells-guide.md](code-smells-guide.md)
- [references/tech-debt-management.md](tech-debt-management.md)
- [references/legacy-code-strategies.md](legacy-code-strategies.md)
- [references/automated-refactoring-tools.md](automated-refactoring-tools.md)

## Pattern: Reuse-Before-Write Ladder

**Use when:** Before writing any new code — refactor target, helper function, or new abstraction — run this ordered checklist first. Stop at the first rung that holds; only fall through to the next rung if it doesn't.

1. **Does this need to exist at all?** If the need is speculative (no concrete caller today), skip it — do not build for a hypothetical future requirement.
2. **Does the codebase already have this?** Search for an existing implementation (function, class, module) before writing a new one. A duplicate you didn't find is worse than a slower search.
3. **Does the standard library cover it?** Prefer the language/runtime standard library over a hand-rolled equivalent.
4. **Does a native platform feature cover it?** Framework or platform primitives (built-in caching, built-in validation, built-in retry) usually outrank custom code in reliability and maintenance cost.
5. **Does an already-installed dependency cover it?** Check `package.json`/`requirements.txt`/equivalent for a library already in the tree before adding new surface area or a new dependency.
6. **Can it be one line?** If the minimal correct implementation is a one-liner, write the one-liner, not a wrapper class around it.
7. **Only then, write the minimum.** Write the smallest change that satisfies the requirement — no unrequested abstraction, no speculative extensibility.

This ladder operationalizes this skill's existing simplicity bias (see [Do / Avoid](../SKILL.md#do--avoid) in the main skill file and the general "boring over clever" framing throughout this skill) as a literal, ordered sequence of lookups rather than a general preference — closer to a runbook an agent can execute step-by-step than a principle to keep in mind. It is most useful during the "smallest safe step" phase of the Safe Refactor Loop, before introducing a new helper, utility, or abstraction as part of a refactor.

Attribution: ladder structure adapted from the core ruleset in [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), commit `2ed6c52c`, MIT license (2026-08-09).
