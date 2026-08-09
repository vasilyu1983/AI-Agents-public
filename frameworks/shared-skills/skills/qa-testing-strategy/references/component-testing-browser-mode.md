# Component Testing in Browser Mode

Use this reference when UI logic is too rich for pure unit tests but full E2E would be too slow or expensive.

## Why this layer exists

- Runs components in a real browser, not a DOM shim
- Catches rendering, focus, accessibility, and interaction issues earlier than E2E
- Keeps scope narrow, so failures stay cheaper to diagnose than full end-to-end tests

## Default recommendation

- JS/TS web apps: prefer Vitest Browser Mode for component tests
- Keep component tests below E2E in the strategy stack
- Use them for state transitions, validation messages, loading states, keyboard navigation, and a11y smoke

## What belongs here

- Form validation and error rendering
- Loading, empty, and error states
- Keyboard and focus behavior
- Design-system components with meaningful interaction
- Visual and accessibility smoke on stable components

## What does not belong here

- Pure business rules with no rendering risk
- Full cross-page workflows
- Third-party integration semantics better covered by contract or integration tests

## Decision rules

```text
Need confidence in a UI behavior?
    │
    ├─ No browser semantics involved
    │   └─ Unit test
    │
    ├─ Single component or narrow UI composition
    │   └─ Browser-mode component test
    │
    └─ Multi-page user journey or auth/payment flow
        └─ E2E test
```

## Good assertions

- User-visible text and error states
- ARIA roles, names, and focus order
- Screenshot diffs for stable components only
- Network or callback outcomes that are observable from the component boundary

## Avoid

- Recreating a full app flow inside component tests
- Heavy mocking that hides broken contracts
- Snapshot-only assertions with no behavioral checks
