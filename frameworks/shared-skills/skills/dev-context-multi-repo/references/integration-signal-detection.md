# Integration Signal Detection

Look for these signal classes:

- dependency manifests
- environment variable names
- API specs
- webhook handlers
- queue/topic names
- infrastructure config
- vendor SDK package names
- CI/CD deploy steps
- **database schema artifacts** (see below)
- **ORM/data-access registrations** (see below)

### Database & Storage Signal Detection

Storage engine detection is a common source of errors — the documented storage type often drifts from the actual driver in code. Always verify the **actual driver package** in dependency manifests rather than trusting documentation headers.

| Signal | File Pattern | What It Reveals |
|--------|-------------|-----------------|
| EF Core DbContext | `*DbContext.cs`, `*Context.cs` | SQL tables (DbSet properties), relationships, concurrency tokens |
| MongoDB Registry | `*MongoRegistry.cs`, `*MongoDbRegistry.cs` | Collection names, document types, indexes |
| SQL Migrations | `db/sql/migrations/*.sql`, `database/sql/Migrations/*.sql` | Table DDL, column types, constraints, migration timeline |
| InitSchema file | `*InitSchema*.sql`, `*Init_Schema*.sql`, `*initial_ddl*.sql` | Clean baseline schema (most valuable single file) |
| Npgsql in .csproj | `<PackageReference Include="Npgsql...">` | **PostgreSQL** (not SQL Server, even if docs say SQL Server) |
| SqlClient in .csproj | `<PackageReference Include="*SqlClient*">` | SQL Server confirmed |
| MongoDB driver in .csproj | `<PackageReference Include="MongoDB*">` | MongoDB confirmed |
| Connection strings | `appsettings*.json`, vault references | Database names, servers, connection pooling |
| Entity mapping files | `*Map.cs`, `*Configuration.cs`, `*EntityTypeConfiguration.cs` | Column mappings, FK constraints, indexes |
| Dapper usage | `IDbConnectionFactory`, raw SQL queries | SQL access without EF Core (Dapper pattern) |

### Cross-Service Data Flow Signals

Beyond storage, detect **how data flows between services**:

| Signal | File Pattern | What It Reveals |
|--------|-------------|-----------------|
| Kafka producers/consumers | `*Kafka*` projects, `IKafkaProducer`, `KafkaConsumerHandler` | Async data flow between services |
| RabbitMQ handlers | `*RabbitMq*` projects, `IBus`, `IMessageHandler` | Event-driven data flow |
| Protobuf contracts | `*.proto` files, `*Contracts*` projects | Typed message schemas |
| NuGet API clients | `*.PrivateApi.Client` packages | Synchronous service-to-service calls |
| ETL/CDC consumers | `Acme.Infrastructure.Etl.*`, CDC event handlers | Change data capture feeds |
| State machine files | `*StateMachine*`, `Stateless` library usage | Entity lifecycle state transitions |

Emit a `SystemEdge` only when there is at least one concrete artifact or two weaker corroborating signals.

Do not upgrade edge-level evidence into portfolio-wide topology claims unless every sibling edge in scope was checked. Central diagrams, dependency matrices, and messaging summaries must preserve verification scope from the underlying edges and label gaps as `subset-verified`, `inferred`, or `unverified`.

