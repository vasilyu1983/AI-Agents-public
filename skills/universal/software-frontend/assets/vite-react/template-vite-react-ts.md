# Vite + React + TypeScript: post-scaffold checklist

Use the [official scaffold documentation](https://vite.dev/guide/) for the installed toolchain. This checklist records application-specific decisions after generation; it does not replace CLI output.

## Before adding application code

- [ ] Use the official scaffold in a new directory, or preserve an existing app's structure.
- [ ] Read the CLI's supported runtime and package-manager requirements; commit its lockfile.
- [ ] Keep generated compiler, bundler, and test configuration unless a concrete requirement changes it.
- [ ] Confirm every extra dependency's peer range against the installed framework.
- [ ] Add only the router, data layer, or component library the feature actually needs.
- [ ] Keep secrets in server-only configuration; public build variables are readable by users.
- [ ] Define deployment output and the supported rendering model before integrating server code.

## Post-scaffold checks

- [ ] Select the official React TypeScript scaffold and preserve its JSX/plugin settings.
- [ ] Keep a client-only SPA unless SSR is an explicit requirement; Vite alone supplies no server render.
- [ ] Configure the host fallback for nested SPA URLs and test a direct request to one.
- [ ] Check the installed router major before choosing import paths.
- [ ] Keep filters and pagination in URL search parameters when links must be shareable.
- [ ] Use component state first; add a store only for shared state with an identified lifetime.
- [ ] Give server-state caches their own keys, error UI, and mutation invalidation.
- [ ] Use the Vite public-variable prefix only for values safe to include in the client bundle.
- [ ] Check deployment base paths against links, assets, and lazy-loaded chunks.
- [ ] Keep TypeScript path aliases aligned with bundler and test resolver settings.
- [ ] Check the installed Vite migration guide before changing chunk splitting or transform options.
- [ ] Import heavy optional features on interaction or route entry; measure the result.
- [ ] Test retry behavior and preserve user input through recoverable errors.

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

- Framework implementation: [../../references/vite-react-patterns.md](../../references/vite-react-patterns.md).
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
