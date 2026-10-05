# Security And Ownership Models

Treat the security model as part of the platform decision.

## Platform Security Lens

| Platform | Primary security boundary | Default question |
|----------|---------------------------|------------------|
| Supabase | Postgres RLS + publishable/secret key separation (legacy `anon`/`service_role` keys deprecated by end-2026) | Are the table policies correct for every read and write path? |
| Convex | Server function boundaries + auth context | Which writes are client-triggered but server-authorized? |
| Firebase / Firestore | Security rules + client SDK trust boundary | Can the rules be understood and tested for every collection path? |
| Appwrite | Project permissions + server/admin surface | Which credentials stay server-side and which operations are client-safe? |
| PocketBase | App-level auth plus operational isolation around a small runtime | Is this deployment simple enough that the admin surface and secrets stay tightly controlled? |
| PlanetScale Postgres / Neon database-only | Database roles, grants, and optional RLS; application auth is a separate choice | Who connects as which database role, and can a privileged connection bypass tenant policies? |
| Neon backend primitives | Managed Better Auth plus the authorization boundary of each selected service | How are user/tenant identities propagated into database, functions, and object-storage checks? |

## Decision Rules

- If the team cannot explain row- or document-level permissions clearly, stop and design the security model before choosing the platform.
- If many actions must stay server-owned, prefer platforms with explicit server function boundaries over client-heavy permission rules alone.
- If secrets, admin APIs, or privileged jobs need strong isolation, keep them in a private server context or separate service, not in the client app.
- If the platform choice forces security logic into a model the team does not understand, it is the wrong platform.

## Common Mistakes

- Treating auth and authorization as the same problem.
- Choosing a platform for speed while deferring the permission model.
- Assuming realtime implies safe client reads.
- Letting storage or background jobs bypass the same ownership rules used by core records.
