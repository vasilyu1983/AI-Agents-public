# SvelteKit with runes: post-scaffold checklist

Use the [official scaffold documentation](https://svelte.dev/docs/kit/creating-a-project) for the installed toolchain. This checklist records application-specific decisions after generation; it does not replace CLI output.

## Before adding application code

- [ ] Use the official scaffold in a new directory, or preserve an existing app's structure.
- [ ] Read the CLI's supported runtime and package-manager requirements; commit its lockfile.
- [ ] Keep generated compiler, bundler, and test configuration unless a concrete requirement changes it.
- [ ] Confirm every extra dependency's peer range against the installed framework.
- [ ] Add only the router, data layer, or component library the feature actually needs.
- [ ] Keep secrets in server-only configuration; public build variables are readable by users.
- [ ] Define deployment output and the supported rendering model before integrating server code.

## Post-scaffold checks

- [ ] Use the official Svelte CLI and preserve its generated TypeScript/Svelte configuration.
- [ ] Use state for mutable component data, derived for derivation, and effect for external synchronization.
- [ ] Keep per-user server state request-scoped; do not put it in a shared module singleton.
- [ ] Choose server loads for privileged data and universal loads only for browser-safe dependencies.
- [ ] Use server form actions by default and progressive enhancement when required.
- [ ] Validate and authorize action inputs; return expected errors in the framework form contract.
- [ ] Evaluate remote functions only after checking their experimental status and required compiler/kit opt-ins.
- [ ] Keep remote files outside lib/server and keep secrets in server-only imports.
- [ ] Select the adapter for the deployment host before introducing runtime-dependent APIs.
- [ ] Enable prerendering only where all required data and routes can be resolved at build time.
- [ ] Keep browser-only effects out of server render and verify initial markup matches hydration.
- [ ] Confirm asset/image processing works in the production adapter output.
- [ ] Test action pending/error states and restoration of user input.

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

- Framework implementation: [../../references/svelte-sveltekit-patterns.md](../../references/svelte-sveltekit-patterns.md).
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
