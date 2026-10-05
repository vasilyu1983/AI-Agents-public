# Migration And Exit Strategies

Every platform choice should include an exit story before the first production dependency becomes sticky.

## Exit Signals

- The platform's natural data model now fights the product.
- Security rules or policies are hard to audit.
- One workflow needs bespoke scaling or operational SLOs.
- Scheduled jobs, file handling, or privileged writes have outgrown the platform boundary.
- The team needs portability across multiple services or vendors.

## Practical Exit Paths

| Starting point | Common exit path |
|----------------|------------------|
| Supabase | Keep Postgres, move auth- or workflow-heavy paths into custom backend services first. The database itself is the most portable layer — `pg_dump`/`pg_restore` to a plain Postgres host (RDS, Neon, PlanetScale Postgres, self-hosted) is the well-trodden path; auth, storage, and RLS policies do not move automatically and need their own migration plan |
| Convex | Keep product surface stable, move the heaviest workflow or integration boundaries into external services incrementally |
| Firebase / Firestore | First check SQL Connect or Firestore Enterprise Native/Pipeline versus MongoDB compatibility in [platform-comparison.md](platform-comparison.md); if they do not fit, move the highest-value bounded context into a custom API/datastore |
| Appwrite | Peel off critical services one domain at a time while keeping Appwrite for less-sensitive product surfaces |
| PocketBase | Promote hot paths into a dedicated backend early rather than stretching the single-binary model too far |

## Default Rule

Do not migrate the whole platform at once unless the product is still very early. Migrate the tightest pain point first: auth boundary, write path, scheduled workflow, or reporting domain.

## Auth Export Proof

- Keep a stable application identity and map provider UIDs, tenant membership, and linked identities to it. Rewriting auth UIDs can orphan application rows.
- Inventory password hash algorithm, salt, and algorithm parameters; verify both export permission and the destination's exact import support. Firebase user listing omits password hashes/salts without `firebaseauth.configs.getHashConfig`. Missing or incompatible hashes require an explicit reset or staged migration plan, not a claim that passwords moved.
- Export provider links and verified-email state separately. OAuth client IDs/secrets and registered redirect URIs belong to the provider configuration; preserve or recreate them deliberately and test each sign-in provider. Never assume an exported user can be relinked solely by matching email.
- Inventory MFA factors, recovery methods, passkeys, and enrollment metadata. Verify destination transfer support; if a factor cannot move, plan secure re-enrollment and prove it on test identities.
- Sessions, refresh tokens, and signing keys are a separate migration surface. Test revocation and cutover behavior; account import does not preserve active sessions automatically.
- Prove password login, OAuth linking, MFA, recovery, tenant isolation, and stable-ID joins on synthetic accounts before cutover. Paginate exports and reconcile counts; store credential exports only in approved protected storage.

Primary checks: [Firebase user export permissions](https://firebase.google.com/docs/auth/admin/manage-users), [Firebase hash import formats](https://firebase.google.com/docs/auth/admin/import-users), and [Supabase's migration guidance](https://supabase.com/docs/guides/platform/migrating-to-supabase/auth0). Consult the source and destination provider's equivalent guides for each actual migration.
