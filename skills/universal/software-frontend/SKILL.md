---
name: software-frontend
description: "Builds web frontend UI and rendering. Use when implementing components or fixing hydration, SSR, routing, or state; UX, accessibility, and performance audits have other owners."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# Frontend Engineering

Use this skill for production web frontend work across React, Next.js, Vue, Nuxt, Angular, Svelte, and adjacent tooling. It owns framework choice, frontend implementation patterns, hydration and SSR debugging, state and data-fetching patterns, and frontend release discipline.

## Quick Reference

| Task | Use |
|------|-----|
| Full-stack React app | [references/fullstack-patterns.md](references/fullstack-patterns.md), [assets/nextjs/template-nextjs-tailwind-shadcn.md](assets/nextjs/template-nextjs-tailwind-shadcn.md) |
| React SPA | [references/vite-react-patterns.md](references/vite-react-patterns.md), [assets/vite-react/template-vite-react-ts.md](assets/vite-react/template-vite-react-ts.md) |
| React Router or Remix | [references/remix-react-patterns.md](references/remix-react-patterns.md), [assets/remix/template-remix-react.md](assets/remix/template-remix-react.md) |
| Vue or Nuxt | [references/vue-nuxt-patterns.md](references/vue-nuxt-patterns.md), [assets/vue-nuxt/template-nuxt4-tailwind.md](assets/vue-nuxt/template-nuxt4-tailwind.md) |
| Angular | [references/angular-patterns.md](references/angular-patterns.md), [assets/angular/template-angular21-standalone.md](assets/angular/template-angular21-standalone.md) (post-scaffold checklist; use the installed CLI) |
| Svelte or SvelteKit | [references/svelte-sveltekit-patterns.md](references/svelte-sveltekit-patterns.md), [assets/svelte/template-sveltekit-runes.md](assets/svelte/template-sveltekit-runes.md) |
| State, tests, performance, and gotchas | [references/state-management-patterns.md](references/state-management-patterns.md), [references/testing-frontend-patterns.md](references/testing-frontend-patterns.md), [references/performance-optimization.md](references/performance-optimization.md), [references/production-gotchas.md](references/production-gotchas.md), [references/operational-playbook.md](references/operational-playbook.md) |

## When to Use This Skill

- Build or scaffold a frontend app.
- Fix hydration, SSR, build, or client-server boundary issues.
- Choose routing, state, data-fetching, and component patterns.
- Set up frontend testing, performance budgets, and release gates.
- Implement UI in a modern framework with production-safe defaults.

## Route Elsewhere

- Backend APIs or service implementation: use [software-backend](../software-backend/SKILL.md).
- API contract design: use [dev-api-design](../dev-api-design/SKILL.md).
- UI or UX design: use [software-ui-ux-design](../software-ui-ux-design/SKILL.md); accessibility implementation/remediation: [software-accessibility](../software-accessibility/SKILL.md); formal audits/testing: [qa-testing-accessibility](../qa-testing-accessibility/SKILL.md); performance audits: [software-performance](../software-performance/SKILL.md).
- Mobile native development: use [software-mobile](../software-mobile/SKILL.md).
- Internationalization setup: use [software-localisation](../software-localisation/SKILL.md).
- E2E test-authoring focus: use [qa-testing-playwright](../qa-testing-playwright/SKILL.md).
- Natural conversational chat surfaces in a web app (Chrome `window.ai` built-in AI, WebLLM / transformers.js in-browser inference, cloud LLM streaming, with deterministic fallback when on-device unavailable): use [ai-context-layer/references/conversational-surfaces-cross-platform.md](../ai-context-layer/references/conversational-surfaces-cross-platform.md).

## Defaults

