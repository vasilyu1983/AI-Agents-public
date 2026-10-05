# Frontend boundaries in full-stack applications

Load for SSR/RSC data flow, authentication UI, forms, and cache synchronization. Backend services and schemas belong to [software-backend](../../software-backend/SKILL.md); public API contracts belong to [dev-api-design](../../dev-api-design/SKILL.md).

## Contents

- [Choose the boundary](#choose-the-boundary)
- [Draw the data flow before coding](#draw-the-data-flow-before-coding)
- [Server and client composition](#server-and-client-composition)
- [Response DTOs](#response-dtos)
- [Authentication UI](#authentication-ui)
- [Initial reads](#initial-reads)
- [Client cache ownership](#client-cache-ownership)
- [Form mutation boundary](#form-mutation-boundary)
- [React form state](#react-form-state)
- [Server Actions and cache synchronization](#server-actions-and-cache-synchronization)
- [Optimistic updates](#optimistic-updates)
- [Error presentation](#error-presentation)
- [Pagination and URL state](#pagination-and-url-state)
- [tRPC at the frontend boundary](#trpc-at-the-frontend-boundary)
- [Streaming and subscriptions](#streaming-and-subscriptions)
- [Boundary verification](#boundary-verification)
- [Handoff contract](#handoff-contract)

## Choose the boundary

| Surface | Default | Change when |
|---|---|---|
| Initial content in an SSR/RSC app | Framework loader or server component | A browser-only feature requires client execution |
| Interactive server state | Existing framework data APIs or query cache | The router cannot support the required lifecycle |
| Same-app form mutation | Framework action with server validation | Other clients need an independently versioned API |
| Public or multi-client data | Documented API with response DTOs | An internal same-language contract is sufficient |
| Local UI state | Component state | Several surfaces share the same lifetime |

A Server Component performs one render; it is not a live subscription. Use a supported streaming/subscription transport when updates must arrive without navigation or refresh.

## Draw the data flow before coding

Record these for the changed feature:

1. The source of truth and the layer that may write it.
2. The authentication context attached to each read and mutation.
3. The minimal fields the browser needs.
4. Loading, error, and cache behavior across initial render and navigation.
5. The event that makes each view stale and how it becomes current again.

Keep database clients, signing keys, privileged tokens, and internal service credentials in server-only modules. Framework client bundles and public build variables are inspectable by the user.

## Server and client composition

For Next.js, follow the installed version's [Server and Client Components guide](https://nextjs.org/docs/app/getting-started/server-and-client-components). A client module imports its transitive dependencies into the client graph; keep the boundary close to the interactive leaf.

- Fetch content in the server layer when that avoids a client waterfall.
- Pass a DTO, not an ORM entity with internal or privileged fields.
- Pass server-rendered content through composition slots rather than importing server modules from a client file.
- Use the framework's serialization contract; ordinary callbacks cannot cross the boundary as props.
- Keep providers as deep as practical so static ancestors stay server-rendered.
- A client component can still participate in SSR; `use client` does not make browser APIs safe during initial render.
- Use the framework's server-only guard when available so an accidental import fails at build time.

Do not fetch your own public HTTP endpoint from a server render just to reach a service already available in that process. Call the server-only data layer directly when its authorization and caching contract supports it.

## Response DTOs

Share types through the contract package or generated client already used by the repo. TypeScript types do not validate an HTTP response at runtime.

```typescript
// Example browser-facing contract; no password hash or internal role policy.
export type ProfileView = {
  id: string;
  displayName: string;
  avatarUrl: string | null;
};

export type FieldErrors = Partial<Record<'displayName', string[]>>;
export type SaveProfileResult =
  | { ok: true; profile: ProfileView }
  | { ok: false; kind: 'validation'; fieldErrors: FieldErrors }
  | { ok: false; kind: 'unauthorized' | 'conflict' | 'unavailable' };
```

Parse untrusted data at the boundary using the installed schema library. A generic `fetch<T>()` cast is insufficient. Keep the schema import browser-safe; split a shared contract from modules that load server secrets.

## Authentication UI

Use the application's existing auth provider and session contract. Do not add handwritten JWT signing, password storage, or a second auth store from an example.

- Render session unknown/loading separately from signed out.
- Let the server decide identity and permissions for every request.
- Treat route guards, proxy checks, and hidden controls as UX; they cannot authorize a mutation.
- For browser sessions, prefer the established secure cookie flow rather than persisting bearer tokens in localStorage by default.
- Check the provider's cookie, CSRF, redirect, and cross-origin requirements with [software-security-appsec](../../software-security-appsec/SKILL.md).
- Keep permissions displayed in the UI synchronized after role changes and session expiration.
- Clear user-specific query caches on sign-out or account switch.
- Validate return destinations against the application's allowed routes; do not trust a URL supplied by the browser.

A signed-out response can arrive while the page is open. Preserve safe draft input, explain that authentication is needed, and retry only after the new session is established.

## Initial reads

Choose one owner for a read. A loader and a client Effect fetching the same data without a hydration contract can cause duplicate requests and inconsistent states.

| Framework | Initial read boundary |
|---|---|
| Next.js App Router | Server Component/data layer; client cache only for interactive refresh |
| React Router framework mode | Route loader; clientLoader only for browser-owned data |
| Nuxt | SSR-aware useFetch/useAsyncData with stable keys |
| SvelteKit | load or server load according to the dependency's trust boundary |
| Angular | SSR/HTTP transfer-cache contract plus client read state |
| Client SPA | Query cache or route data API; account for the initial network request |

For independent reads, start work together and await at the boundary that needs it. For dependent reads, preserve dependency order; parallelizing them blindly changes correctness.

## Client cache ownership

Use the router's data lifecycle when it already owns the feature. Add TanStack Query or the existing equivalent for background refresh and interactive server state that the router does not cover.

A query key identifies the response contract, not just the component:

- Include filters, page/cursor, locale, tenant, or account context when they change the result.
- Keep credentials out of keys and logs.
- Cancel obsolete requests when a new input makes their results irrelevant.
- Avoid process-global query clients for request-specific SSR data.
- Set hydration behavior deliberately so stale time does not accidentally duplicate the initial fetch.
- Make expired sessions and permission changes invalidate private data.

Cache duration is a product/data decision. Use the accepted freshness window rather than copying a universal stale-time number.

## Form mutation boundary

Before choosing a form library, identify who owns validation and the error shape. Browser validation improves feedback; server validation and authorization protect the operation.

A successful HTTP response is not always a successful domain operation. Decode the documented result and show the corresponding UI state.

1. Read the form input without discarding the user's draft.
2. Run local validation for immediate feedback.
3. Submit through the framework action or documented API.
4. Validate again and authorize at the server boundary.
5. Map field errors to their labels and associate explanatory text.
6. On success, synchronize the affected views and then navigate if required.
7. On conflict or transient failure, preserve draft state and show the recovery action.

Use the framework's pending state to prevent accidental concurrent submissions. A disabled button is insufficient for duplicate-delivery correctness; use the server's idempotency contract where the operation requires it.

## React form state

Use `useActionState` with a function matching the installed React signature. The action receives previous state before the submitted payload. Keep form errors serializable and expected failures in the result shape.

```tsx
'use client';
import { useActionState } from 'react';

type State = { message: string };

type Props = {
  save: (previous: State, input: FormData) => Promise<State>;
};

export function DisplayNameForm({ save }: Props) {
  const [state, action, pending] = useActionState(save, { message: '' });
  return (
    <form action={action}>
      <label htmlFor="display-name">Display name</label>
      <input id="display-name" name="displayName" required />
      <button disabled={pending}>Save</button>
      <p role="status">{state.message}</p>
    </form>
  );
}
```

The supplied action must enforce the server contract. `role="status"` carries a short outcome message, not a streamed page or the whole form.

## Server Actions and cache synchronization

For Next.js, load the installed version's [forms guide](https://nextjs.org/docs/app/guides/forms) and [caching guide](https://nextjs.org/docs/app/guides/caching). Exported Server Actions are reachable endpoints; treat submitted arguments and IDs as untrusted.

- Check identity and object-level permission inside each action.
- Return expected field/domain errors in a structured result; let unexpected failures reach the error boundary and server logs.
- Keep redirects outside a broad catch where the framework implements them by throwing.
- Choose path/tag/query invalidation from the actual read dependencies.
- Verify installed revalidation semantics; do not assume every cache API means immediate read-your-writes.
- Avoid private data in shared caches without an explicit identity-aware contract.
- Keep transport serialization and privacy constraints in action return values.

Revalidation changes server-side data freshness. It does not automatically erase an unrelated local store, optimistic draft, or external query cache.

## Optimistic updates

Apply optimism only when rollback or reconciliation has a defined result.

- Snapshot the previous cache value before mutation.
- Cancel an in-flight read that could overwrite the optimistic state.
- Give temporary items a stable local identity.
- On rejection, restore the prior value and preserve the draft.
- On success, replace temporary state with the authoritative response.
- Refresh affected lists/counts when the response cannot describe every dependency.
- Resolve concurrent edits using the server's revision/conflict contract.

For irreversible or high-impact operations, show the confirmed result after the server accepts it unless the product has explicitly designed safe optimistic behavior.

## Error presentation

| Contract result | UI behavior |
|---|---|
| Invalid field | Inline associated error; keep entered values |
| No session | Sign-in recovery; retain safe draft state |
| Forbidden | Explain unavailable action without leaking hidden data |
| Not found | Route/record absence state, not an infinite spinner |
| Conflict | Offer reload/reconcile using the authoritative revision |
| Rate limited | Respect documented retry information; avoid a retry loop |
| Network/server failure | Recoverable error with an explicit retry |
| Unknown response shape | Fail the operation and report a diagnostic; do not render success |

Do not display raw stack traces, database errors, tokens, or internal exception messages to the browser. Use an existing correlation ID contract when support needs to connect UI and server evidence.

## Pagination and URL state

Keep shareable filters and pages in the URL rather than duplicating them in a global store. Reset a cursor when a filter changes its result set.

- Check whether the API returns a cursor, page, or offset and preserve that contract.
- Abort obsolete requests or ignore their responses using the established query lifecycle.
- Distinguish an empty first page from the end of pagination.
- Do not assume a sort is stable without a tie-breaker defined by the API.
- Preserve browser back/forward behavior through filter and page changes.

## tRPC at the frontend boundary

Use tRPC when the repo already owns a same-language client/server contract. For public or non-TypeScript clients, load [dev-api-design](../../dev-api-design/SKILL.md) before selecting an interface.

tRPC infers compile-time client types; it does not make authorization automatic or provide runtime validation unless the procedure specifies it. Keep runtime schemas and permission checks at the server entry point.

- Import router types with type-only imports into the browser contract.
- Keep the runtime server router and database modules out of client code.
- Choose the installed tRPC/TanStack integration from its [official client docs](https://trpc.io/docs/client/tanstack-react-query/setup).
- Create request-scoped server clients and a stable browser provider lifecycle.
- Define query invalidation and mutation error mapping as for any other API.
- Test serialization of dates or non-JSON values using the configured transformer.

## Streaming and subscriptions

Streaming HTML fills a rendered document progressively. It is distinct from a live data subscription. A Suspense boundary is also insufficient as a subscription or authorization mechanism.

For live updates, route transport implementation to [software-realtime](../../software-realtime/SKILL.md) and specify:

- session renewal and authorization changes;
- reconnect/resume and duplicate-message handling;
- stale/partial UI and ordering semantics;
- unsubscribe/cleanup on navigation;
- which cache or store owns the authoritative update.

Announce concise progress/outcome text when needed; keep large streamed content outside live regions.

## Boundary verification

- Unit-test DTO parsing, field-error mapping, and URL-state transformations where they can fail.
- Component-test pending, rejected, confirmed, and expired-session UI.
- Assert invalid input and rejected authorization cause no successful mutation UI.
- Test an account switch without reusing another user's cached data.
- Test hard reload, client navigation, and back/forward with the same data contract.
- Test SSR/private cache behavior with two distinct synthetic sessions.
- Check initial HTML and hydrated DOM for matching content and useful loading states.
- Check expected errors preserve input and unexpected response shapes fail visibly.
- Use [qa-testing-playwright](../../qa-testing-playwright/SKILL.md) for deployed/browser journeys, including async RSC behavior.

## Handoff contract

Report the changed frontend behavior, read/mutation boundary, DTO or action contract, cache synchronization, and proof exercised. Name any authorization or backend behavior that needs its owning implementation verified; passing a component test does not establish service correctness.
