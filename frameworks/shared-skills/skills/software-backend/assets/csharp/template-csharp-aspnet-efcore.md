# Backend Engineering - C# + ASP.NET Core + Entity Framework Core Template

*Purpose: Enterprise-grade .NET 10 (LTS) APIs with C# 14, strong typing, DI, and mature tooling, ideal for large teams and Azure ecosystems*

---

# When to Use

Use this template when building:
- Enterprise APIs with complex business logic and domain modeling
- Services targeting Azure or Windows Server ecosystems
- Systems requiring strong type safety and compile-time guarantees
- High-performance services needing AOT compilation or gRPC
- Teams with .NET/C# expertise or enterprise backgrounds
- Microservices with mature DevOps pipelines (CI/CD, health checks, observability)

**C#/ASP.NET Core Advantages:**
- **Built-in DI**: First-class dependency injection container
- **Performance**: Kestrel is among the fastest web servers; AOT compilation available
- **Strong typing**: Compile-time safety with nullable reference types
- **Mature ecosystem**: Entity Framework Core, Identity, SignalR, gRPC, OpenAPI
- **Cross-platform**: Runs on Linux, macOS, Windows
- **Enterprise tooling**: Visual Studio, Rider, dotnet CLI, Azure DevOps

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Tech Stack:**
- [ ] .NET 10 LTS (C# 14; released Nov 2025, supported through Nov 2028)
- [ ] ASP.NET Core 10 (Minimal API or Controller-based, built-in validation, OpenAPI 3.1)
- [ ] Entity Framework Core 10 (LeftJoin, named query filters, simplified ExecuteUpdate)
- [ ] PostgreSQL 16+ (via Npgsql provider)
- [ ] HybridCache + Redis (L1/L2 caching with stampede protection)
- [ ] Microsoft.Extensions.Resilience + Polly v8 (retry, circuit breaker, timeout)
- [ ] Serilog (structured logging)
- [ ] xUnit + Moq (testing)
- [ ] MediatR (optional, CQRS/mediator pattern)

**Project Name:** `{{project_name}}`

**Team:**
- Backend: {{team_size}} .NET developers
- DevOps: {{devops_team_size}} engineers

---

# 2. Project Structure

```
project-root/
|-- src/
|   |-- {{ProjectName}}.Api/
|   |   |-- Controllers/
|   |   |   |-- AuthController.cs
|   |   |   `-- UsersController.cs
|   |   |-- Middleware/
|   |   |   |-- ExceptionHandlingMiddleware.cs
|   |   |   `-- CorrelationIdMiddleware.cs
|   |   |-- Filters/
|   |   |   `-- ValidationFilter.cs
|   |   |-- Program.cs
|   |   |-- appsettings.json
|   |   |-- appsettings.Development.json
|   |   `-- {{ProjectName}}.Api.csproj
|   |-- {{ProjectName}}.Application/
|   |   |-- DTOs/
|   |   |   `-- UserDto.cs
|   |   |-- Interfaces/
|   |   |   |-- IUserService.cs
|   |   |   `-- IUserRepository.cs
|   |   |-- Services/
|   |   |   `-- UserService.cs
|   |   |-- Validators/
|   |   |   `-- CreateUserValidator.cs
|   |   `-- {{ProjectName}}.Application.csproj
|   |-- {{ProjectName}}.Domain/
|   |   |-- Entities/
|   |   |   `-- User.cs
|   |   |-- Exceptions/
|   |   |   |-- DomainException.cs
|   |   |   `-- NotFoundException.cs
|   |   |-- ValueObjects/
|   |   |   `-- Email.cs
|   |   `-- {{ProjectName}}.Domain.csproj
|   `-- {{ProjectName}}.Infrastructure/
|       |-- Data/
|       |   |-- AppDbContext.cs
|       |   |-- Configurations/
|       |   |   `-- UserConfiguration.cs
|       |   `-- Migrations/
|       |-- Repositories/
|       |   `-- UserRepository.cs
|       |-- Services/
|       |   `-- CacheService.cs
|       `-- {{ProjectName}}.Infrastructure.csproj
|-- tests/
|   |-- {{ProjectName}}.UnitTests/
|   |   |-- Services/
|   |   |   `-- UserServiceTests.cs
|   |   `-- {{ProjectName}}.UnitTests.csproj
|   `-- {{ProjectName}}.IntegrationTests/
|       |-- ApiTests/
|       |   `-- UsersApiTests.cs
|       |-- Fixtures/
|       |   `-- WebApplicationFixture.cs
|       `-- {{ProjectName}}.IntegrationTests.csproj
|-- docker-compose.yml
|-- Dockerfile
|-- .editorconfig
|-- Directory.Build.props
|-- {{ProjectName}}.sln
`-- README.md
```

**Key Principles:**
- Clean Architecture (Domain -> Application -> Infrastructure -> API)
- Dependency Inversion: inner layers define interfaces, outer layers implement
- Entity Framework Core with code-first migrations
- Serilog structured logging with correlation IDs
- xUnit integration tests with WebApplicationFactory

---

## Centralization Guide

> **Important**: Shared patterns go in the Application/Infrastructure layers. **Do not duplicate** across projects.

| Utility | Extract To | Reference |
|---------|------------|-----------|
| Config (Options pattern) | `Api/` service registration | [config-validation.md](../../../software-clean-code-standard/utilities/config-validation.md) |
| JWT (token generation/validation) | `Infrastructure/Services/` | [auth-utilities.md](../../../software-clean-code-standard/utilities/auth-utilities.md) |
| Password hashing (BCrypt) | `Infrastructure/Services/` | [auth-utilities.md](../../../software-clean-code-standard/utilities/auth-utilities.md) |
| Errors (ProblemDetails, middleware) | `Api/Middleware/` | [error-handling.md](../../../software-clean-code-standard/utilities/error-handling.md) |
| Logging (Serilog setup) | `Api/Program.cs` | [logging-utilities.md](../../../software-clean-code-standard/utilities/logging-utilities.md) |

---

# 3. Environment Configuration

## appsettings.json

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "Microsoft.EntityFrameworkCore": "Warning"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=myapp;Username=postgres;Password=postgres",
    "Redis": "localhost:6379"
  },
  "Jwt": {
    "SecretKey": "your-super-secret-jwt-key-minimum-32-characters-long",
    "Issuer": "MyApi",
    "Audience": "MyApi",
    "ExpirationMinutes": 60
  },
  "Cors": {
    "AllowedOrigins": ["http://localhost:3000", "https://myapp.com"]
  },
  "RateLimiting": {
    "PermitLimit": 100,
    "WindowSeconds": 60
  }
}
```

## Directory.Build.props

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest-recommended</AnalysisLevel>
  </PropertyGroup>
</Project>
```

