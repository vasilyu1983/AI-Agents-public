# Go + Fiber + GORM: non-default stack delta

Load this only when the team already uses Fiber and GORM or their ergonomics justify those dependencies. The default Go service scaffold, HTTP lifecycle, health checks, explicit timeouts, tests and deployment gates live in [Go + chi + sqlc + pgx](template-go-chi-sqlc-pgx.md). Do not copy its SQL access layer together with GORM into the same service.

## Choose and pin

- Check the supported Go releases at [go.dev/doc/devel/release](https://go.dev/doc/devel/release), the module's `go` directive, and the compatible Fiber and GORM majors in their official migration guides. Use one verified major throughout the scaffold. Fiber v3 uses `github.com/gofiber/fiber/v3` and handlers of shape `func(fiber.Ctx) error`; the old v2 handlers are not drop-in code.
- Select a PostgreSQL major with enough support runway using [PostgreSQL versioning](https://www.postgresql.org/support/versioning/). Do not use a fixed minimum without checking its support end date.
- Pin a supported Go builder image that matches `go.mod`; build with an explicit `GO_VERSION` argument or an organization-owned digest. Do not copy an older builder tag from archived examples.

## Fiber delta

Use [Fiber's current app and routing docs](https://docs.gofiber.io/api/app/) for route and middleware signatures. A minimal route for the current v3 docs is:

```go
app := fiber.New()
app.Get("/healthz", func(c fiber.Ctx) error {
    return c.SendStatus(fiber.StatusOK)
})
```

Retain the default scaffold's request validation, authentication boundary, problem response, correlation ID, deadlines, readiness, and graceful-shutdown tests. Check Fiber's request-context lifetime before passing request-derived values to goroutines or asynchronous work. Keep the service's transport choice explicit if standard `net/http` interoperability matters.

## GORM delta

Use [GORM's PostgreSQL connection guide](https://gorm.io/docs/connecting_to_the_database.html) to open `gorm.DB`; configure and monitor the underlying `database/sql` pool. Keep migrations as reviewed, versioned changes rather than calling `AutoMigrate` on production startup. Verify query plans for hot paths and keep a way to use explicit SQL when an ORM query hides critical behavior.

```go
// Representative transaction; Order and OutboxEvent are domain models.
err := db.Transaction(func(tx *gorm.DB) error {
    if err := tx.Create(&order).Error; err != nil { return err }
    return tx.Create(&outboxEvent).Error
})
if err != nil { return err }
```

GORM's [transaction guide](https://gorm.io/docs/transactions.html) requires every operation inside this callback to use `tx`; using `db` escapes the transaction. Treat a successful commit as the local effect only. A separate publisher may deliver the outbox event more than once; follow [leased outbox dispatch](../../references/message-queues-background-jobs.md#job-runtime-and-outbox-dispatch) and receiver deduplication.

## Verification delta

- Exercise a rollback where the second insert fails; neither the business row nor the event may commit.
- Run concurrent requests against an idempotency key and verify one local effect.
- Verify Fiber handler error mapping and request-value lifetime with the selected major.
- Compare the compiled builder/runtime architecture and CA bundle; run the default template's smoke and shutdown checks.
