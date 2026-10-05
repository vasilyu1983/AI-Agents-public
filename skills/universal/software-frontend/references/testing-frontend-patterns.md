# Component and unit testing

Load when implementing frontend behavior. Browser journeys, Playwright fixtures, visual baselines, and E2E CI belong to [qa-testing-playwright](../../qa-testing-playwright/SKILL.md); accessibility testing belongs to [qa-testing-accessibility](../../qa-testing-accessibility/SKILL.md).

## Contents

- [Choose the smallest useful proof](#choose-the-smallest-useful-proof)
- [Use the generated runner configuration](#use-the-generated-runner-configuration)
- [Assert behavior through accessible queries](#assert-behavior-through-accessible-queries)
- [Isolate provider lifetimes](#isolate-provider-lifetimes)
- [Mock at the boundary](#mock-at-the-boundary)
- [Hooks and timers](#hooks-and-timers)
- [Framework adapters](#framework-adapters)
- [Next.js Server Components and actions](#nextjs-server-components-and-actions)
- [Useful defect cases](#useful-defect-cases)
- [Handoff evidence](#handoff-evidence)

## Choose the smallest useful proof

| Behavior | Proof |
|---|---|
| Formatting, parsing, reducer, URL-state transformation | Unit test with real edge-case inputs |
| Input, button, validation, pending/error UI | Component test with user interaction |
| Hook that depends on a provider | Hook/component test with an isolated provider |
| Query/mutation response mapping | Component integration with a network stub |
| SSR hydration, browser API, async RSC, navigation | Browser proof through the owning QA skill |

Do not choose a fixed unit/component/E2E percentage or claim universal execution times. Match the test layer to the defect and observe runtime in the actual project.

## Use the generated runner configuration

Keep the repository's Vitest, Angular TestBed, Vue Test Utils, or Svelte Testing Library setup. A generic pasted runner config can change aliases, transforms, DOM environment, or framework plugins.

For a React DOM suite using Vitest, a typical setup file is:

```typescript
import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

afterEach(cleanup);
```

Check the installed runner's globals setting. Import `test`, `expect`, and hooks explicitly in examples instead of assuming globals.

A DOM emulator does not implement browser layout or every browser API. Use browser proof for geometry, native focus/dialog interactions, canvas, or hydration failures rather than stubbing away the disputed behavior.

## Assert behavior through accessible queries

Prefer role and accessible name for controls, label text for fields, and visible text for outcomes. A test ID is useful when no user-facing selector exists; it must not hide missing labels.

```tsx
import { test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DisplayNameEditor } from './DisplayNameEditor';

test('preserves draft input after a rejected save', async () => {
  const user = userEvent.setup();
  render(<DisplayNameEditor save={async () => ({ ok: false })} />);

  await user.type(screen.getByRole('textbox', { name: 'Display name' }), 'Draft');
  await user.click(screen.getByRole('button', { name: 'Save' }));

  expect(await screen.findByRole('alert')).toHaveTextContent('Could not save');
  expect(screen.getByRole('textbox', { name: 'Display name' })).toHaveValue('Draft');
});
```

This example specifies a component contract, not a bundled implementation. Adapt it to the actual error shape and semantics rather than adding a component solely to match the test.

- Await `userEvent` interactions.
- Use `findBy*` for an element that appears asynchronously.
- Use `queryBy*` when asserting absence.
- Keep `waitFor` callbacks assertion-only; repeated clicks or mutations inside them can create false results.
- Assert that an error path does not show success or discard input.
- Avoid snapshots of an entire DOM tree; test the specific behavior that could regress.

## Isolate provider lifetimes

Create a fresh query cache, store, router, and session for each test. Do not reuse production module singletons across tests.

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { PropsWithChildren } from 'react';

export function createQueryWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  function Wrapper({ children }: PropsWithChildren) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  }
  return { Wrapper, client };
}
```

Use a new wrapper per test and clear its client during teardown. Disable retry only when testing a single rejected response; enable the actual retry policy in tests that verify retries.

Keep fixtures synthetic and small. The fixture should exercise the feature's contract, including empty results, a rejected mutation, or a session switch when relevant.

## Mock at the boundary

Prefer a network-level stub over mocking every custom hook. Let the component, query key, DTO parser, and state transitions run together.

```typescript
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll } from 'vitest';

const server = setupServer(
  http.get('https://api.example.test/profile', () =>
    HttpResponse.json({ id: 'example-1', displayName: 'Example' })
  )
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

Align the request URL with the application's configured test API. Unexpected requests should fail the test rather than reaching a live service. Use per-test handlers for rejection, malformed responses, and delayed completion.

A successful mock response proves only the mocked contract. Add API/service integration proof in its owner when behavior depends on server authorization or persistence.

## Hooks and timers

Use `renderHook` for reusable hook behavior; a component interaction is often better proof for a hook used only by one feature.

- Wrap direct state updates in the runner's `act` helper when required.
- When fake timers are necessary, configure user-event's timer advancement for the installed versions.
- Flush only the intended scheduled work; do not replace every asynchronous wait with a timer jump.
- Restore real timers and spies after each test.
- Test cancellation/unmount behavior if stale responses can overwrite newer state.

## Framework adapters

| Stack | Component/unit boundary |
|---|---|
| React | Testing Library with the repository's transforms and provider wrappers |
| Vue/Nuxt | Vue Test Utils or Nuxt test utilities; preserve auto-import and runtime context |
| Angular | TestBed with the configured runner; use HTTP testing providers for resource reads |
| Svelte | Svelte Testing Library plus the Svelte plugin; observe rendered behavior rather than compiled internals |

Do not use a React renderer for other frameworks or transplant plain-Vite setup into a framework that supplies its own transform/runtime layer.

## Next.js Server Components and actions

The [Next.js Vitest guide](https://nextjs.org/docs/app/guides/testing/vitest) describes support for synchronous Server/Client Components and recommends E2E for async Server Components. Check installed support before claiming an async RSC render is covered.

Awaiting a page function and rendering returned JSX bypasses the RSC transport, streaming, framework request context, and hydration. It can test an extracted pure function, but cannot establish route correctness.

For actions, unit-test extracted validation and result mapping. Framework integration proof must still verify authentication, request context, redirects, serialization, and invalidation. Do not mock all of those and describe the result as a secure end-to-end mutation test.

## Useful defect cases

- Required field omitted: error is associated with the field; submit has no successful effect.
- Mutation rejected: draft remains, pending state clears, success is absent.
- Duplicate click: behavior follows the concurrent-submission contract.
- Response malformed: parser rejects it and the UI reports failure.
- Input changes during fetch: obsolete data does not replace the newer result.
- Account changes: previous user's cache is not displayed.
- Component unmounts: subscriptions and obsolete work are cleaned up.
- Retry accepted: the confirmed response replaces optimistic state.

Select only cases reachable by the changed contract. Tests that restate component markup without exercising a meaningful risk add maintenance cost.

## Handoff evidence

Record which behavior failed before the fix, the test command/result, and the layers actually exercised. Report browser-only or server behavior separately when a component/unit suite cannot prove it.
