# Backend Engineering - Rust + Axum + SQLx Template

*Purpose: Explicit SQL-first Rust backend for teams that want Axum ergonomics, compile-time query checking, and strong runtime discipline.*

---

# When to Use

Use this template when building:

- memory-safe REST APIs
- services with performance-sensitive database paths
- systems where explicit SQL is easier to audit than ORM-generated queries
- Rust backends with moderate to high operational rigor

Prefer this over SeaORM when explicit query review matters more than ORM convenience.

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Tech Stack:**
- [ ] Rust stable
- [ ] Axum
- [ ] SQLx
- [ ] Tokio
- [ ] PostgreSQL
- [ ] Serde
- [ ] Tracing

**Project Name:** `{{project_name}}`

---

# 2. Project Structure

```text
project-root/
|-- src/
|   |-- main.rs
|   |-- app.rs
|   |-- config.rs
|   |-- db.rs
|   |-- routes/
|   |   |-- mod.rs
|   |   |-- health.rs
|   |   `-- users.rs
|   `-- problem.rs
|-- migrations/
|   `-- 202603130001_create_users.sql
|-- Cargo.toml
`-- .env.example
```

---

# 3. Dependencies

## Cargo.toml

```toml
[package]
name = "your_api"
version = "0.1.0"
edition = "2021"

[dependencies]
anyhow = "1"
axum = "0.8"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
sqlx = { version = "0.8", features = ["runtime-tokio", "postgres", "uuid", "time"] }
tokio = { version = "1", features = ["macros", "rt-multi-thread", "signal"] }
tower = "0.5"
tower-http = { version = "0.6", features = ["trace", "timeout"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "fmt"] }
uuid = { version = "1", features = ["serde", "v4"] }
```

## .env.example

```env
APP_PORT=3000
DATABASE_URL=postgres://postgres:postgres@localhost:5432/app
RUST_LOG=info,tower_http=info
```

---

# 4. Database Layer

## migrations/202603130001_create_users.sql

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## src/db.rs

```rust
use sqlx::{postgres::PgPoolOptions, PgPool};
use std::time::Duration;

pub async fn connect(database_url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(20)
        .acquire_timeout(Duration::from_secs(5))
        .connect(database_url)
        .await
}
```

---

# 5. HTTP Layer

## src/problem.rs

```rust
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde::Serialize;

#[derive(Serialize)]
pub struct ProblemDetails<'a> {
    pub r#type: &'a str,
    pub title: &'a str,
    pub status: u16,
    pub detail: &'a str,
    pub instance: &'a str,
}

pub fn problem(
    status: StatusCode,
    typ: &'static str,
    title: &'static str,
    detail: &'static str,
    instance: &str,
) -> Response {
    (
        status,
        [("content-type", "application/problem+json")],
        Json(ProblemDetails {
            r#type: typ,
            title,
            status: status.as_u16(),
            detail,
            instance,
        }),
    )
        .into_response()
}
```

## src/routes/users.rs

```rust
use axum::{extract::State, http::StatusCode, response::IntoResponse, routing::{get, post}, Json, Router};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use uuid::Uuid;

use crate::problem::problem;

#[derive(Clone)]
pub struct AppState {
    pub db: PgPool,
}

#[derive(Deserialize)]
pub struct CreateUserRequest {
    pub email: String,
    pub full_name: String,
}

#[derive(Serialize)]
pub struct UserDto {
    pub id: Uuid,
    pub email: String,
    pub full_name: String,
}

pub fn routes(state: AppState) -> Router {
    Router::new()
        .route("/users", get(list_users).post(create_user))
        .with_state(state)
}

async fn list_users(State(state): State<AppState>) -> Result<Json<Vec<UserDto>>, impl IntoResponse> {
    let rows = sqlx::query_as!(
        UserDto,
        r#"SELECT id, email, full_name FROM users ORDER BY created_at DESC"#
    )
    .fetch_all(&state.db)
    .await
    .map_err(|_| problem(StatusCode::INTERNAL_SERVER_ERROR, "https://api.example.com/problems/internal", "Internal Server Error", "Failed to list users.", "/users"))?;

    Ok(Json(rows))
}

async fn create_user(
    State(state): State<AppState>,
    Json(input): Json<CreateUserRequest>,
) -> Result<impl IntoResponse, impl IntoResponse> {
    let row = sqlx::query_as!(
        UserDto,
        r#"
        INSERT INTO users (id, email, full_name)
        VALUES ($1, $2, $3)
        RETURNING id, email, full_name
        "#,
        Uuid::new_v4(),
        input.email,
        input.full_name
    )
    .fetch_one(&state.db)
    .await
    .map_err(|_| problem(StatusCode::CONFLICT, "https://api.example.com/problems/email-conflict", "Conflict", "A user with this email already exists.", "/users"))?;

    Ok((StatusCode::CREATED, Json(row)))
}
```

## src/routes/health.rs

```rust
use axum::{routing::get, Json, Router};
use serde_json::json;

pub fn routes() -> Router {
    Router::new().route("/health/live", get(|| async { Json(json!({ "status": "ok" })) }))
}
```

## src/routes/mod.rs

```rust
pub mod health;
pub mod users;
```

## src/app.rs

```rust
use axum::Router;
use tower_http::{timeout::TimeoutLayer, trace::TraceLayer};
use std::time::Duration;

use crate::routes::{health, users::{self, AppState}};

pub fn build_app(state: AppState) -> Router {
    Router::new()
        .merge(health::routes())
        .merge(users::routes(state))
        .layer(TraceLayer::new_for_http())
        .layer(TimeoutLayer::new(Duration::from_secs(30)))
}
```

## src/main.rs

```rust
mod app;
mod config;
mod db;
mod problem;
mod routes;

use std::net::SocketAddr;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use crate::routes::users::AppState;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::from_default_env())
        .with(tracing_subscriber::fmt::layer())
        .init();

    let settings = config::Settings::from_env()?;
    let db = db::connect(&settings.database_url).await?;
    let app = app::build_app(AppState { db });

    let addr = SocketAddr::from(([0, 0, 0, 0], settings.port));
    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;
    Ok(())
}
```

## src/config.rs

```rust
pub struct Settings {
    pub port: u16,
    pub database_url: String,
}

impl Settings {
    pub fn from_env() -> Result<Self, std::env::VarError> {
        let port = std::env::var("APP_PORT")
            .ok()
            .and_then(|value| value.parse().ok())
            .unwrap_or(3000);

        Ok(Self {
            port,
            database_url: std::env::var("DATABASE_URL")?,
        })
    }
}
```

---

# 6. Operational Notes

- Use SQLx offline preparation or CI query checking before deployment.
- Keep RFC 9457 error responses consistent across all handlers.
- Add auth and rate limiting before exposing mutating routes publicly.
- Prefer `tracing` spans with request IDs on all DB-backed endpoints.

---

# END

**Next Steps**
1. Run migrations.
2. Set `DATABASE_URL`.
3. Start the service with `cargo run`.
4. Add tests, auth, and OpenTelemetry before production.
