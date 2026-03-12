# C# Backend Best Practices

Comprehensive guide for building production-grade backend services with C# 14 / .NET 10 (LTS) and ASP.NET Core 10.

> **Target platform**: .NET 10 LTS (released November 2025, supported through November 2028). C# 14 language features require .NET 10 SDK.

## Contents

- [Core C# Principles](#core-c-principles)
- [C# 14 Features](#c-14-features)
- [Async Patterns](#async-patterns)
- [Error Handling](#error-handling)
- [HTTP Server Best Practices](#http-server-best-practices)
- [Database Patterns](#database-patterns)
- [Dependency Injection](#dependency-injection)
- [Caching Patterns](#caching-patterns)
- [Resilience Patterns](#resilience-patterns)
- [Performance Optimization](#performance-optimization)
- [Testing Best Practices](#testing-best-practices)
- [Logging Best Practices](#logging-best-practices)
- [Configuration Management](#configuration-management)
- [Security Best Practices](#security-best-practices)
- [Deployment Patterns](#deployment-patterns)
- [Common Pitfalls](#common-pitfalls)
- [Resources](#resources)

---

## Core C# Principles

### Modern C# Idioms (C# 12–14)

**Prefer Records for DTOs and Value Objects**
```csharp
// Good: Immutable record with value equality
public record UserDto(int Id, string Email, string FullName);

public record CreateUserRequest(
    string Email,
    string Password,
    string FullName);

// Good: Record struct for small value types (no heap allocation)
public readonly record struct Money(decimal Amount, string Currency);

// Avoid: Mutable class for data transfer
public class UserDto
{
    public int Id { get; set; }
    public string Email { get; set; } = "";
}
```

**Use Pattern Matching**
```csharp
// Good: Switch expression with pattern matching
public string GetStatusMessage(OrderStatus status) => status switch
{
    OrderStatus.Pending => "Your order is being processed",
    OrderStatus.Shipped => "Your order is on the way",
    OrderStatus.Delivered => "Your order has been delivered",
    OrderStatus.Cancelled => "Your order was cancelled",
    _ => throw new ArgumentOutOfRangeException(nameof(status))
};

// Good: Property pattern
public decimal CalculateDiscount(Customer customer) => customer switch
{
    { IsPremium: true, OrderCount: > 100 } => 0.20m,
    { IsPremium: true } => 0.10m,
    { OrderCount: > 50 } => 0.05m,
    _ => 0m
};
```

**Nullable Reference Types (NRT)**
```csharp
// Enable in .csproj: <Nullable>enable</Nullable>

// Good: Explicit nullability
public User? FindByEmail(string email) { /* ... */ }

public string GetDisplayName(User? user)
{
    return user?.FullName ?? "Anonymous";
}

// Avoid: Ignoring nullability warnings with !
var name = user!.Name; // Suppresses warning but hides bugs
```

**Primary Constructors (C# 12)**
```csharp
// Good: Concise DI with primary constructors
public class UserService(
    IUserRepository userRepository,
    ILogger<UserService> logger)
{
    public async Task<User?> GetByIdAsync(int id)
    {
        logger.LogInformation("Fetching user {UserId}", id);
        return await userRepository.GetByIdAsync(id);
    }
}
```

**Collection Expressions (C# 12)**
```csharp
// Good: Clean collection initialization
int[] numbers = [1, 2, 3, 4, 5];
List<string> names = ["Alice", "Bob", "Charlie"];
ReadOnlySpan<byte> bytes = [0x00, 0xFF];

// Spread operator
int[] first = [1, 2, 3];
int[] second = [4, 5, 6];
int[] combined = [..first, ..second]; // [1, 2, 3, 4, 5, 6]
```

---

## C# 14 Features

> These features require .NET 10 SDK. They are the latest language additions as of February 2026.

### Extension Members

C# 14 replaces the old `static class` extension method syntax with dedicated `extension` blocks. You can now define extension properties, static extension methods, and even extension operators.

```csharp
public static class EnumerableExtensions
{
    extension<T>(IEnumerable<T> source)
    {
        // Extension property (new in C# 14)
        public bool IsEmpty => !source.Any();

        // Extension method
        public IEnumerable<T> WhereNotNull() =>
            source.Where(item => item is not null);
    }

    extension<T>(IEnumerable<T>)
    {
        // Static extension method
        public static IEnumerable<T> Empty => Enumerable.Empty<T>();
    }
}

// Usage - feels like a native member
var empty = orders.IsEmpty;
var valid = orders.WhereNotNull();
```

### The `field` Keyword

Semi-auto properties — write a custom accessor body while referencing the compiler-generated backing field with `field`. Eliminates boilerplate for validation logic.

```csharp
// Before C# 14: explicit backing field required
private string _email;
public string Email
{
    get => _email;
    set => _email = value?.Trim().ToLowerInvariant()
        ?? throw new ArgumentNullException(nameof(value));
}

// C# 14: field keyword — no manual backing field
public string Email
{
    get;
    set => field = value?.Trim().ToLowerInvariant()
        ?? throw new ArgumentNullException(nameof(value));
}

// Works with init-only too
public decimal Price
{
    get;
    init => field = value >= 0 ? value
        : throw new ArgumentOutOfRangeException(nameof(value));
}
```

### Null-Conditional Assignment

The `?.` and `?[]` operators now work on the left side of assignments. The right side is only evaluated when the left side is not null.

```csharp
// Before C# 14
if (customer is not null)
{
    customer.LastOrderDate = DateTime.UtcNow;
}

// C# 14 — concise null-conditional assignment
customer?.LastOrderDate = DateTime.UtcNow;

// Works with compound assignment
customer?.Points += 10;
customer?.Tags?.Add("vip");
```

### Simple Lambda Parameters with Modifiers

Lambda parameters can now have modifiers (`ref`, `out`, `in`, `scoped`) without requiring explicit types.

```csharp
// Before C# 14: modifiers required explicit types
Func<string, bool> tryParse = (string text, out int result) =>
    int.TryParse(text, out result);

// C# 14: modifiers without types
TryParse<int> tryParse = (text, out result) =>
    int.TryParse(text, out result);
```

### Implicit Span Conversions

First-class `Span<T>` and `ReadOnlySpan<T>` support. Implicit conversions between arrays, spans, and read-only spans reduce boilerplate in high-performance code.

```csharp
// C# 14: implicit conversion from T[] to Span<T>
void ProcessData(ReadOnlySpan<byte> data) { /* ... */ }

byte[] buffer = GetBuffer();
ProcessData(buffer); // No explicit cast needed

// Spans work as extension method receivers
Span<int> numbers = stackalloc int[] { 1, 2, 3 };
var hasTwo = numbers.Contains(2); // Extension method resolves on Span<T>
```

### Partial Events and Constructors

`partial` now applies to instance constructors and events, not just methods and properties.

```csharp
// Partial constructor — useful for source generators
public partial class UserEntity
{
    public partial UserEntity(string email, string name);
}

// In generated file
public partial class UserEntity
{
    public partial UserEntity(string email, string name)
    {
        Email = email ?? throw new ArgumentNullException(nameof(email));
        Name = name ?? throw new ArgumentNullException(nameof(name));
        CreatedAt = DateTime.UtcNow;
    }
}
```

---

## Async Patterns

### async/await Best Practices

**Async All the Way**
```csharp
// Good: Async from controller to data access
public async Task<IActionResult> GetUser(int id)
{
    var user = await _userService.GetByIdAsync(id);
    return user is null ? NotFound() : Ok(user);
}

// Avoid: Blocking on async code (deadlock risk)
public IActionResult GetUser(int id)
{
    var user = _userService.GetByIdAsync(id).Result; // DEADLOCK
    return Ok(user);
}
```

**ConfigureAwait in Library Code**
```csharp
// Good: Library/shared code should not capture context
public async Task<byte[]> DownloadAsync(string url)
{
    using var client = new HttpClient();
    return await client.GetByteArrayAsync(url).ConfigureAwait(false);
}

// ASP.NET Core controllers: ConfigureAwait(false) is not needed
// (no SynchronizationContext) but harmless
```

**Cancellation Token Propagation**
```csharp
// Good: Accept and forward CancellationToken everywhere
public async Task<User?> GetByIdAsync(int id, CancellationToken ct = default)
{
    return await _context.Users
        .FirstOrDefaultAsync(u => u.Id == id, ct);
}

// Controller
[HttpGet("{id}")]
public async Task<IActionResult> GetUser(int id, CancellationToken ct)
{
    var user = await _userService.GetByIdAsync(id, ct);
    return user is null ? NotFound() : Ok(user);
}
```

**Parallel Async Operations**
```csharp
// Good: Run independent tasks in parallel
public async Task<DashboardData> GetDashboardAsync(int userId, CancellationToken ct)
{
    var userTask = _userService.GetByIdAsync(userId, ct);
    var ordersTask = _orderService.GetRecentAsync(userId, ct);
    var statsTask = _statsService.GetUserStatsAsync(userId, ct);

    await Task.WhenAll(userTask, ordersTask, statsTask);

    return new DashboardData(
        userTask.Result,
        ordersTask.Result,
        statsTask.Result);
}

// Avoid: Sequential awaits for independent operations
var user = await _userService.GetByIdAsync(userId, ct);
var orders = await _orderService.GetRecentAsync(userId, ct); // Unnecessary wait
```

**ValueTask for Hot Paths**
```csharp
// Good: Use ValueTask when result is often synchronous (cached)
public ValueTask<User?> GetCachedUserAsync(int id)
{
    if (_cache.TryGetValue(id, out var user))
        return ValueTask.FromResult<User?>(user);

    return new ValueTask<User?>(FetchAndCacheUserAsync(id));
}
```

---

## Error Handling

### Result Pattern

```csharp
// Good: Typed result instead of exceptions for domain errors
public abstract record Result<T>
{
    public record Success(T Value) : Result<T>;
    public record Failure(string Error, string? Code = null) : Result<T>;

    public T? GetValueOrDefault() => this is Success s ? s.Value : default;
    public bool IsSuccess => this is Success;
}

// Usage
public async Task<Result<User>> CreateUserAsync(CreateUserRequest request)
{
    var existing = await _repo.GetByEmailAsync(request.Email);
    if (existing is not null)
        return new Result<User>.Failure("Email already registered", "DUPLICATE_EMAIL");

    var user = new User(request.Email, request.FullName);
    await _repo.AddAsync(user);
    return new Result<User>.Success(user);
}
```

### Exception Hierarchy

```csharp
// Domain exceptions
public abstract class DomainException(string message, string code)
    : Exception(message)
{
    public string Code { get; } = code;
}

public class NotFoundException(string entity, object id)
    : DomainException($"{entity} with id '{id}' was not found", "NOT_FOUND");

public class ConflictException(string message)
    : DomainException(message, "CONFLICT");

public class ValidationException(string message, IDictionary<string, string[]>? errors = null)
    : DomainException(message, "VALIDATION_ERROR")
{
    public IDictionary<string, string[]> Errors { get; } = errors ?? new Dictionary<string, string[]>();
}
```

### Global Exception Handler (Middleware)

```csharp
public class ExceptionHandlingMiddleware(
    RequestDelegate next,
    ILogger<ExceptionHandlingMiddleware> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await next(context);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Unhandled exception for {Method} {Path}",
                context.Request.Method, context.Request.Path);

            await HandleExceptionAsync(context, ex);
        }
    }

    private static async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var (statusCode, problemDetails) = exception switch
        {
            NotFoundException ex => (StatusCodes.Status404NotFound,
                new ProblemDetails
                {
                    Status = 404,
                    Title = "Resource not found",
                    Detail = ex.Message,
                    Type = "https://tools.ietf.org/html/rfc9110#section-15.5.5"
                }),
            ValidationException ex => (StatusCodes.Status400BadRequest,
                new ValidationProblemDetails(ex.Errors)
                {
                    Status = 400,
                    Title = "Validation failed",
                    Detail = ex.Message,
                    Type = "https://tools.ietf.org/html/rfc9110#section-15.5.1"
                }),
            ConflictException ex => (StatusCodes.Status409Conflict,
                new ProblemDetails
                {
                    Status = 409,
                    Title = "Conflict",
                    Detail = ex.Message,
                    Type = "https://tools.ietf.org/html/rfc9110#section-15.5.10"
                }),
            _ => (StatusCodes.Status500InternalServerError,
                new ProblemDetails
                {
                    Status = 500,
                    Title = "An error occurred",
                    Detail = "An unexpected error occurred. Please try again later.",
                    Type = "https://tools.ietf.org/html/rfc9110#section-15.6.1"
                })
        };

        context.Response.StatusCode = statusCode;
        context.Response.ContentType = "application/problem+json";
        await context.Response.WriteAsJsonAsync(problemDetails);
    }
}
```

---

## HTTP Server Best Practices

### Minimal API (ASP.NET Core 10)

```csharp
var builder = WebApplication.CreateBuilder(args);

// Services
builder.Services.AddOpenApi(); // OpenAPI 3.1 (replaces Swashbuckle in .NET 10)
builder.Services.AddValidation(); // Built-in validation (.NET 10)
builder.Services.AddScoped<IUserService, UserService>();

var app = builder.Build();

// Middleware
app.UseMiddleware<ExceptionHandlingMiddleware>();
app.UseAuthentication();
app.UseAuthorization();

app.MapOpenApi(); // Serves OpenAPI 3.1 doc at /openapi/v1.json

// Route groups
var api = app.MapGroup("/api/v1");

api.MapGet("/users/{id}", async (int id, IUserService svc, CancellationToken ct) =>
{
    var user = await svc.GetByIdAsync(id, ct);
    return user is null ? Results.NotFound() : Results.Ok(user);
})
.WithName("GetUser")
.Produces<UserDto>(200)
.Produces(404);

// .NET 10: Validation is automatic via [Required], [Range], etc.
api.MapPost("/users", async (CreateUserRequest req, IUserService svc, CancellationToken ct) =>
{
    var user = await svc.CreateAsync(req, ct);
    return Results.Created($"/api/v1/users/{user.Id}", user);
})
.WithName("CreateUser")
.Produces<UserDto>(201)
.ProducesValidationProblem();

app.Run();
```

### Server-Sent Events (ASP.NET Core 10)

```csharp
// SSE endpoint — built-in support in .NET 10
app.MapGet("/api/v1/events/orders", (CancellationToken ct) =>
{
    async IAsyncEnumerable<OrderEvent> StreamOrders(
        [EnumeratorCancellation] CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            var evt = await _orderQueue.DequeueAsync(cancellationToken);
            yield return evt;
        }
    }

    return TypedResults.ServerSentEvents(StreamOrders(ct), eventType: "order-update");
});
```

### Built-in Minimal API Validation (.NET 10)

```csharp
// Validation attributes work automatically — no manual FluentValidation needed
public record CreateUserRequest(
    [Required] string Email,
    [Required, MinLength(8)] string Password,
    [Required, MinLength(2), MaxLength(255)] string FullName);

// Source-generator based — AOT-compatible
// Empty form strings automatically map to null for nullable types
public record UpdateUserRequest(
    string? Email,
    DateOnly? BirthDate); // Empty string → null (no parse error)

// Disable validation for specific endpoints
app.MapPost("/internal/import", (RawData data) => Results.Ok())
    .DisableValidation();
```

### Controller-Based API

```csharp
[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class UsersController(
    IUserService userService,
    ILogger<UsersController> logger) : ControllerBase
{
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserDto), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> GetById(int id, CancellationToken ct)
    {
        var user = await userService.GetByIdAsync(id, ct);
        return user is null ? NotFound() : Ok(user);
    }

    [HttpPost]
    [ProducesResponseType(typeof(UserDto), 201)]
    [ProducesResponseType(typeof(ValidationProblemDetails), 400)]
    public async Task<IActionResult> Create(
        [FromBody] CreateUserRequest request,
        CancellationToken ct)
    {
        var user = await userService.CreateAsync(request, ct);
        return CreatedAtAction(nameof(GetById), new { id = user.Id }, user);
    }
}
```

### Middleware Pipeline

```csharp
var app = builder.Build();

// Order matters: outermost to innermost
app.UseExceptionHandler("/error");
app.UseHsts();
app.UseHttpsRedirection();
app.UseResponseCompression();

app.UseCors("AllowSpecificOrigins");
app.UseAuthentication();
app.UseAuthorization();

app.UseRateLimiter();
app.MapControllers();

app.Run();
```

### Health Checks

```csharp
// Registration
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "postgres")
    .AddRedis(redisConnectionString, name: "redis")
    .AddCheck<CustomHealthCheck>("custom");

// Mapping
app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false // No dependency checks for liveness
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});
```

### Graceful Shutdown

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.Configure<HostOptions>(options =>
{
    options.ShutdownTimeout = TimeSpan.FromSeconds(30);
});

var app = builder.Build();

app.Lifetime.ApplicationStopping.Register(() =>
{
    Log.Information("Application is shutting down...");
    // Drain queues, close connections, etc.
});

app.Run();
```

---

## Database Patterns

### Entity Framework Core 10 Setup

```csharp
public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();
    public DbSet<Order> Orders => Set<Order>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}

// Registration with connection pooling
builder.Services.AddDbContextPool<AppDbContext>(options =>
{
    options.UseNpgsql(connectionString, npgsqlOptions =>
    {
        npgsqlOptions.EnableRetryOnFailure(
            maxRetryCount: 3,
            maxRetryDelay: TimeSpan.FromSeconds(5),
            errorCodesToAdd: null);
        npgsqlOptions.CommandTimeout(30);
    });
});
```

### Entity Configuration (Fluent API)

```csharp
public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("users");
        builder.HasKey(u => u.Id);

        builder.Property(u => u.Email)
            .HasMaxLength(255)
            .IsRequired();

        builder.Property(u => u.FullName)
            .HasMaxLength(255)
            .IsRequired();

        builder.Property(u => u.HashedPassword)
            .HasMaxLength(255)
            .IsRequired();

        builder.Property(u => u.CreatedAt)
            .HasDefaultValueSql("NOW()");

        builder.HasIndex(u => u.Email).IsUnique();
    }
}
```

### Repository Pattern

```csharp
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<T>> GetAllAsync(CancellationToken ct = default);
    Task AddAsync(T entity, CancellationToken ct = default);
    void Update(T entity);
    void Remove(T entity);
}

public class EfRepository<T>(AppDbContext context) : IRepository<T>
    where T : class
{
    public async Task<T?> GetByIdAsync(int id, CancellationToken ct = default)
        => await context.Set<T>().FindAsync([id], ct);

    public async Task<IReadOnlyList<T>> GetAllAsync(CancellationToken ct = default)
        => await context.Set<T>().ToListAsync(ct);

    public async Task AddAsync(T entity, CancellationToken ct = default)
        => await context.Set<T>().AddAsync(entity, ct);

    public void Update(T entity)
        => context.Set<T>().Update(entity);

    public void Remove(T entity)
        => context.Set<T>().Remove(entity);
}
```

### Unit of Work

```csharp
public interface IUnitOfWork
{
    IUserRepository Users { get; }
    IOrderRepository Orders { get; }
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}

public class UnitOfWork(AppDbContext context) : IUnitOfWork
{
    private IUserRepository? _users;
    private IOrderRepository? _orders;

    public IUserRepository Users =>
        _users ??= new UserRepository(context);

    public IOrderRepository Orders =>
        _orders ??= new OrderRepository(context);

    public Task<int> SaveChangesAsync(CancellationToken ct = default)
        => context.SaveChangesAsync(ct);
}
```

### Transaction Pattern

```csharp
public async Task TransferFundsAsync(int fromId, int toId, decimal amount, CancellationToken ct)
{
    await using var transaction = await _context.Database.BeginTransactionAsync(ct);
    try
    {
        var from = await _context.Accounts.FindAsync([fromId], ct)
            ?? throw new NotFoundException("Account", fromId);
        var to = await _context.Accounts.FindAsync([toId], ct)
            ?? throw new NotFoundException("Account", toId);

        from.Balance -= amount;
        to.Balance += amount;

        await _context.SaveChangesAsync(ct);
        await transaction.CommitAsync(ct);
    }
    catch
    {
        await transaction.RollbackAsync(ct);
        throw;
    }
}
```

### Named Query Filters (EF Core 10)

Named filters replace the single-filter-per-entity limitation. Each filter gets a name and can be selectively disabled per query.

```csharp
// Model configuration — multiple named filters
modelBuilder.Entity<User>()
    .HasQueryFilter("SoftDelete", u => u.DeletedAt == null)
    .HasQueryFilter("ActiveOnly", u => u.IsActive);

modelBuilder.Entity<Order>()
    .HasQueryFilter("SoftDelete", o => o.DeletedAt == null)
    .HasQueryFilter("TenantFilter", o => o.TenantId == currentTenantId);

// Disable specific filters per query
var allUsersIncludingDeleted = await _context.Users
    .IgnoreQueryFilters(["SoftDelete"])
    .ToListAsync(ct);

// Disable all filters (same as before)
var everything = await _context.Users
    .IgnoreQueryFilters()
    .ToListAsync(ct);
```

### LeftJoin / RightJoin (EF Core 10)

First-class LINQ join operators — replaces the verbose GroupJoin + SelectMany + DefaultIfEmpty pattern.

```csharp
// Before EF Core 10: verbose left join
var query = context.Students
    .GroupJoin(context.Departments,
        s => s.DepartmentId, d => d.Id,
        (s, deps) => new { Student = s, Deps = deps })
    .SelectMany(
        x => x.Deps.DefaultIfEmpty(),
        (x, dept) => new { x.Student.Name, Department = dept!.Name ?? "[NONE]" });

// EF Core 10: clean LeftJoin
var query = context.Students
    .LeftJoin(
        context.Departments,
        student => student.DepartmentId,
        department => department.Id,
        (student, department) => new
        {
            student.FirstName,
            student.LastName,
            Department = department.Name ?? "[NONE]"
        });
```

### Simplified ExecuteUpdateAsync (EF Core 10)

The lambda is now a regular `Action` instead of an expression tree, making conditional updates trivial.

```csharp
// EF Core 10: regular lambda — conditional logic works naturally
await context.Users.ExecuteUpdateAsync(s =>
{
    s.SetProperty(u => u.LastLoginAt, DateTime.UtcNow);
    if (resetPoints)
    {
        s.SetProperty(u => u.Points, 0);
    }
});

// Bulk update JSON properties (EF Core 10 + complex types)
await context.Blogs.ExecuteUpdateAsync(s =>
    s.SetProperty(b => b.Details.Views, b => b.Details.Views + 1));
```

### Migrations

```bash
# Create migration
dotnet ef migrations add CreateUsersTable

# Apply migrations
dotnet ef database update

# Generate SQL script (for production)
dotnet ef migrations script --idempotent -o migrations.sql
```

---

## Dependency Injection

### Registration Patterns

```csharp
var builder = WebApplication.CreateBuilder(args);

// Scoped: One instance per HTTP request (default for EF DbContext)
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();

// Transient: New instance every time
builder.Services.AddTransient<IEmailService, EmailService>();

// Singleton: One instance for the app lifetime
builder.Services.AddSingleton<ICacheService, RedisCacheService>();

// Keyed services (.NET 8+)
builder.Services.AddKeyedScoped<INotificationService, EmailNotification>("email");
builder.Services.AddKeyedScoped<INotificationService, SmsNotification>("sms");
```

### Interface Segregation

```csharp
// Good: Small, focused interfaces
public interface IUserReader
{
    Task<User?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<User?> GetByEmailAsync(string email, CancellationToken ct = default);
}

public interface IUserWriter
{
    Task AddAsync(User user, CancellationToken ct = default);
    Task UpdateAsync(User user, CancellationToken ct = default);
}

// Avoid: God interface
public interface IUserService
{
    // 20+ methods covering everything
}
```

---

## Caching Patterns

### HybridCache (.NET 10 — GA)

HybridCache replaces manual `IMemoryCache` + `IDistributedCache` stacking. It provides L1 (in-memory) + L2 (Redis) with stampede protection, tag-based invalidation, and a single API.

```csharp
// Registration
builder.Services.AddHybridCache(options =>
{
    options.DefaultEntryOptions = new HybridCacheEntryOptions
    {
        Expiration = TimeSpan.FromMinutes(5),
        LocalCacheExpiration = TimeSpan.FromMinutes(1)
    };
});

// Add Redis as L2 backend
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = "localhost:6379";
});

// Usage in service — stampede-safe by default
public class ProductService(HybridCache cache, IProductRepository repo)
{
    public async Task<ProductDto?> GetByIdAsync(int id, CancellationToken ct)
    {
        return await cache.GetOrCreateAsync(
            $"product:{id}",
            async token => await repo.GetByIdAsync(id, token),
            new HybridCacheEntryOptions { Expiration = TimeSpan.FromMinutes(10) },
            tags: ["products"],
            cancellationToken: ct);
    }

    public async Task InvalidateProductCacheAsync(CancellationToken ct)
    {
        // Tag-based bulk invalidation
        await cache.RemoveByTagAsync("products", ct);
    }
}
```

| Feature | IMemoryCache | IDistributedCache | HybridCache |
|---------|-------------|-------------------|-------------|
| L1 (in-process) | Yes | No | Yes |
| L2 (Redis) | No | Yes | Yes |
| Stampede protection | No | No | Yes |
| Tag-based invalidation | No | No | Yes |
| Single API | Yes | Yes | Yes |

---

## Resilience Patterns

### Microsoft.Extensions.Resilience + Polly v8

> **Polly v8** is the standard for .NET resilience. Use `Microsoft.Extensions.Http.Resilience` for HTTP clients — it integrates Polly v8 with DI, OpenTelemetry, and `IHttpClientFactory`.

```csharp
// Registration: standard resilience handler (retry + circuit breaker + timeout)
builder.Services.AddHttpClient("ExternalApi", client =>
{
    client.BaseAddress = new Uri("https://api.example.com");
})
.AddStandardResilienceHandler(); // Polly v8: retry, circuit breaker, timeout, rate limiter

// Custom resilience pipeline
builder.Services.AddHttpClient("PaymentGateway", client =>
{
    client.BaseAddress = new Uri("https://payments.example.com");
})
.AddResilienceHandler("payment-pipeline", pipeline =>
{
    pipeline.AddRetry(new HttpRetryStrategyOptions
    {
        MaxRetryAttempts = 3,
        Delay = TimeSpan.FromMilliseconds(500),
        BackoffType = DelayBackoffType.Exponential,
        ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
            .HandleResult(r => r.StatusCode == HttpStatusCode.TooManyRequests)
            .HandleResult(r => r.StatusCode >= HttpStatusCode.InternalServerError)
    });

    pipeline.AddCircuitBreaker(new HttpCircuitBreakerStrategyOptions
    {
        SamplingDuration = TimeSpan.FromSeconds(30),
        FailureRatio = 0.5,
        MinimumThroughput = 10,
        BreakDuration = TimeSpan.FromSeconds(15)
    });

    pipeline.AddTimeout(TimeSpan.FromSeconds(10));
});
```

| Do | Avoid |
|----|-------|
| Use `AddStandardResilienceHandler()` as default | Writing manual retry loops |
| Configure per-client resilience pipelines | Global retry policies for all clients |
| Set explicit timeouts on every HTTP client | Unbounded HTTP calls |
| Use `AddResilienceHandler` for custom policies | Raw `Polly.Policy` (legacy v7 API) |

---

## Performance Optimization

### Response Caching and Compression

```csharp
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
});

builder.Services.AddOutputCache(options =>
{
    options.AddBasePolicy(p => p.Expire(TimeSpan.FromMinutes(5)));
    options.AddPolicy("UserProfile", p =>
        p.Expire(TimeSpan.FromMinutes(1)).Tag("users"));
});

// Invalidation
app.MapPut("/api/v1/users/{id}", async (int id, ..., IOutputCacheStore cache, CancellationToken ct) =>
{
    // ... update user
    await cache.EvictByTagAsync("users", ct);
});
```

### Efficient Database Queries

```csharp
// Good: Select only what you need
var userDtos = await _context.Users
    .Where(u => u.IsActive)
    .Select(u => new UserDto(u.Id, u.Email, u.FullName))
    .AsNoTracking()
    .ToListAsync(ct);

// Avoid: Loading entire entities when you need a few fields
var users = await _context.Users.ToListAsync(ct);
var dtos = users.Select(u => new UserDto(u.Id, u.Email, u.FullName));

// Good: Explicit eager loading
var orders = await _context.Orders
    .Include(o => o.Items)
    .Where(o => o.UserId == userId)
    .ToListAsync(ct);

// Avoid: Implicit lazy loading (N+1 queries)
```

### Compiled Queries

```csharp
// Good: Compile queries that run frequently
private static readonly Func<AppDbContext, string, Task<User?>> GetByEmailQuery =
    EF.CompileAsyncQuery((AppDbContext ctx, string email) =>
        ctx.Users.FirstOrDefault(u => u.Email == email));

public async Task<User?> GetByEmailAsync(string email)
    => await GetByEmailQuery(_context, email);
```

### IAsyncEnumerable for Large Result Sets

```csharp
// Good: Stream results instead of buffering
public async IAsyncEnumerable<UserDto> GetAllUsersAsync(
    [EnumeratorCancellation] CancellationToken ct = default)
{
    await foreach (var user in _context.Users.AsAsyncEnumerable().WithCancellation(ct))
    {
        yield return new UserDto(user.Id, user.Email, user.FullName);
    }
}
```

### Object Pooling

```csharp
// Good: Pool expensive objects
builder.Services.AddSingleton<ObjectPool<StringBuilder>>(
    new DefaultObjectPoolProvider().CreateStringBuilderPool());

// Usage
public string BuildReport(ObjectPool<StringBuilder> pool, IEnumerable<Item> items)
{
    var sb = pool.Get();
    try
    {
        foreach (var item in items)
            sb.AppendLine(item.ToString());
        return sb.ToString();
    }
    finally
    {
        pool.Return(sb);
    }
}
```

---

## Testing Best Practices

### Unit Tests with xUnit

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repoMock = new();
    private readonly Mock<ILogger<UserService>> _loggerMock = new();
    private readonly UserService _sut;

    public UserServiceTests()
    {
        _sut = new UserService(_repoMock.Object, _loggerMock.Object);
    }

    [Fact]
    public async Task GetByIdAsync_UserExists_ReturnsUser()
    {
        // Arrange
        var expected = new User { Id = 1, Email = "test@example.com" };
        _repoMock.Setup(r => r.GetByIdAsync(1, default))
            .ReturnsAsync(expected);

        // Act
        var result = await _sut.GetByIdAsync(1);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("test@example.com", result.Email);
    }

    [Fact]
    public async Task GetByIdAsync_UserNotFound_ReturnsNull()
    {
        _repoMock.Setup(r => r.GetByIdAsync(99, default))
            .ReturnsAsync((User?)null);

        var result = await _sut.GetByIdAsync(99);

        Assert.Null(result);
    }
}
```

### Theory (Parameterized Tests)

```csharp
[Theory]
[InlineData("", false)]
[InlineData("test", false)]
[InlineData("test@", false)]
[InlineData("test@example.com", true)]
[InlineData("user+tag@example.co.uk", true)]
public void IsValidEmail_ReturnsExpected(string email, bool expected)
{
    var result = EmailValidator.IsValid(email);
    Assert.Equal(expected, result);
}
```

### Integration Tests with WebApplicationFactory

```csharp
public class UsersApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public UsersApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace real DB with in-memory for tests
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));
            });
        }).CreateClient();
    }

    [Fact]
    public async Task CreateUser_ValidRequest_Returns201()
    {
        var request = new { Email = "test@example.com", Password = "P@ssw0rd!", FullName = "Test User" };

        var response = await _client.PostAsJsonAsync("/api/v1/users", request);

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var user = await response.Content.ReadFromJsonAsync<UserDto>();
        Assert.Equal("test@example.com", user!.Email);
    }

    [Fact]
    public async Task GetUser_NotFound_Returns404()
    {
        var response = await _client.GetAsync("/api/v1/users/999");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
```

### Test Data Builders

```csharp
public class UserBuilder
{
    private int _id = 1;
    private string _email = "user@example.com";
    private string _fullName = "Test User";
    private bool _isActive = true;

    public UserBuilder WithId(int id) { _id = id; return this; }
    public UserBuilder WithEmail(string email) { _email = email; return this; }
    public UserBuilder WithFullName(string name) { _fullName = name; return this; }
    public UserBuilder Inactive() { _isActive = false; return this; }

    public User Build() => new()
    {
        Id = _id,
        Email = _email,
        FullName = _fullName,
        IsActive = _isActive
    };
}

// Usage
var user = new UserBuilder().WithEmail("admin@company.com").Build();
```

---

## Logging Best Practices

### Structured Logging with Serilog

```csharp
// Program.cs
builder.Host.UseSerilog((context, config) =>
{
    config
        .ReadFrom.Configuration(context.Configuration)
        .Enrich.FromLogContext()
        .Enrich.WithMachineName()
        .Enrich.WithProperty("Application", "MyApi")
        .WriteTo.Console(new JsonFormatter())
        .WriteTo.Seq("http://localhost:5341");
});

// Usage in services
logger.LogInformation("User {UserId} placed order {OrderId} for {Amount:C}",
    userId, orderId, amount);

// Avoid string interpolation - breaks structured logging
logger.LogInformation($"User {userId} placed order {orderId}"); // BAD
```

### Correlation IDs

```csharp
public class CorrelationIdMiddleware(RequestDelegate next)
{
    private const string CorrelationHeader = "X-Correlation-Id";

    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers[CorrelationHeader].FirstOrDefault()
            ?? Guid.NewGuid().ToString();

        context.Items["CorrelationId"] = correlationId;
        context.Response.Headers[CorrelationHeader] = correlationId;

        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            await next(context);
        }
    }
}
```

### Log Scopes

```csharp
public async Task ProcessOrderAsync(int orderId, CancellationToken ct)
{
    using var scope = _logger.BeginScope(new Dictionary<string, object>
    {
        ["OrderId"] = orderId,
        ["Operation"] = "ProcessOrder"
    });

    _logger.LogInformation("Starting order processing");
    // All logs within this scope include OrderId and Operation
    await ValidateOrderAsync(orderId, ct);
    _logger.LogInformation("Order processing complete");
}
```

---

## Configuration Management

### Options Pattern

```csharp
// appsettings.json
// {
//   "Jwt": { "SecretKey": "...", "Issuer": "...", "ExpirationMinutes": 60 },
//   "Database": { "ConnectionString": "...", "MaxRetryCount": 3 }
// }

public class JwtOptions
{
    public const string SectionName = "Jwt";
    public required string SecretKey { get; init; }
    public required string Issuer { get; init; }
    public int ExpirationMinutes { get; init; } = 60;
}

// Registration with validation
builder.Services.AddOptions<JwtOptions>()
    .BindConfiguration(JwtOptions.SectionName)
    .ValidateDataAnnotations()
    .ValidateOnStart();

// Injection
public class AuthService(IOptions<JwtOptions> jwtOptions)
{
    private readonly JwtOptions _jwt = jwtOptions.Value;
}
```

### Environment-Based Configuration

```csharp
var builder = WebApplication.CreateBuilder(args);

// Loaded in order (later overrides earlier):
// appsettings.json
// appsettings.{Environment}.json
// Environment variables
// Command-line args

// Access
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
var jwtSecret = builder.Configuration["Jwt:SecretKey"];
```

---

## Security Best Practices

### Authentication with JWT

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = jwtOptions.Issuer,
            ValidateAudience = true,
            ValidAudience = jwtOptions.Audience,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(jwtOptions.SecretKey)),
            ClockSkew = TimeSpan.Zero
        };
    });
```

### Authorization Policies

```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireRole("Admin"));

    options.AddPolicy("PremiumUser", policy =>
        policy.RequireClaim("subscription", "premium", "enterprise"));
});

// Usage
[Authorize(Policy = "AdminOnly")]
[HttpDelete("{id}")]
public async Task<IActionResult> DeleteUser(int id, CancellationToken ct)
{
    // Only admins reach here
}
```

### Password Hashing

```csharp
// Good: Use ASP.NET Core Identity's PasswordHasher (PBKDF2)
// or BCrypt.Net-Next
using BCrypt.Net;

public static class PasswordHelper
{
    public static string Hash(string password)
        => BCrypt.Net.BCrypt.HashPassword(password, workFactor: 12);

    public static bool Verify(string password, string hash)
        => BCrypt.Net.BCrypt.Verify(password, hash);
}
```

### Passkey / WebAuthn Authentication (ASP.NET Core 10)

ASP.NET Core Identity now natively supports passkey authentication — phishing-resistant, passwordless sign-in using WebAuthn / FIDO2.

```csharp
// Registration — passkeys are built into Identity in .NET 10
builder.Services.AddIdentity<ApplicationUser, IdentityRole>()
    .AddEntityFrameworkStores<AppDbContext>()
    .AddDefaultTokenProviders();

// Passkey endpoints are included in the Identity UI scaffold
// No additional packages needed for basic passkey support
```

### Rate Limiting (.NET 8+)

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("fixed", limiter =>
    {
        limiter.PermitLimit = 100;
        limiter.Window = TimeSpan.FromMinutes(1);
        limiter.QueueLimit = 0;
    });

    options.AddSlidingWindowLimiter("sliding", limiter =>
    {
        limiter.PermitLimit = 100;
        limiter.Window = TimeSpan.FromMinutes(1);
        limiter.SegmentsPerWindow = 4;
    });

    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
});

// Apply to endpoints
app.MapGet("/api/data", () => "ok").RequireRateLimiting("fixed");
```

### CORS Configuration

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowSpecificOrigins", policy =>
    {
        policy.WithOrigins("https://myapp.com", "https://staging.myapp.com")
            .AllowAnyHeader()
            .AllowAnyMethod()
            .AllowCredentials();
    });
});
```

---

## Deployment Patterns

### Docker Multi-Stage Build

```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY *.csproj ./
RUN dotnet restore

COPY . .
RUN dotnet publish -c Release -o /app/publish --no-restore

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app

COPY --from=build /app/publish .

# Non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080

ENTRYPOINT ["dotnet", "MyApi.dll"]
```

### Kestrel Configuration

```csharp
builder.WebHost.ConfigureKestrel(options =>
{
    options.Limits.MaxConcurrentConnections = 100;
    options.Limits.MaxRequestBodySize = 10 * 1024 * 1024; // 10 MB
    options.Limits.RequestHeadersTimeout = TimeSpan.FromSeconds(30);
    options.Limits.KeepAliveTimeout = TimeSpan.FromMinutes(2);
});
```

---

## Common Pitfalls

### Captive Dependencies

```csharp
// BAD: Singleton captures scoped service -> same DbContext for all requests
builder.Services.AddSingleton<ISomeService, SomeService>(); // singleton
builder.Services.AddScoped<AppDbContext>(); // scoped

public class SomeService(AppDbContext context) { } // BUG: context is never refreshed

// GOOD: Use IServiceScopeFactory to create scopes on demand
public class SomeService(IServiceScopeFactory scopeFactory)
{
    public async Task DoWorkAsync()
    {
        using var scope = scopeFactory.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        // context is properly scoped
    }
}
```

### Async Void

```csharp
// BAD: Async void - exceptions are unobservable, fire-and-forget
public async void ProcessOrder(Order order) { /* ... */ } // Crashes silently on error

// GOOD: Async Task
public async Task ProcessOrderAsync(Order order) { /* ... */ }

// Exception: Event handlers in frameworks that require async void
```

### DbContext Threading

```csharp
// BAD: Sharing DbContext across threads
var tasks = userIds.Select(id => _context.Users.FindAsync(id).AsTask());
await Task.WhenAll(tasks); // DbContext is not thread-safe

// GOOD: Separate scope per concurrent operation
var tasks = userIds.Select(async id =>
{
    using var scope = _scopeFactory.CreateScope();
    var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    return await context.Users.FindAsync(id);
});
await Task.WhenAll(tasks);
```

### IDisposable Leaks

```csharp
// BAD: HttpClient not disposed / created per request
public async Task<string> FetchAsync(string url)
{
    var client = new HttpClient(); // Connection leak
    return await client.GetStringAsync(url);
}

// GOOD: Use IHttpClientFactory + resilience handler (.NET 10)
builder.Services.AddHttpClient("ExternalApi", client =>
{
    client.BaseAddress = new Uri("https://api.example.com");
})
.AddStandardResilienceHandler(); // Automatic retry, circuit breaker, timeout

public class ExternalApiService(IHttpClientFactory httpClientFactory)
{
    public async Task<string> FetchAsync(string path, CancellationToken ct)
    {
        var client = httpClientFactory.CreateClient("ExternalApi");
        return await client.GetStringAsync(path, ct);
    }
}
```

---

## Resources

- [What's new in .NET 10](https://learn.microsoft.com/dotnet/core/whats-new/dotnet-10/overview) - .NET 10 LTS release overview
- [What's new in C# 14](https://learn.microsoft.com/dotnet/csharp/whats-new/csharp-14) - Extension members, field keyword, null-conditional assignment
- [What's new in ASP.NET Core 10](https://learn.microsoft.com/aspnet/core/release-notes/aspnetcore-10.0) - Validation, SSE, OpenAPI 3.1, passkeys
- [What's new in EF Core 10](https://learn.microsoft.com/ef/core/what-is-new/ef-core-10.0/whatsnew) - LeftJoin, named filters, ExecuteUpdate
- [ASP.NET Core Documentation](https://learn.microsoft.com/aspnet/core/)
- [C# Language Reference](https://learn.microsoft.com/dotnet/csharp/)
- [Entity Framework Core Docs](https://learn.microsoft.com/ef/core/)
- [HybridCache in ASP.NET Core](https://learn.microsoft.com/aspnet/core/performance/caching/hybrid) - L1+L2 caching with stampede protection
- [Build resilient HTTP apps (.NET)](https://learn.microsoft.com/dotnet/core/resilience/http-resilience) - Polly v8 + Microsoft.Extensions.Resilience
- [.NET Architecture Guides](https://dotnet.microsoft.com/learn/dotnet/architecture-guides)
- [Minimal APIs Overview](https://learn.microsoft.com/aspnet/core/fundamentals/minimal-apis)
- [Steve Smith - Clean Architecture](https://github.com/ardalis/CleanArchitecture)
- [Nick Chapsas - YouTube (.NET patterns)](https://www.youtube.com/@nickchapsas)
- [Andrew Lock - .NET Blog](https://andrewlock.net/)
- [Milan Jovanovic - .NET Blog](https://www.milanjovanovic.tech/blog)
