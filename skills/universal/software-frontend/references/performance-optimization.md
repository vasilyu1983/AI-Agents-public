# Framework performance changes

Load after a frontend bottleneck has been measured. Metric definitions, field/lab methodology, cross-platform diagnosis, budgets, and observability belong to [software-performance](../../software-performance/SKILL.md). Browser benchmark implementation belongs to [qa-testing-performance](../../qa-testing-performance/SKILL.md).

## Contents

- [Keep measurement with the change](#keep-measurement-with-the-change)
- [React rendering](#react-rendering)
- [Next.js client boundary](#nextjs-client-boundary)
- [Next.js images](#nextjs-images)
- [Next.js fonts and scripts](#nextjs-fonts-and-scripts)
- [Vite and React SPA](#vite-and-react-spa)
- [Vue and Nuxt](#vue-and-nuxt)
- [Angular](#angular)
- [Svelte and SvelteKit](#svelte-and-sveltekit)
- [Verification and rollback](#verification-and-rollback)

## Keep measurement with the change

Record the route, user action, rendering mode, production build, and comparable before/after input. A faster dev server or a smaller bundle alone does not prove a faster user interaction.

| Measured symptom | Framework investigation |
|---|---|
| Heavy initial JavaScript | Client boundary, optional imports, duplicate packages |
| Repeated render/commit work | State subscription, prop identity, derived-state placement |
| SSR-to-client duplicate fetch | Loader/query hydration ownership and cache keys |
| Slow route reveal | Dependent fetch waterfall, Suspense/layout boundary |
| Image-related delay or shift | Framework image options and responsive sizes |
| Navigation jank | Route data, prefetch policy, urgent versus transition work |

Use the product's measured budget. Universal gzipped-byte ceilings and unsourced tool speedup claims are not defaults.

## React rendering

- Keep transient state near the surface that changes; a root provider update can rerender unrelated consumers.
- Subscribe to the needed slice of an external store rather than its entire object.
- Use stable list identities; replacing keys remounts components and loses state.
- Use `memo`, `useMemo`, or `useCallback` only where measured work or referential identity requires them.
- With React Compiler, verify the installed integration and inspect profiler evidence before removing existing memoization.
- Use a transition for non-urgent result rendering; keep the controlled input update urgent.
- `useDeferredValue` defers rendering, not network requests; it is not a debounce or rate limiter.
- Virtualize only when DOM/render cost is the bottleneck, and verify focus, accessible semantics, scroll restoration, and find behavior.

For supported React builds, Performance Tracks distinguish scheduling, render, and effect work. Profile a representative production/profiling build instead of treating development Strict Mode repetition as a production regression.

## Next.js client boundary

Keep static content and server-only dependencies outside the client graph. A large client layout makes all imported descendants part of that graph; passing server-rendered children can preserve composition without a broad client import.

- Inspect route chunks after changing a provider, component library, or heavy feature import.
- Use dynamic imports for genuinely optional client features, not content required at first paint.
- Declare lazy component loaders at module scope; recreating them during render remounts state.
- Keep a meaningful Suspense/loading fallback with reserved space.
- Test initial SSR and client navigation separately; cache state can make one appear faster.
- Use the installed version's Cache Components/caching guide before adopting cache directives.
- Keep private data out of shared cache entries; request memoization is not durable cross-request caching.

Raw React prerender/resume APIs are framework-integration tools. Use the framework's supported rendering mode instead of adding a parallel hand-built SSR pipeline.

## Next.js images

Read the installed version's [Image API](https://nextjs.org/docs/app/api-reference/components/image) before choosing loading props. The `priority` prop was deprecated at the Next.js 16 boundary in favor of `preload`; select preload, eager loading, or fetchPriority for the actual critical image rather than setting all of them.

- Supply intrinsic dimensions, or use `fill` in a correctly sized positioned parent.
- Give responsive images a `sizes` value matching the CSS layout.
- Reserve the rendered box so hydration/image completion does not shift content.
- Avoid lazy-loading the measured above-fold critical image.
- Restrict remote patterns to the intended sources.
- Check optimization behavior through the production adapter/CDN, including its output formats and cache policy.

Loading every image eagerly can compete with the critical asset; adding preload indiscriminately is not an optimization.

## Next.js fonts and scripts

Use `next/font` with only the required families, subsets, and weights. Inspect layout changes when fallback metrics differ; a font integration alone does not guarantee zero shift.

For [next/script](https://nextjs.org/docs/app/api-reference/components/script):

- Use `afterInteractive` for scripts needed after hydration and `lazyOnload` for optional idle work.
- Keep `beforeInteractive` limited to a documented early requirement; it does not block hydration according to the API contract.
- Check worker-strategy support before use: the documentation marks it experimental and unsupported in App Router.
- Honor the application's consent boundary before loading tracking code.
- Measure both download and later main-thread work; a deferred script can still harm interactions.

## Vite and React SPA

Use the installed Vite migration/configuration guide for the current bundler. Do not paste old `manualChunks` shapes into a different bundler's splitting API.

- Inspect duplicate runtime packages and unused heavy modules in the production output.
- Split route/interaction-specific features and preserve an error UI when a chunk fails to load.
- Check host cache headers and asset base paths using the built output.
- Keep client routing fallback separate from caching hashed static assets.
- Confirm a library's package exports/tree-shaking behavior rather than assuming a named import guarantees removal.

A client SPA still must fetch its initial data; code splitting cannot eliminate the data waterfall by itself.

## Vue and Nuxt

- Keep SSR-aware useFetch/useAsyncData keys stable and input-specific to avoid duplicate work or stale sharing.
- Avoid passing a frequently changing broad object when a narrow prop is sufficient.
- Use computed derivations instead of Effects/watchers that copy one reactive state into another.
- Lazy-load expensive optional components with a reserved fallback box.
- Use ClientOnly for browser-dependent behavior, not as a universal hydration workaround.
- Check Nuxt island/lazy-hydration support and module compatibility in the installed release before enabling it.
- Preserve request-specific state isolation through SSR and payload hydration.

## Angular

- Use stable `track` identities in `@for`; changing identities causes DOM recreation.
- Keep derivations in computed signals and effects limited to external synchronization.
- Evaluate `@defer` for optional expensive sections; keep essential content and its dependencies in the initial route.
- Lazy-load route components where the feature boundary supports it.
- Check the application's change-detection configuration and library compatibility before migrating to zoneless.
- Preserve HTTP transfer-cache rules for private responses; hydration reuse must not leak user data.

Inspect the rendered interaction and network calls after a signal/resource change. Fewer subscriptions are not proof of fewer requests or faster paint.

## Svelte and SvelteKit

- Use `$derived` for derivation; an `$effect` that writes another state can add update cycles.
- Keep independent load operations concurrent while preserving real data dependencies.
- Use server/universal loads according to the trust boundary, and avoid duplicate component fetches.
- Use keyed lists when identity must survive reorder, and verify focus/state behavior.
- Limit preloading to likely navigation and account for data-saving preferences when supported.
- Check adapter and prerender compatibility before moving work to build time.
- Experimental remote functions need explicit adoption and performance evidence; do not replace a working load/action flow solely for novelty.

## Verification and rollback

- Rebuild and compare the same route/action with the same synthetic data and cache conditions.
- Confirm an optimization preserves error, loading, permission, keyboard, and focus behavior.
- Inspect network requests as well as render traces; a rerender reduction can hide extra fetching.
- Keep the change local enough to revert if field evidence contradicts the lab result.
- Record measured results or state that a performance effect is not yet measured.

For the broader diagnosis or threshold decision, load [software-performance](../../software-performance/SKILL.md). For component regressions introduced by the implementation, load [testing-frontend-patterns.md](testing-frontend-patterns.md).