## .editorconfig (excerpt)

```ini
[*.cs]
indent_style = space
indent_size = 4

# Prefer expression bodies
csharp_style_expression_bodied_methods = when_on_single_line
csharp_style_expression_bodied_properties = true

# Prefer primary constructors
csharp_style_prefer_primary_constructors = true

# Nullable
dotnet_diagnostic.CS8600.severity = error
dotnet_diagnostic.CS8602.severity = error
dotnet_diagnostic.CS8603.severity = error
```

---

# 4. Domain Layer

## Domain/Entities/User.cs

```csharp
namespace MyApp.Domain.Entities;

public class User
{
    public int Id { get; private set; }
    public string Email { get; private set; } = null!;
    public string HashedPassword { get; private set; } = null!;
    public string FullName { get; private set; } = null!;
    public bool IsActive { get; private set; } = true;
    public DateTime CreatedAt { get; private set; }
    public DateTime UpdatedAt { get; private set; }
    public DateTime? DeletedAt { get; private set; }

    private User() { } // EF Core needs parameterless constructor

    public static User Create(string email, string hashedPassword, string fullName)
    {
        return new User
        {
            Email = email,
            HashedPassword = hashedPassword,
            FullName = fullName,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
    }

    public void UpdateProfile(string fullName)
    {
        FullName = fullName;
        UpdatedAt = DateTime.UtcNow;
    }

    public void Deactivate()
    {
        IsActive = false;
        DeletedAt = DateTime.UtcNow;
        UpdatedAt = DateTime.UtcNow;
    }
}
```

