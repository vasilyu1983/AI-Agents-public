# React Router framework mode / existing Remix: post-scaffold checklist

Use the [official scaffold documentation](https://reactrouter.com/start/framework/installation) for the installed toolchain. This checklist records application-specific decisions after generation; it does not replace CLI output.

## Before adding application code

- [ ] Use the official scaffold in a new directory, or preserve an existing app's structure.
- [ ] Read the CLI's supported runtime and package-manager requirements; commit its lockfile.
- [ ] Keep generated compiler, bundler, and test configuration unless a concrete requirement changes it.
- [ ] Confirm every extra dependency's peer range against the installed framework.
- [ ] Add only the router, data layer, or component library the feature actually needs.
- [ ] Keep secrets in server-only configuration; public build variables are readable by users.
- [ ] Define deployment output and the supported rendering model before integrating server code.

## Post-scaffold checks

- [ ] For a new route-driven React app, use the supported React Router framework scaffold.
- [ ] For an existing Remix app, follow its migration guide instead of recreating its routes.
- [ ] Check framework versus data-router mode before copying a loader or route module.
- [ ] Use generated route types; align imports and adapters with the installed major.
- [ ] Keep read work in loaders and server mutations in actions with request-scoped authorization.
- [ ] Use Form for navigational submissions and fetcher for local submissions without navigation.
- [ ] Preserve progressive enhancement where the product requires no-JavaScript submissions.
- [ ] Keep pending and action-error UI close to the form that produced them.
- [ ] Review revalidation conditions so successful mutations refresh affected data.
- [ ] Keep session cookies and privileged service calls in server modules.
- [ ] Define a route error boundary and test direct URL entry as well as navigation.
- [ ] Check prerender/SSR/SPA output and adapter requirements before enabling a mode.
- [ ] Check official release/support guidance before adding legacy Remix dependencies.

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

- Framework implementation: [../../references/remix-react-patterns.md](../../references/remix-react-patterns.md).
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
