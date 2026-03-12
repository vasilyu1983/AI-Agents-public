# Rust Backend Best Practices

Comprehensive guide for building ultra-high-performance, memory-safe backend services with Rust.

## Contents

- [Ownership & Borrowing](#ownership--borrowing)
- [Error Handling](#error-handling)
- [Async/Await Patterns](#asyncawait-patterns)
- [Type System Patterns](#type-system-patterns)
- [Performance Optimization](#performance-optimization)
- [Axum Web Framework Patterns](#axum-web-framework-patterns)
- [Database Patterns with SeaORM](#database-patterns-with-seaorm)
- [Testing Best Practices](#testing-best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Deployment Patterns](#deployment-patterns)
- [Resources](#resources)

---

## Ownership & Borrowing

### Core Ownership Rules

**Rule 1: Each value has exactly one owner**
```rust
let s1 = String::from("hello");
let s2 = s1; // s1 is moved to s2, s1 is no longer valid

// println!("{}", s1); // Compile error: value borrowed after move
println!("{}", s2); // OK
```

**Rule 2: Borrowing doesn't transfer ownership**
```rust
fn calculate_length(s: &String) -> usize {
    s.len()
} // s goes out of scope, but nothing happens (it doesn't own the data)

let s1 = String::from("hello");
let len = calculate_length(&s1); // Borrow s1
println!("Length of '{}' is {}", s1, len); // s1 still valid
```

**Rule 3: Mutable references are exclusive**
```rust
let mut s = String::from("hello");

let r1 = &mut s;
// let r2 = &mut s; // Compile error: cannot borrow `s` as mutable more than once

r1.push_str(", world");
println!("{}", r1);
```

### Common Borrowing Patterns

**Split Borrows**
```rust
struct Data {
    field1: Vec<i32>,
    field2: Vec<i32>,
}

impl Data {
    // Good: Borrow different fields separately
    fn process(&mut self) {
        self.process_field1(&mut self.field1);
        self.process_field2(&mut self.field2);
    }

    fn process_field1(&self, field: &mut Vec<i32>) {
        field.push(1);
    }

    fn process_field2(&self, field: &mut Vec<i32>) {
        field.push(2);
    }
}
```

**Interior Mutability**
```rust
use std::cell::RefCell;
use std::rc::Rc;

struct Database {
    cache: RefCell<HashMap<String, String>>,
}

impl Database {
    fn get(&self, key: &str) -> Option<String> {
        // Can mutate cache even with immutable self reference
        let mut cache = self.cache.borrow_mut();
        cache.get(key).cloned()
    }
}
```

---

## Error Handling

### Result Type Pattern

```rust
#[derive(Debug)]
enum AppError {
    Database(String),
    NotFound(String),
    Validation(String),
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AppError::Database(msg) => write!(f, "Database error: {}", msg),
            AppError::NotFound(msg) => write!(f, "Not found: {}", msg),
            AppError::Validation(msg) => write!(f, "Validation error: {}", msg),
        }
    }
}

impl std::error::Error for AppError {}

// Convert from other error types
impl From<sqlx::Error> for AppError {
    fn from(err: sqlx::Error) -> Self {
        AppError::Database(err.to_string())
    }
}

// Usage
fn get_user(id: i32) -> Result<User, AppError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_one(&pool)
        .await?; // ? operator auto-converts errors

    Ok(user)
}
```

### The ? Operator

```rust
// Without ?
fn read_username() -> Result<String, io::Error> {
    let mut f = match File::open("username.txt") {
        Ok(file) => file,
        Err(e) => return Err(e),
    };

    let mut s = String::new();
    match f.read_to_string(&mut s) {
        Ok(_) => Ok(s),
        Err(e) => Err(e),
    }
}

// With ?
fn read_username() -> Result<String, io::Error> {
    let mut f = File::open("username.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}

// Even shorter with chaining
fn read_username() -> Result<String, io::Error> {
    let mut s = String::new();
    File::open("username.txt")?.read_to_string(&mut s)?;
    Ok(s)
}
```

### Custom Error Types with thiserror

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ApiError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Validation failed: {field}: {message}")]
    Validation { field: String, message: String },

    #[error("Unauthorized")]
    Unauthorized,
}

impl From<ApiError> for axum::http::StatusCode {
    fn from(err: ApiError) -> Self {
        match err {
            ApiError::Database(_) => StatusCode::INTERNAL_SERVER_ERROR,
            ApiError::NotFound(_) => StatusCode::NOT_FOUND,
            ApiError::Validation { .. } => StatusCode::BAD_REQUEST,
            ApiError::Unauthorized => StatusCode::UNAUTHORIZED,
        }
    }
}
```

---

## Async/Await Patterns

### Basic Async Functions

```rust
async fn fetch_user(id: i32) -> Result<User, Error> {
    let user = sqlx::query_as!(
        User,
        "SELECT * FROM users WHERE id = $1",
        id
    )
    .fetch_one(&pool)
    .await?;

    Ok(user)
}

// Calling async functions
#[tokio::main]
async fn main() {
    let user = fetch_user(1).await.unwrap();
    println!("User: {:?}", user);
}
```

### Concurrent Operations

```rust
use tokio::join;

async fn fetch_multiple_users(ids: Vec<i32>) -> Result<Vec<User>, Error> {
    let futures: Vec<_> = ids
        .into_iter()
        .map(|id| fetch_user(id))
        .collect();

    // Wait for all futures concurrently
    let results = futures::future::try_join_all(futures).await?;
    Ok(results)
}

// Or using tokio::spawn for true parallelism
async fn fetch_parallel(ids: Vec<i32>) -> Result<Vec<User>, Error> {
    let handles: Vec<_> = ids
        .into_iter()
        .map(|id| tokio::spawn(fetch_user(id)))
        .collect();

    let mut users = Vec::new();
    for handle in handles {
        users.push(handle.await??); // Note double ??
    }
    Ok(users)
}
```

### Select Pattern

```rust
use tokio::select;
use tokio::time::{sleep, Duration};

async fn fetch_with_timeout(id: i32) -> Result<User, Error> {
    select! {
        user = fetch_user(id) => user,
        _ = sleep(Duration::from_secs(5)) => Err(Error::Timeout),
    }
}
```

### Channels for Communication

```rust
use tokio::sync::mpsc;

async fn producer(tx: mpsc::Sender<i32>) {
    for i in 0..10 {
        tx.send(i).await.unwrap();
        sleep(Duration::from_millis(100)).await;
    }
}

async fn consumer(mut rx: mpsc::Receiver<i32>) {
    while let Some(value) = rx.recv().await {
        println!("Received: {}", value);
    }
}

#[tokio::main]
async fn main() {
    let (tx, rx) = mpsc::channel(32);

    tokio::spawn(producer(tx));
    tokio::spawn(consumer(rx)).await.unwrap();
}
```

---

## Type System Patterns

### Newtype Pattern

```rust
// Wrap primitive types for type safety
struct UserId(i32);
struct OrderId(i32);

// Compiler prevents mixing up IDs
fn get_user(id: UserId) -> User { /* ... */ }
fn get_order(id: OrderId) -> Order { /* ... */ }

// let user = get_user(OrderId(1)); // Compile error!
```

### Type State Pattern

```rust
// Encode states in the type system
struct Locked;
struct Unlocked;

struct Door<State> {
    _state: PhantomData<State>,
}

impl Door<Locked> {
    fn unlock(self) -> Door<Unlocked> {
        println!("Door unlocked");
        Door { _state: PhantomData }
    }
}

impl Door<Unlocked> {
    fn open(&self) {
        println!("Door opened");
    }

    fn lock(self) -> Door<Locked> {
        println!("Door locked");
        Door { _state: PhantomData }
    }
}

// Usage
let door = Door::<Locked> { _state: PhantomData };
// door.open(); // Compile error: method not available for Locked state
let door = door.unlock();
door.open(); // OK
```

### Builder Pattern

```rust
#[derive(Default)]
struct UserBuilder {
    email: Option<String>,
    name: Option<String>,
    age: Option<u32>,
}

impl UserBuilder {
    fn email(mut self, email: impl Into<String>) -> Self {
        self.email = Some(email.into());
        self
    }

    fn name(mut self, name: impl Into<String>) -> Self {
        self.name = Some(name.into());
        self
    }

    fn age(mut self, age: u32) -> Self {
        self.age = Some(age);
        self
    }

    fn build(self) -> Result<User, &'static str> {
        Ok(User {
            email: self.email.ok_or("email is required")?,
            name: self.name.ok_or("name is required")?,
            age: self.age.unwrap_or(0),
        })
    }
}

// Usage
let user = UserBuilder::default()
    .email("test@example.com")
    .name("Test User")
    .age(25)
    .build()?;
```

---

## Performance Optimization

### Zero-Cost Abstractions

```rust
// This high-level code:
let sum: i32 = (0..1000).filter(|x| x % 2 == 0).sum();

// Compiles to the same machine code as:
let mut sum = 0;
for i in 0..1000 {
    if i % 2 == 0 {
        sum += i;
    }
}
```

### Avoid Unnecessary Clones

```rust
// Bad: Unnecessary clones
fn process_string(s: String) -> String {
    s.to_uppercase()
}

let original = String::from("hello");
let processed = process_string(original.clone()); // Clone not needed!

// Good: Take ownership or borrow
fn process_string(s: &str) -> String {
    s.to_uppercase()
}

let original = String::from("hello");
let processed = process_string(&original); // Borrow only
```

### Use Cow for Conditional Cloning

```rust
use std::borrow::Cow;

fn process(input: &str) -> Cow<str> {
    if input.contains("special") {
        Cow::Owned(input.replace("special", "SPECIAL"))
    } else {
        Cow::Borrowed(input) // No allocation!
    }
}
```

### SmallVec for Stack Allocation

```rust
use smallvec::SmallVec;

// Store up to 4 items on stack, heap after that
let mut vec: SmallVec<[i32; 4]> = SmallVec::new();
vec.push(1);
vec.push(2);
vec.push(3);
// Still on stack!

vec.push(4);
vec.push(5);
// Now heap-allocated
```

---

## Axum Web Framework Patterns

### Handler Functions

```rust
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
    response::IntoResponse,
};

// Path parameters
async fn get_user(
    Path(id): Path<i32>,
    State(db): State<DatabasePool>,
) -> Result<Json<User>, StatusCode> {
    let user = fetch_user(&db, id).await
        .map_err(|_| StatusCode::NOT_FOUND)?;

    Ok(Json(user))
}

// Query parameters
#[derive(Deserialize)]
struct Pagination {
    page: Option<u32>,
    per_page: Option<u32>,
}

async fn list_users(
    Query(pagination): Query<Pagination>,
    State(db): State<DatabasePool>,
) -> Json<Vec<User>> {
    let page = pagination.page.unwrap_or(1);
    let per_page = pagination.per_page.unwrap_or(20);

    let users = fetch_users_paginated(&db, page, per_page).await;
    Json(users)
}

// JSON body
async fn create_user(
    State(db): State<DatabasePool>,
    Json(payload): Json<CreateUserRequest>,
) -> Result<Json<User>, StatusCode> {
    let user = insert_user(&db, payload).await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(user))
}
```

### Middleware

```rust
use axum::{
    middleware::{self, Next},
    http::Request,
    response::Response,
};

async fn auth_middleware<B>(
    req: Request<B>,
    next: Next<B>,
) -> Result<Response, StatusCode> {
    let auth_header = req.headers()
        .get("Authorization")
        .and_then(|h| h.to_str().ok());

    match auth_header {
        Some(token) if validate_token(token) => Ok(next.run(req).await),
        _ => Err(StatusCode::UNAUTHORIZED),
    }
}

// Apply middleware
let app = Router::new()
    .route("/protected", get(protected_handler))
    .layer(middleware::from_fn(auth_middleware));
```

### Error Handling

```rust
use axum::{
    response::{IntoResponse, Response},
    http::StatusCode,
    Json,
};

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            ApiError::NotFound(msg) => (StatusCode::NOT_FOUND, msg),
            ApiError::Unauthorized => (StatusCode::UNAUTHORIZED, "Unauthorized".to_string()),
            ApiError::Validation { field, message } => {
                (StatusCode::BAD_REQUEST, format!("{}: {}", field, message))
            }
            ApiError::Database(_) => {
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error".to_string())
            }
        };

        (status, Json(serde_json::json!({
            "error": message
        }))).into_response()
    }
}
```

---

## Database Patterns with SeaORM

### Query Builder

```rust
use sea_orm::{entity::*, query::*};

// Select with conditions
let users: Vec<user::Model> = User::find()
    .filter(user::Column::Age.gte(18))
    .filter(user::Column::Active.eq(true))
    .order_by_asc(user::Column::Name)
    .limit(10)
    .all(&db)
    .await?;

// Join queries
let posts_with_users = Post::find()
    .find_also_related(User)
    .all(&db)
    .await?;

// Aggregate functions
let count: i64 = User::find()
    .filter(user::Column::Age.gte(18))
    .count(&db)
    .await?;
```

### Transactions

```rust
use sea_orm::TransactionTrait;

async fn transfer_funds(
    db: &DatabaseConnection,
    from_id: i32,
    to_id: i32,
    amount: i32,
) -> Result<(), DbErr> {
    let txn = db.begin().await?;

    // Withdraw
    let from_account = Account::find_by_id(from_id)
        .one(&txn)
        .await?
        .ok_or(DbErr::Custom("Account not found".to_string()))?;

    let mut from_active: account::ActiveModel = from_account.into();
    from_active.balance = Set(from_active.balance.unwrap() - amount);
    from_active.update(&txn).await?;

    // Deposit
    let to_account = Account::find_by_id(to_id)
        .one(&txn)
        .await?
        .ok_or(DbErr::Custom("Account not found".to_string()))?;

    let mut to_active: account::ActiveModel = to_account.into();
    to_active.balance = Set(to_active.balance.unwrap() + amount);
    to_active.update(&txn).await?;

    txn.commit().await?;
    Ok(())
}
```

---

## Testing Best Practices

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_user_validation() {
        let user = User {
            email: "test@example.com".to_string(),
            name: "Test".to_string(),
            age: 25,
        };

        assert!(user.is_valid());
    }

    #[test]
    #[should_panic(expected = "email is required")]
    fn test_invalid_user() {
        let user = User {
            email: "".to_string(),
            name: "Test".to_string(),
            age: 25,
        };

        user.validate().unwrap();
    }
}
```

### Async Tests

```rust
#[tokio::test]
async fn test_fetch_user() {
    let pool = create_test_pool().await;
    let user = fetch_user(&pool, 1).await.unwrap();
    assert_eq!(user.id, 1);
}

#[tokio::test]
async fn test_concurrent_operations() {
    let results = tokio::join!(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    );

    assert!(results.0.is_ok());
    assert!(results.1.is_ok());
    assert!(results.2.is_ok());
}
```

### Property-Based Testing

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_parse_email(email in "[a-z]+@[a-z]+\\.[a-z]+") {
        assert!(validate_email(&email));
    }

    #[test]
    fn test_no_overflow(a in 0..i32::MAX, b in 0..i32::MAX) {
        let result = a.checked_add(b);
        prop_assert!(result.is_some() || a + b < 0);
    }
}
```

---

## Common Pitfalls

### Lifetime Elision Confusion

```rust
// Bad: Unclear lifetimes
fn get_first<'a>(s: &'a str, _other: &'a str) -> &'a str {
    s.split_whitespace().next().unwrap()
}

// Good: Explicit when needed
fn get_first<'a, 'b>(s: &'a str, _other: &'b str) -> &'a str {
    s.split_whitespace().next().unwrap()
}
```

### Moving Out of Borrowed Content

```rust
struct Container {
    items: Vec<String>,
}