## Domain/Exceptions/DomainException.cs

```csharp
namespace MyApp.Domain.Exceptions;

public abstract class DomainException(string message, string code)
    : Exception(message)
{
    public string Code { get; } = code;
}

public class NotFoundException(string entity, object id)
    : DomainException($"{entity} with id '{id}' was not found", "NOT_FOUND");

public class ConflictException(string message)
    : DomainException(message, "CONFLICT");
```

---

# 5. Infrastructure Layer

## Infrastructure/Data/AppDbContext.cs

```csharp
using Microsoft.EntityFrameworkCore;
using MyApp.Domain.Entities;

namespace MyApp.Infrastructure.Data;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}
```

## Infrastructure/Data/Configurations/UserConfiguration.cs

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using MyApp.Domain.Entities;

namespace MyApp.Infrastructure.Data.Configurations;

public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("users");
        builder.HasKey(u => u.Id);

        builder.Property(u => u.Email).HasMaxLength(255).IsRequired();
        builder.Property(u => u.HashedPassword).HasMaxLength(255).IsRequired();
        builder.Property(u => u.FullName).HasMaxLength(255).IsRequired();
        builder.Property(u => u.CreatedAt).HasDefaultValueSql("NOW()");
        builder.Property(u => u.UpdatedAt).HasDefaultValueSql("NOW()");

        builder.HasIndex(u => u.Email).IsUnique();

        // Global query filter for soft delete
        builder.HasQueryFilter(u => u.DeletedAt == null);
    }
}
```

## Infrastructure/Repositories/UserRepository.cs

```csharp
using Microsoft.EntityFrameworkCore;
using MyApp.Application.Interfaces;
using MyApp.Domain.Entities;
using MyApp.Infrastructure.Data;

namespace MyApp.Infrastructure.Repositories;

public class UserRepository(AppDbContext context) : IUserRepository
{
    public async Task<User?> GetByIdAsync(int id, CancellationToken ct = default)
        => await context.Users.FirstOrDefaultAsync(u => u.Id == id, ct);

    public async Task<User?> GetByEmailAsync(string email, CancellationToken ct = default)
        => await context.Users.FirstOrDefaultAsync(u => u.Email == email, ct);

    public async Task AddAsync(User user, CancellationToken ct = default)
    {
        await context.Users.AddAsync(user, ct);
        await context.SaveChangesAsync(ct);
    }

    public async Task UpdateAsync(User user, CancellationToken ct = default)
    {
        context.Users.Update(user);
        await context.SaveChangesAsync(ct);
    }

    public async Task<IReadOnlyList<User>> ListAsync(
        int skip = 0, int take = 20, CancellationToken ct = default)
    {
        return await context.Users
            .OrderBy(u => u.Id)
            .Skip(skip)
            .Take(take)
            .AsNoTracking()
            .ToListAsync(ct);
    }
}
```

---

# 6. Application Layer

## Application/Interfaces/IUserRepository.cs

```csharp
using MyApp.Domain.Entities;

namespace MyApp.Application.Interfaces;

public interface IUserRepository
{
    Task<User?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<User?> GetByEmailAsync(string email, CancellationToken ct = default);
    Task AddAsync(User user, CancellationToken ct = default);
    Task UpdateAsync(User user, CancellationToken ct = default);
    Task<IReadOnlyList<User>> ListAsync(int skip = 0, int take = 20, CancellationToken ct = default);
}
```

## Application/DTOs/UserDto.cs

```csharp
namespace MyApp.Application.DTOs;

public record UserDto(int Id, string Email, string FullName, bool IsActive, DateTime CreatedAt);

public record CreateUserRequest(string Email, string Password, string FullName);

public record UpdateUserRequest(string? FullName);

public record LoginRequest(string Email, string Password);

public record TokenResponse(string AccessToken, string TokenType = "Bearer");
```

## Application/Services/UserService.cs

```csharp
using MyApp.Application.DTOs;
using MyApp.Application.Interfaces;
using MyApp.Domain.Entities;
using MyApp.Domain.Exceptions;

namespace MyApp.Application.Services;

