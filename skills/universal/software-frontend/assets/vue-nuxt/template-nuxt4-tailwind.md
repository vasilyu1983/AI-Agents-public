# Nuxt + Vue + Tailwind: post-scaffold checklist

Use the [official scaffold documentation](https://nuxt.com/docs/getting-started/installation) for the installed toolchain. This checklist records application-specific decisions after generation; it does not replace CLI output.

## Before adding application code

- [ ] Use the official scaffold in a new directory, or preserve an existing app's structure.
- [ ] Read the CLI's supported runtime and package-manager requirements; commit its lockfile.
- [ ] Keep generated compiler, bundler, and test configuration unless a concrete requirement changes it.
- [ ] Confirm every extra dependency's peer range against the installed framework.
- [ ] Add only the router, data layer, or component library the feature actually needs.
- [ ] Keep secrets in server-only configuration; public build variables are readable by users.
- [ ] Define deployment output and the supported rendering model before integrating server code.

## Post-scaffold checks

- [ ] Use the official Nuxt scaffold and its generated directory conventions for the installed major.
- [ ] Keep script setup and composables aligned with the repository; avoid a second state layer.
- [ ] Use useFetch/useAsyncData for SSR-aware page data rather than duplicate setup-time requests.
- [ ] Give async-data keys stable input semantics and check navigation/refetch behavior.
- [ ] Keep request-specific state out of process-global stores to prevent SSR data leakage.
- [ ] Use useState or the existing Pinia integration when state must serialize across hydration.
- [ ] Keep runtimeConfig.public limited to public data; secrets remain server-side.
- [ ] Use ClientOnly only for features requiring browser APIs and provide useful fallback content.
- [ ] Check module peer compatibility before adding Tailwind, UI, image, or auth integrations.
- [ ] Configure the Nitro deployment preset for the actual host and server capabilities.
- [ ] Check route rules against public/user-specific caching requirements.
- [ ] Use useSeoMeta for metadata and inspect the initial server HTML.
- [ ] Test hydration after both direct loads and client navigation with real data.

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

- Framework implementation: [../../references/vue-nuxt-patterns.md](../../references/vue-nuxt-patterns.md).
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
