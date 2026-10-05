# Angular standalone application: post-scaffold checklist

Use the [official scaffold documentation](https://angular.dev/tools/cli/setup-local) for the installed toolchain. This checklist records application-specific decisions after generation; it does not replace CLI output.

## Before adding application code

- [ ] Use the official scaffold in a new directory, or preserve an existing app's structure.
- [ ] Read the CLI's supported runtime and package-manager requirements; commit its lockfile.
- [ ] Keep generated compiler, bundler, and test configuration unless a concrete requirement changes it.
- [ ] Confirm every extra dependency's peer range against the installed framework.
- [ ] Add only the router, data layer, or component library the feature actually needs.
- [ ] Keep secrets in server-only configuration; public build variables are readable by users.
- [ ] Define deployment output and the supported rendering model before integrating server code.

## Post-scaffold checks

- [ ] Use the installed Angular CLI scaffold; keep its generated TypeScript and test configuration.
- [ ] Confirm standalone component imports explicitly rather than adding an unnecessary NgModule.
- [ ] Preserve the generated change-detection setup and verify third-party compatibility.
- [ ] Use signals for local derived state; keep computed derivations free of side effects.
- [ ] Choose typed Reactive Forms for an existing reactive-form codebase; evaluate Signal Forms against its API status.
- [ ] Import FormField when binding a Signal Forms field and expose field errors accessibly.
- [ ] Use httpResource for reactive reads and HttpClient for mutations; render loading and error states.
- [ ] Keep guards as navigation UX; the server must authorize every protected operation.
- [ ] Lazy-load route components with stable routing and chunk-error recovery.
- [ ] Use a stable identity expression with the modern for control-flow block.
- [ ] Check SSR browser-API access, hydration, and transfer-cache handling of private data.
- [ ] Review the generated production budget against a measured baseline rather than a copied threshold.
- [ ] Exercise the configured test runner instead of mixing Jasmine and Vitest conventions.

## Proof before handoff

- [ ] Run the generated lint, type-check, unit-test, and production-build commands that exist in package scripts.
- [ ] Serve the production output through the intended adapter or host; a dev server is insufficient proof.
- [ ] Open the initial URL directly, then navigate, refresh, and use browser back/forward.
- [ ] Exercise loading, empty, error, success, and expired-session states where applicable.
- [ ] Confirm keyboard focus, semantic controls, labels, and dialog behavior in the rendered app.
- [ ] Inspect browser and server logs for hydration errors and unexpected requests.
- [ ] Confirm the build has no secrets or server-only imports in client chunks.
- [ ] Record the commands run, output checked, and any deployment behavior left unverified.

## Load only for the next implementation step

- Framework implementation: [../../references/angular-patterns.md](../../references/angular-patterns.md).
- Component and unit proof: [../../references/testing-frontend-patterns.md](../../references/testing-frontend-patterns.md).
- Framework performance changes: [../../references/performance-optimization.md](../../references/performance-optimization.md).
- Accessibility remediation: [../../../software-accessibility/SKILL.md](../../../software-accessibility/SKILL.md).
- Browser journeys: [../../../qa-testing-playwright/SKILL.md](../../../qa-testing-playwright/SKILL.md).

## Record the scaffold outcome

- CLI/version used: read from command output and lockfile.
- Rendering mode and deployment adapter: record the selected combination.
- Extra dependencies: list the feature that requires each.
- Deviations from generated configuration: explain each change.
- Remaining proof: name any host or browser behavior not exercised.