public class UserService(
    IUserRepository userRepository,
    IPasswordHasher passwordHasher,
    ILogger<UserService> logger) : IUserService
{
    public async Task<UserDto> CreateAsync(CreateUserRequest request, CancellationToken ct = default)
    {
        var existing = await userRepository.GetByEmailAsync(request.Email, ct);
        if (existing is not null)
            throw new ConflictException("Email already registered");

        var hashedPassword = passwordHasher.Hash(request.Password);
        var user = User.Create(request.Email, hashedPassword, request.FullName);

        await userRepository.AddAsync(user, ct);
        logger.LogInformation("User {UserId} created with email {Email}", user.Id, user.Email);

        return ToDto(user);
    }

    public async Task<UserDto?> GetByIdAsync(int id, CancellationToken ct = default)
    {
        var user = await userRepository.GetByIdAsync(id, ct);
        return user is null ? null : ToDto(user);
    }

    private static UserDto ToDto(User user) =>
        new(user.Id, user.Email, user.FullName, user.IsActive, user.CreatedAt);
}
```

---

# 7. API Layer

## Api/Program.cs

```csharp
using Microsoft.EntityFrameworkCore;
using MyApp.Api.Middleware;
using MyApp.Application.Interfaces;
using MyApp.Application.Services;
using MyApp.Infrastructure.Data;
using MyApp.Infrastructure.Repositories;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// Serilog
builder.Host.UseSerilog((context, config) =>
{
    config.ReadFrom.Configuration(context.Configuration)
        .Enrich.FromLogContext()
        .WriteTo.Console(new Serilog.Formatting.Json.JsonFormatter());
});

// Database (EF Core 10)
builder.Services.AddDbContextPool<AppDbContext>(options =>
{
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        npgsql => npgsql.EnableRetryOnFailure(3));
});

// DI
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IUserService, UserService>();

// HybridCache (.NET 10 — L1 in-memory + L2 Redis)
builder.Services.AddHybridCache();
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
});

// Resilience (Polly v8 via Microsoft.Extensions.Http.Resilience)
builder.Services.AddHttpClient("ExternalApi", client =>
{
    client.BaseAddress = new Uri(builder.Configuration["ExternalApi:BaseUrl"]!);
})
.AddStandardResilienceHandler();

// Validation (.NET 10 — source-generator based, automatic)
builder.Services.AddValidation();

// Auth
builder.Services.AddAuthentication().AddJwtBearer();
builder.Services.AddAuthorization();

// API
builder.Services.AddControllers();

// OpenAPI 3.1 (.NET 10 — replaces Swashbuckle)
builder.Services.AddOpenApi();

// Health checks
builder.Services.AddHealthChecks()
    .AddNpgSql(builder.Configuration.GetConnectionString("DefaultConnection")!);

// CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        var origins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? [];
        policy.WithOrigins(origins)
            .AllowAnyHeader()
            .AllowAnyMethod()
            .AllowCredentials();
    });
});

var app = builder.Build();

// Middleware pipeline
app.UseMiddleware<CorrelationIdMiddleware>();
app.UseMiddleware<ExceptionHandlingMiddleware>();
app.UseSerilogRequestLogging();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi(); // Serves OpenAPI 3.1 doc
}

app.UseHttpsRedirection();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.MapHealthChecks("/health");

app.Run();

// Make Program accessible for integration tests
public partial class Program { }
```

## Api/Controllers/UsersController.cs

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using MyApp.Application.DTOs;
using MyApp.Application.Interfaces;

namespace MyApp.Api.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
[Produces("application/json")]
public class UsersController(IUserService userService) : ControllerBase
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

---

# 8. Testing

## tests/UnitTests/Services/UserServiceTests.cs

```csharp
using Moq;
using MyApp.Application.DTOs;
using MyApp.Application.Interfaces;
using MyApp.Application.Services;
using MyApp.Domain.Entities;
using MyApp.Domain.Exceptions;

namespace MyApp.UnitTests.Services;

