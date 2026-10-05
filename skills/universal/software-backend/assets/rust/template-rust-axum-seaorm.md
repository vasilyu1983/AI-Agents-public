# Rust + Axum + SeaORM: non-default stack delta

Load this when the service already uses SeaORM or its entity and relation model is worth an ORM layer. The default Axum service structure, transport errors, lifecycle, health checks, SQL migration discipline and deployment checks live in [Rust + Axum + SQLx](template-rust-axum-sqlx.md). Do not combine its SQLx repository sample with a second SeaORM repository for the same table.

## Choose and pin

- Read the current [SeaORM documentation](https://www.sea-ql.org/SeaORM/docs/index/) and select one compatible SeaORM, SQLx, Axum, Tokio and Rust toolchain set. Pin the chosen compatible versions in `Cargo.lock` and verify MSRV before building.
- SeaORM 2 changed entity generation and added a dense model format. An older entity or migration snippet must be checked against the selected version's [entity generation guide](https://www.sea-ql.org/SeaORM/docs/generate-entity/sea-orm-cli/) before use. Do not mix SeaORM 1 entities and SeaORM 2 examples by default.
- Select a supported PostgreSQL major with enough runway from [PostgreSQL versioning](https://www.postgresql.org/support/versioning/); keep its minor release current.

## SeaORM delta

Connect with `Database::connect` and pass the shared `DatabaseConnection` or a reference through Axum state. The connection wraps a pool for PostgreSQL; size it against the service's concurrency and database limits. Define or generate entities against reviewed migrations. Do not rely on startup schema sync for production rollout.

For a SeaORM 2 dense entity, start from the selected version's generated form, for example:

```rust
use sea_orm::entity::prelude::*;

#[sea_orm::model]
#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel)]
#[sea_orm(table_name = "orders")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    pub status: String,
}
impl ActiveModelBehavior for ActiveModel {}
```

For a multi-write operation, use SeaORM's `TransactionTrait::transaction` or an explicit transaction. Pass the transaction handle to every query and mutation; a call on the original pool is outside the unit of work. SeaORM's [transaction API](https://docs.rs/sea-orm/latest/sea_orm/struct.DatabaseTransaction.html) documents commit on success and rollback on error for the callback form. Keep an outbox row in the same transaction when publication follows a business write.

When mapping an entity to an API response, select only required columns and handle not-found, uniqueness and database errors explicitly. Use the current [entity guide](https://www.sea-ql.org/SeaORM/docs/generate-entity/newtype/) for model macros and relations; old generated examples may use a different format. Verify the generated SQL and query plan for hot reads.

## Verification delta

- Test rollback after a second write fails; verify no business row or outbox row remains.
- Test concurrent key reuse and receiver deduplication for retried mutations.
- Exercise migration up/down or forward-only rollback according to the repository policy against the selected PostgreSQL major.
- Run `cargo test` and the default SQLx template's transport, readiness and shutdown checks, adapting repository assertions to SeaORM.
