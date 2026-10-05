# Cookbook: Vertex Agent Engine Memory Bank

Use this when a Vertex-hosted agent stack wants managed memory, but the product
still needs app-owned truth and explicit boundary control.

## Good fit

- Google-hosted agent stacks
- User-scoped recall that benefits from managed storage
- Teams comfortable with provider-managed memory lifecycles, with local audit on top

## Boundary rule

Memory Bank can accelerate recall. It does not replace:

- operational truth
- local invalidation policy
- DSAR/delete workflow
- tenant or org scope derivation

## Wiring pattern

1. Derive `owner_scope` in the app first.
2. Map managed-memory reads into `LearnedMemory` or typed projections.
3. Record every invalidate/delete action in app-owned audit logs.
4. Keep rebuild/export assumptions documented before production rollout.

## Gotchas

- Managed memory features change faster than app contracts; revalidate before
  customer-facing claims.
- Provider delete behavior may not match your legal/audit needs.
- Scope mistakes at request construction become real incidents, not just noisy results.