public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repoMock = new();
    private readonly Mock<IPasswordHasher> _hasherMock = new();
    private readonly Mock<ILogger<UserService>> _loggerMock = new();
    private readonly UserService _sut;

    public UserServiceTests()
    {
        _sut = new UserService(_repoMock.Object, _hasherMock.Object, _loggerMock.Object);
    }

    [Fact]
    public async Task CreateAsync_NewUser_ReturnsDto()
    {
        var request = new CreateUserRequest("test@example.com", "P@ssw0rd!", "Test User");
        _repoMock.Setup(r => r.GetByEmailAsync(request.Email, default)).ReturnsAsync((User?)null);
        _hasherMock.Setup(h => h.Hash(request.Password)).Returns("hashed");

        var result = await _sut.CreateAsync(request);

        Assert.Equal("test@example.com", result.Email);
        _repoMock.Verify(r => r.AddAsync(It.IsAny<User>(), default), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_DuplicateEmail_ThrowsConflict()
    {
        var existing = User.Create("test@example.com", "hash", "Existing");
        _repoMock.Setup(r => r.GetByEmailAsync("test@example.com", default)).ReturnsAsync(existing);

        await Assert.ThrowsAsync<ConflictException>(() =>
            _sut.CreateAsync(new("test@example.com", "pass", "New User")));
    }
}
```

## tests/IntegrationTests/ApiTests/UsersApiTests.cs

```csharp
using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using MyApp.Application.DTOs;
using MyApp.Infrastructure.Data;

namespace MyApp.IntegrationTests.ApiTests;

public class UsersApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public UsersApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb_" + Guid.NewGuid()));
            });
        }).CreateClient();
    }

    [Fact]
    public async Task CreateUser_ValidRequest_Returns201()
    {
        var request = new CreateUserRequest("test@example.com", "P@ssw0rd!", "Test User");

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

---

# 9. Docker Setup

## Dockerfile

```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY *.sln ./
COPY src/**/*.csproj ./src/
RUN for file in src/*/*.csproj; do \
      dir=$(dirname "$file"); \
      mkdir -p "$dir"; \
      mv "$file" "$dir/"; \
    done
RUN dotnet restore

COPY . .
RUN dotnet publish src/MyApp.Api/MyApp.Api.csproj -c Release -o /app/publish --no-restore

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser
USER appuser

COPY --from=build /app/publish .

EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080

ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
```

## docker-compose.yml

```yaml
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__DefaultConnection=Host=postgres;Port=5432;Database=myapp;Username=postgres;Password=postgres
      - ConnectionStrings__Redis=redis:6379
      - Jwt__SecretKey=your-super-secret-jwt-key-minimum-32-chars
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

## Makefile

```makefile
.PHONY: build run test migrate lint

build:
	dotnet build

run:
	dotnet run --project src/MyApp.Api

test:
	dotnet test --verbosity normal

test-coverage:
	dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage

migrate-add:
	dotnet ef migrations add $(name) --project src/MyApp.Infrastructure --startup-project src/MyApp.Api

migrate-up:
	dotnet ef database update --project src/MyApp.Infrastructure --startup-project src/MyApp.Api

migrate-script:
	dotnet ef migrations script --idempotent --project src/MyApp.Infrastructure --startup-project src/MyApp.Api -o migrations.sql

lint:
	dotnet format --verify-no-changes

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api
```

---

# 10. Production Checklist

## Security
- [ ] JWT secret is strong (min 32 chars) and stored in secret manager
- [ ] Passkey / WebAuthn support via ASP.NET Core Identity (.NET 10)
- [ ] HTTPS enforced via Kestrel or reverse proxy
- [ ] Rate limiting per endpoint (built-in .NET 8+ rate limiter)
- [ ] CORS restricted to specific origins
- [ ] SQL injection prevention (EF Core parameterized queries; SQL injection analyzer in EF 10)
- [ ] Password hashing with BCrypt (work factor 12+) or ASP.NET Core Identity PasswordHasher
- [ ] Input validation with built-in Minimal API validation (.NET 10) or DataAnnotations
- [ ] Security headers (HSTS, X-Content-Type-Options, etc.)
- [ ] Dependency vulnerability scanning (`dotnet list package --vulnerable`)
- [ ] Configuration validated at startup (Options pattern + ValidateOnStart)

## Performance
- [ ] DbContext pooling (`AddDbContextPool`)
- [ ] HybridCache for read-heavy operations (L1 in-memory + L2 Redis, stampede protection)
- [ ] Async/await for all I/O operations with CancellationToken propagation
- [ ] Database indexes on foreign keys and query columns
- [ ] Response compression (Brotli + GZip)
- [ ] Pagination for list endpoints (prefer cursor-based)
- [ ] Load testing with k6 or NBomber
- [ ] AsNoTracking for read-only queries; compiled queries for hot paths
- [ ] EF Core 10 LeftJoin instead of GroupJoin+SelectMany+DefaultIfEmpty

## Observability
- [ ] Structured logging with Serilog (JSON format)
- [ ] Correlation ID tracking (X-Correlation-Id header)
- [ ] Error tracking (Sentry or Application Insights)
- [ ] APM integration (Application Insights, Datadog, or New Relic)
- [ ] Health check endpoints (/health/live, /health/ready)
- [ ] Metrics exposed (Prometheus via prometheus-net or OpenTelemetry)
- [ ] OpenTelemetry tracing

## Deployment
- [ ] Multi-stage Docker build with non-root user
- [ ] Container security scanning
- [ ] EF Core migrations automated (or idempotent SQL scripts)
- [ ] Graceful shutdown configured (HostOptions.ShutdownTimeout)
- [ ] Zero-downtime deployment
- [ ] CI/CD pipeline (GitHub Actions, Azure DevOps)
- [ ] Blue-green or canary deployment

## Reliability
- [ ] Database backups automated
- [ ] Redis persistence configured
- [ ] Retry logic with Microsoft.Extensions.Resilience + Polly v8 (`AddStandardResilienceHandler`)
- [ ] Timeouts on all HTTP clients and DB queries
- [ ] Circuit breaker for external services (Polly v8 pipelines)
- [ ] Background jobs with retry (Hangfire or custom IHostedService)
- [ ] Dead letter queue for failed messages
- [ ] Named query filters for soft-delete and multi-tenancy (EF Core 10)

---

# END

**Congratulations!** You now have a production-grade C# 14 / .NET 10 backend with ASP.NET Core 10, Entity Framework Core 10, and PostgreSQL.

**Next Steps:**
1. Create solution: `dotnet new sln -n MyApp`
2. Create projects and add to solution
3. Copy `appsettings.json` and configure connection strings
4. Start services with `docker compose up -d`
5. Run migrations with `make migrate-up`
6. Start development server with `make run`
7. Access OpenAPI docs at `https://localhost:5001/openapi/v1.json`

**C# 14 / .NET 10 Best Practices:**
- **Extension members (C# 14)**: Use `extension` blocks for extension properties and methods
- **`field` keyword (C# 14)**: Semi-auto properties — custom accessor logic without backing field boilerplate
- **Null-conditional assignment (C# 14)**: `obj?.Prop = value;` — cleaner null-safe code
- **Nullable reference types**: Enable `<Nullable>enable</Nullable>` project-wide
- **Primary constructors**: Use for concise DI injection
- **Records for DTOs**: Immutable with value equality
- **Options pattern**: Strongly-typed configuration with validation
- **CancellationToken**: Propagate through all async methods
- **Clean Architecture**: Domain has no dependencies on infrastructure
- **HybridCache**: Replace manual IMemoryCache + IDistributedCache with HybridCache (L1+L2, stampede-safe)
- **Microsoft.Extensions.Resilience**: Use `AddStandardResilienceHandler()` for HTTP clients (replaces raw Polly)
- **Built-in validation**: Use `AddValidation()` — source-generator based, AOT-compatible
- **OpenAPI 3.1**: Use `AddOpenApi()` + `MapOpenApi()` (replaces Swashbuckle)
- **EF Core 10 LeftJoin**: Replace GroupJoin+SelectMany+DefaultIfEmpty with `.LeftJoin()`
- **Named query filters**: Tag filters by name, disable selectively with `.IgnoreQueryFilters(["name"])`
- **WebApplicationFactory**: Integration tests with real HTTP pipeline
- **Serilog**: Structured logging with message templates (no string interpolation)
