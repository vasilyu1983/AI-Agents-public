# BDD Testing Template: Cucumber & Gherkin

Gherkin earns its cost only when non-engineers read or write the scenarios. If nobody outside engineering reviews the feature files, write the same checks as plain tests with Given/When/Then names; the step-definition layer is otherwise pure maintenance overhead.

## When to Use

- Use for acceptance criteria that product, compliance or support stakeholders sign off, and for a thin set of critical journeys.
- Do not use for unit tests, implementation details, or exhaustive input combinations (use parameterised or property-based tests).

## Rules

- Declarative, not imperative: describe what the user achieves, not which fields they click.
- Each scenario is independent and sets up its own state; use `Background` only for truly shared preconditions.
- One behaviour per scenario; split a scenario that needs several `When` steps.
- Keep step definitions thin: they call the same drivers and fixtures as the rest of the suite, so there is one automation layer, not two.
- Tag scenarios by gate (`@smoke`, `@deploy-gate`) so the same files feed the E2E scopes in [../../SKILL.md](../../SKILL.md#e2e-gate-topology-default).
- Treat an undefined or pending step as a failure in CI (for Cucumber.js, run with `--strict`, which is the default in recent versions; verify for your runner).

## Example

```gherkin
Feature: Account recovery

  Scenario: User resets a forgotten password
    Given a registered user "user@example.com"
    When they request a password reset and follow the emailed link
    And they choose a new password
    Then they can sign in with the new password
    And the old password no longer works
```

```gherkin
# Imperative anti-pattern: couples the spec to the UI and breaks on every layout change
When I click "#forgot-link"
And I type "user@example.com" into "input[name=email]"
And I click the button "Send"
```

## Related Resources

- [../../references/shift-left-testing.md](../../references/shift-left-testing.md) — acceptance criteria in the stage model
- [../template-test-case-design.md](../template-test-case-design.md) — Given/When/Then and oracles
