# .NET/EF Core Crypto Integration Security

Security rules for **C#/.NET crypto/fintech services** using **Entity Framework Core**. Apply these rules in addition to general AppSec patterns.

---

## Security Rules

### No Secrets in Code

- API keys, tokens, connection strings must come from configuration or environment variables
- Never hardcode credentials, private keys, or wallet seeds

### No Sensitive Data in Logs

- Tokens, passwords, private keys, wallet addresses with balances must not appear in logs
- Mask or exclude PII and financial data from log output

### Input Validation

- All external inputs validated before use (null/empty, format, ranges)
- Use `decimal` for all financial/crypto values — never `double` or `float`

### Database Security

- SQL queries must use ORM (EF Core) or parameterized queries — never string concatenation
- No dynamic SQL construction

### Error Messages

- Error responses must not expose internal technical details (stack traces, configuration values, connection strings)
- Use generic user-facing messages with detailed server-side logging

---

## C# Security Patterns

```csharp
// Good: Secrets from configuration
var apiKey = configuration["ExternalApi:ApiKey"];
var connectionString = configuration.GetConnectionString("CryptoDb");

// Bad: Hardcoded secrets
var apiKey = "sk-live-abc123..."; // NEVER DO THIS

// Good: Safe logging
_logger.LogInformation("Processing transaction {TransactionId}", transaction.Id);

// Bad: Sensitive data in logs
_logger.LogInformation("Processing with key {ApiKey}", apiKey); // NEVER LOG SECRETS

// Good: Parameterized query with EF Core
var wallet = await _context.Wallets
    .Where(w => w.Address == walletAddress)
    .FirstOrDefaultAsync(cancellationToken);

// Good: Financial precision
decimal amount = 100.50m;
decimal fee = amount * 0.001m;

// Bad: Floating point for money
double amount = 100.50; // NEVER USE FOR FINANCIAL VALUES
```

---

## Async & Error Handling

```csharp
// Good: Proper async with cancellation
public async Task<Result<Wallet>> GetWalletAsync(string address, CancellationToken ct)
{
    try
    {
        var wallet = await _context.Wallets
            .AsNoTracking()
            .FirstOrDefaultAsync(w => w.Address == address, ct);

        return wallet is null
            ? Result<Wallet>.Fail("Wallet not found")
            : Result<Wallet>.Success(wallet);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Failed to get wallet {Address}", address);
        return Result<Wallet>.Fail("Failed to retrieve wallet");
    }
}

// Bad: Blocking call
var wallet = _context.Wallets.FirstOrDefault(w => w.Address == address); // No async!

// Bad: Swallowed exception
try { ... }
catch { } // NEVER DO THIS
```

---

## Database (EF Core) Patterns

```csharp
// Good: AsNoTracking for read-only
var transactions = await _context.Transactions
    .AsNoTracking()
    .Where(t => t.WalletId == walletId)
    .ToListAsync(ct);

// Good: Selective Include
var wallet = await _context.Wallets
    .Include(w => w.Transactions.Where(t => t.Status == Status.Pending))
    .FirstOrDefaultAsync(w => w.Id == id, ct);

// Bad: N+1 query pattern
foreach (var wallet in wallets)
{
    var balance = await _context.Balances
        .FirstOrDefaultAsync(b => b.WalletId == wallet.Id); // Query per iteration!
}

// Good: Batch load
var walletIds = wallets.Select(w => w.Id).ToList();
var balances = await _context.Balances
    .Where(b => walletIds.Contains(b.WalletId))
    .ToDictionaryAsync(b => b.WalletId, ct);
```
