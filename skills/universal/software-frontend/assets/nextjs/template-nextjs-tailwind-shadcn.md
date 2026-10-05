# Next.js + Tailwind + shadcn/ui: post-scaffold checklist

Use the [official scaffold documentation](https://nextjs.org/docs/app/api-reference/cli/create-next-app) for the installed toolchain. This checklist records application-specific decisions after generation; it does not replace CLI output.

## Before adding application code

- [ ] Use the official scaffold in a new directory, or preserve an existing app's structure.
- [ ] Read the CLI's supported runtime and package-manager requirements; commit its lockfile.
- [ ] Keep generated compiler, bundler, and test configuration unless a concrete requirement changes it.
- [ ] Confirm every extra dependency's peer range against the installed framework.
- [ ] Add only the router, data layer, or component library the feature actually needs.
- [ ] Keep secrets in server-only configuration; public build variables are readable by users.
- [ ] Define deployment output and the supported rendering model before integrating server code.

## Post-scaffold checks

- [ ] Keep App Router layout, loading, error, and not-found conventions from the scaffold.
- [ ] Place interactive client islands below server-rendered content; do not mark the root tree use client.
- [ ] Follow the Tailwind integration generated for the installed major; do not paste a legacy JS config.
- [ ] Use the current shadcn installer for the scaffold and review generated components before customizing.
- [ ] Keep design tokens shared between CSS and copied components.
- [ ] Configure providers at the narrowest subtree that needs their client state.
- [ ] Pass explicit response DTOs into client components; keep database clients and session secrets server-only.
- [ ] Validate and authorize every mutation on the server; a protected layout is insufficient.
- [ ] Check cache behavior for public versus user-specific data and refresh affected views after mutations.
- [ ] Use the installed Next.js proxy/middleware convention from its migration guide.
- [ ] Confirm image allowlists, sizes, and the actual above-fold image loading strategy.
- [ ] Implement metadata for each content route and retain useful SSR fallbacks for browser-only widgets.
- [ ] Run a browser check across both initial SSR and client navigation.

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

- Framework implementation: [../../references/fullstack-patterns.md](../../references/fullstack-patterns.md).
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