impl Container {
    // Bad: Can't move out of borrowed content
    fn get_first(&self) -> String {
        // self.items[0] // Error: cannot move out of borrowed content
        self.items[0].clone() // Must clone
    }

    // Better: Return reference
    fn get_first(&self) -> &str {
        &self.items[0]
    }
}
```

### Incorrect Arc Usage

```rust
use std::sync::Arc;

// Bad: Arc inside Arc
let data = Arc::new(Arc::new(vec![1, 2, 3]));

// Good: Single Arc
let data = Arc::new(vec![1, 2, 3]);

// Thread-safe sharing
let data1 = Arc::clone(&data);
let handle = tokio::spawn(async move {
    println!("{:?}", data1);
});
```

---

## Deployment Patterns

### Binary Size Optimization

```toml
[profile.release]
opt-level = "z"     # Optimize for size
lto = true          # Enable Link Time Optimization
codegen-units = 1   # Better optimization
strip = true        # Strip symbols from binary
```

### Cross-Compilation

```bash
# Install target
rustup target add x86_64-unknown-linux-musl

# Build for musl (static linking)
cargo build --release --target x86_64-unknown-linux-musl

# Result: Fully static binary with no dependencies
```

### Graceful Shutdown

```rust
use tokio::signal;

#[tokio::main]
async fn main() {
    let app = create_app();

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080")
        .await
        .unwrap();

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .unwrap();
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }

    println!("Signal received, starting graceful shutdown");
}
```

---

## Resources

- [The Rust Programming Language Book](https://doc.rust-lang.org/book/)
- [Rust By Example](https://doc.rust-lang.org/rust-by-example/)
- [Tokio Tutorial](https://tokio.rs/tokio/tutorial)
- [Axum Documentation](https://docs.rs/axum/latest/axum/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Too Many Lists](https://rust-unofficial.github.io/too-many-lists/)