- Pick the framework that matches routing and rendering needs instead of defaulting blindly to one stack.
- Prefer the boring, already-adopted choice in the repo over the newest framework feature. A new primitive (a rendering mode, a compiler, a routing convention) earns adoption only after it has shipped stable for a while and the team has a concrete reason — not because it is new.
- Keep the repository structure; for a new app, use the official CLI scaffold and the matching post-scaffold checklist.
- Search for repo-local frontend patterns before adding new providers, stores, or conventions.
- Treat accessibility and performance as release gates.
- Check the installed framework, lockfile, and official migration guide before adopting an API. Use [data/versions.json](data/versions.json) only as a dated discovery snapshot; confirm support before pinning.
- For a TypeScript compiler migration, check the official release notes and each API-dependent tool's support: typed ESLint, vue-tsc, Angular compiler, and svelte-check. Keep their supported compiler line until compatibility is confirmed; preserve exact lockfile resolution.

### React primitives by capability

Check the installed React/react-dom and framework compatibility before adoption; the versions below are feature boundaries, not current-version pins.

- React 19.2: `Activity` preserves hidden UI state while cleaning up its Effects; `useEffectEvent` reads props/state at invocation in Effect-triggered logic without changing the Effect's reactive dependencies. It is not a dependency-suppression trick. `cacheSignal` belongs to RSC cache lifetime/cancellation, not a client cache. See the [release notes](https://react.dev/blog/2025/10/01/react-19-2).
- React 19.3: `ViewTransition` animates transition updates; Fragment refs expose grouped DOM operations without an extra wrapper; `use(browser())` from React/react-dom opts a browser-only component out of SSR through a Suspense fallback. Keep meaningful server HTML where possible. See the [release notes](https://react.dev/blog/2026/09/09/react-19-3).
- Use the framework's supported render/cache integration rather than introducing a raw React prerender/resume pipeline. Verify Hooks lint support and browser/reduced-motion behavior for the chosen primitive.

## Workflow

1. Clarify rendering model, routing needs, SEO constraints, and deployment shape.
2. Pick the framework and template that fit the problem.
3. Load only the reference that matches the user’s framework or issue.
4. Implement with repo-local patterns for state, data fetching, styling, and testing.
5. Check hydration, accessibility, performance, and handoff requirements before signoff.

## Core Decisions

### Framework Selection

| Need | Framework | Notes |
|------|-----------|-------|
| Full-stack React, SEO | Next.js | App Router; RSC for server components; see `next` in `data/versions.json` for the current major before pinning a minor |
| Route-centric progressive enhancement | React Router (framework mode, default) | Loader/action data contracts. For legacy Remix, check official migration/support guidance before choosing a new scaffold; do not assume another Remix lineage shares React Router framework APIs |
| Client-only React SPA | Vite + React | No SSR complexity |
| Vue full-stack | Nuxt | Auto-imports, server routes; Vapor mode (no virtual DOM) is opt-in, not the default, until Nuxt, Pinia and VueUse support is confirmed — check the `vue` entry in `data/versions.json` and vuejs.org/about/releases before citing a version |
| Angular app | Angular (current major, see `@angular/core` in `data/versions.json`) | Standalone components, signal-first, zoneless change detection; check angular.dev/reference/releases for the current major and LTS line, and angular.dev for zoneless defaults in that major, before pinning |
| Svelte-first | SvelteKit | Runes-based reactivity; see `svelte` in `data/versions.json` for the current major |

Pick the rendering model first (CSR / SSR / SSG / hybrid), then the framework. When two frameworks both fit, default to the one the team already runs in production — introducing a second framework has a real ongoing cost (build tooling, testing setup, hiring, mental context-switching) that rarely pays for itself on a single feature.

### Server vs. Client Rendering Judgment

- Default to server rendering (RSC, SSR, or SSG) for anything that is primarily content, SEO-sensitive, or benefits from a fast first paint without shipping a client-side data-fetch waterfall.
- Reach for client-side rendering deliberately: highly interactive widgets, apps behind auth where SEO doesn't matter, or state that must survive without a round trip (drag-and-drop, canvas/WebGL, real-time collaboration).
- Every client component has a hydration cost: JS shipped, parsed, and executed before the component becomes interactive. Treat `'use client'` (or framework equivalent) as an opt-in cost, not a free escape hatch — push it as far down the tree as the interactivity actually requires, rather than marking whole route trees client-side because one child needs `onClick`.
- A component that only needs interactivity for a small piece (an accordion toggle, a tooltip) can usually stay server-rendered with a small client island around just that piece, instead of promoting the whole page to client-rendered.

### Design System vs. Component Library

- A component library (shadcn/ui, Radix, Angular Material, PrimeNG, Nuxt UI) supplies unopinionated or lightly-opinionated building blocks — buttons, dialogs, form controls — with behavior primitives that still require accessible composition, labels, focus management, and verification; visual language is largely left to the consumer.
- A design system is a product decision: a documented, versioned set of tokens (color, spacing, type scale), usage rules, and often a component API layered on top of one or more component libraries. It exists to keep a product visually and behaviorally consistent across teams and time.
- Don't build a design system when a component library already solves the problem — that's usually over-engineering for a single app or small team. Do insist on a design system (or at least shared tokens) once multiple teams or products need to look and behave consistently, or once the same visual inconsistencies keep recurring across PRs.
- When a repo already has a design system, treat its component API as the source of truth over the underlying library's raw components — don't reach past the design system to Radix/shadcn primitives directly unless the design system has a real gap.

### State and Data Fetching

| Data kind | Default tool | Add this only when… |
|-----------|-------------|----------------------|
| Server state (async, cached) | TanStack Query (or framework loaders when the router already provides them) | Use SWR only when the repo already standardizes on it |
| Global client state (shared across routes) | Zustand (Pinia in Vue) | Switch to Jotai only when state is genuinely atomic/granular, not just shared |
| Server-owned state in RSC apps | Server components + React cache | Client store is needed for interactive/optimistic UI only |
| URL-driven state (filters, pagination) | URL search params | Don't duplicate into a store |

Do not create new global state layers when local state or server-driven patterns are enough.

### UI State Completeness Gate

Enumerate every state the surface can actually reach and handle each deliberately. Loading, empty, error, and success are the baseline where applicable; add background refresh, partial, stale, permission-denied, recoverable, and terminal variants only when the data and authorization contracts can produce them. Mark inapplicable states explicitly during review. Preserve the user’s input and last safe rendered state across retries where appropriate.

### Hydration and SSR Safety

Watch for:
- browser-only values during SSR
- client hooks in server components
- stale effect dependencies
- route and link drift after refactors

If the bug smells like hydration, start with [references/production-gotchas.md](references/production-gotchas.md).

### Release Discipline

Minimum release gate:

- [ ] Lint the edited files
- [ ] Type-check the changed surface (`tsc --noEmit` or equivalent)
- [ ] Run broader lint, type, and build once before handoff
- [ ] Accessibility gate: automated checks plus keyboard/assistive-technology proof for affected behavior; an axe-core pass alone does not establish WCAG 2.2 AA conformance. [WCAG 2.2](https://www.w3.org/TR/WCAG22/#new-features-in-wcag-2-2) adds criteria but removes 4.1.1 Parsing; if a policy requires 2.1, continue testing/reporting that criterion as needed. EU (EAA): the legal reference is whichever EN 301 549 version is cited in the Official Journal — a newer version that adopts WCAG 2.2 is not the legal floor until it is cited; treat 2.2 AA as the engineering target and get the citation status from [software-accessibility](../software-accessibility/SKILL.md)
- [ ] Performance budget: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 at the 75th percentile of page loads (field data, mobile and desktop separately) on the user-facing path
- [ ] Hydration verified: no console errors in SSR/RSC pages after navigation
- [ ] AI-generated code checked for hook rule violations, weak native semantics, and incorrect ARIA

### AI-Generated Frontend Risk

Common AI-specific frontend failures:
- hooks rule violations
- client/server boundary confusion
- div soup and weak semantics
- stale closures and missing deps
- over-fetching in components
- weak keyboard and screen-reader behavior
- imports that don't exist in the project's actual dependency tree, or that exist but at a different version/API shape than the generated code assumes
- components that reinvent a pattern the repo already has (a second modal implementation, a parallel fetch wrapper) instead of matching the existing one

Treat these as expected defects to check for, not rare edge cases. Before accepting AI-generated frontend code, verify it against the real codebase, not just its own internal plausibility: confirm every import resolves in `package.json`/lockfile, confirm the component/hook API used matches the installed version (not a newer or older one the model was trained on), and confirm styling and data-fetching match repo-local conventions rather than introducing a second competing pattern.

## Output Modes

Default to one of these:

- Frontend implementation plan:
  framework, template, state, testing, and release gates.
- Issue diagnosis:
  likely frontend failure mode, affected layer, and fix path.
- Scaffold recommendation:
  framework choice, template, and rationale.
- Production hardening brief:
  hydration, performance, accessibility, and testing checklist.

## Known Traps

- Crossing server and client boundaries casually in SSR or RSC-capable stacks, then debugging hydration mismatches that were baked into the render model.
- Reading browser-only values during server render and assuming the framework will reconcile the difference safely.
- Introducing a new global store before checking whether local state plus server-state tools already cover the problem.
- Refactoring routes, links, or layout composition without validating SEO, navigation semantics, and preserved URL behavior.
- Accepting AI-generated component output that looks plausible but quietly regresses semantics, keyboard support, or hook correctness — imports that don't resolve at the installed version, or a second modal/fetch pattern next to the one the repo already has.
- Picking a framework because it is fashionable rather than because it matches the rendering model.

## Navigation

- Framework references: [references/fullstack-patterns.md](references/fullstack-patterns.md), [references/vite-react-patterns.md](references/vite-react-patterns.md), [references/remix-react-patterns.md](references/remix-react-patterns.md), [references/vue-nuxt-patterns.md](references/vue-nuxt-patterns.md), [references/angular-patterns.md](references/angular-patterns.md), [references/svelte-sveltekit-patterns.md](references/svelte-sveltekit-patterns.md)
- Operational references: [references/production-gotchas.md](references/production-gotchas.md), [references/operational-playbook.md](references/operational-playbook.md), [references/state-management-patterns.md](references/state-management-patterns.md), [references/testing-frontend-patterns.md](references/testing-frontend-patterns.md), [references/performance-optimization.md](references/performance-optimization.md), [references/web-platform-apis.md](references/web-platform-apis.md) (native browser alternatives; feature-detect support), [references/artifacts-builder.md](references/artifacts-builder.md), [references/mui-integration-notes.md](references/mui-integration-notes.md) (MUI theme, SSR, MUI X licensing, form integration)
- Templates: [assets/nextjs/template-nextjs-tailwind-shadcn.md](assets/nextjs/template-nextjs-tailwind-shadcn.md), [assets/vite-react/template-vite-react-ts.md](assets/vite-react/template-vite-react-ts.md), [assets/remix/template-remix-react.md](assets/remix/template-remix-react.md), [assets/vue-nuxt/template-nuxt4-tailwind.md](assets/vue-nuxt/template-nuxt4-tailwind.md), [assets/angular/template-angular21-standalone.md](assets/angular/template-angular21-standalone.md) (post-scaffold checklist), [assets/svelte/template-sveltekit-runes.md](assets/svelte/template-sveltekit-runes.md)
- Related skills: [software-backend](../software-backend/SKILL.md), [software-ui-ux-design](../software-ui-ux-design/SKILL.md), [software-localisation](../software-localisation/SKILL.md), [qa-testing-playwright](../qa-testing-playwright/SKILL.md), [ops-devops-platform](../ops-devops-platform/SKILL.md)

Source mapping lives in [data/sources.json](data/sources.json).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
