# Backend Crypto Integration Best Practices

Patterns for building enterprise-grade cryptocurrency integration platforms in .NET/C#. Based on production systems integrating with TON, Fireblocks, and other blockchain providers.

---

## Table of Contents

1. [Architecture Patterns](#architecture-patterns)
2. [CQRS with MediatR](#cqrs-with-mediatr)
3. [Railway-Oriented Programming with FluentResults](#railway-oriented-programming-with-fluentresults)
4. [Multi-Provider Architecture](#multi-provider-architecture)
5. [Webhook Handling](#webhook-handling)
6. [Event-Driven Architecture with Kafka](#event-driven-architecture-with-kafka)
7. [Transaction Lifecycle Management](#transaction-lifecycle-management)
8. [Wallet Management](#wallet-management)
9. [HTTP Client Resilience](#http-client-resilience)
10. [Configuration Patterns](#configuration-patterns)
11. [Testing Patterns](#testing-patterns)
12. [Security Checklist](#security-checklist)
13. [Observability](#observability)

## Architecture Patterns

### Layered Architecture

**Standard project structure for crypto integrations:**

```
sources/
├── core/                    # Business logic & domain models
│   ├── Data/               # Enums, constants, domain models
│   ├── Services/           # Command handlers, service implementations
│   └── Parties/            # Crypto party creation & management
├── infrastructure/          # Technical integration & data access
│   ├── Kafka/              # Message publishing/consuming
│   ├── BlockchainApi/      # Blockchain client integrations
│   └── CustodialApi/       # Custodial provider integrations (Fireblocks)
├── presentation/            # API endpoints
│   ├── PublicApi/          # User-facing endpoints
│   ├── PrivateApi/         # Internal service endpoints
│   └── Contracts/          # Shared DTOs
└── tests/
    ├── UnitTests/          # NUnit + Moq + AutoFixture
    ├── Api.Tests/          # Integration tests
    └── Utils/              # Test helpers, Wiremock
```

---

## CQRS with MediatR

**Command-based design for crypto operations:**

```csharp
// Command definition
public record OnboardUserCommand(
    string UserId,
    Currency Currency,
    CryptoNetwork Network
) : IRequest<Result<OnboardCommandResult>>;

// Handler with provider selection
public class OnboardUserCommandHandler : IRequestHandler<OnboardUserCommand, Result<OnboardCommandResult>>
{
    private readonly IMediator _mediator;
    private readonly ICalculateProviderService _calculateProviderService;

    public async Task<Result<OnboardCommandResult>> Handle(
        OnboardUserCommand request,
        CancellationToken cancellationToken)
    {
        var provider = await _calculateProviderService.GetCryptoProviderAsync(
            request.Currency, request.Network);

        return provider switch
        {
            CryptoProvider.TonDirect => await _mediator.Send(
                new TonApiOnboardUserCommand(request.UserId), cancellationToken),
            CryptoProvider.Fireblocks => await _mediator.Send(
                new FireblocksOnboardUserCommand(request.UserId, request.Currency), cancellationToken),
            _ => Result.Fail<OnboardCommandResult>("Unsupported provider")
        };
    }
}
```

**Benefits:**
- Clean separation of concerns
- Easy provider switching
- Testable with mocked MediatR

---

## Railway-Oriented Programming with FluentResults

**Error handling without exceptions:**

```csharp
// Service returning Result
public async Task<Result<PaymentInfo>> CreatePaymentAsync(CreatePaymentRequest request)
{
    var walletResult = await _walletService.GetWalletAsync(request.UserId);
    if (walletResult.IsFailed)
        return walletResult.ToResult<PaymentInfo>();

    var validationResult = ValidatePayment(request);
    if (validationResult.IsFailed)
        return validationResult;

    var payment = new PaymentInfo
    {
        Id = Guid.NewGuid(),
        Amount = request.Amount,
        Currency = request.Currency
    };

    await _unitOfWork.Get<PaymentInfo>().AddAsync(payment);
    await _unitOfWork.SaveChangesAsync();

    return Result.Ok(payment);
}

// Controller converting Result to HTTP response
[HttpPost]
public async Task<IActionResult> CreatePayment([FromBody] CreatePaymentRequest request)
{
    var result = await _mediator.Send(new CreatePaymentCommand(request));

    return result.ToApiResult(
        onSuccess: payment => Ok(new { PaymentId = payment.Id }),
        onFailure: errors => BadRequest(new { Errors = errors.Select(e => e.Message) })
    );
}
```

**Extension for HTTP responses:**
```csharp
public static class ResultExtensions
{
    public static IActionResult ToApiResult<T>(
        this Result<T> result,
        Func<T, IActionResult> onSuccess,
        Func<IEnumerable<IError>, IActionResult> onFailure)
    {
        return result.IsSuccess
            ? onSuccess(result.Value)
            : onFailure(result.Errors);
    }
}
```

---

## Multi-Provider Architecture

**Abstract provider interface:**

```csharp
public interface ICryptoProvider
{
    CryptoProvider ProviderType { get; }
    Task<Result<WalletInfo>> CreateWalletAsync(string userId, Currency currency);
    Task<Result<TransactionInfo>> CreatePayoutAsync(PayoutRequest request);
    Task<Result<decimal>> GetBalanceAsync(string address, Currency currency);
}

// Provider implementations
public class TonDirectProvider : ICryptoProvider
{
    public CryptoProvider ProviderType => CryptoProvider.TonDirect;

    public async Task<Result<WalletInfo>> CreateWalletAsync(string userId, Currency currency)
    {
        // Direct blockchain wallet creation via TonCenter API
        var wallet = await _tonApiClient.CreateWalletAsync(userId);
        return Result.Ok(new WalletInfo(wallet.Address, wallet.PublicKey));
    }
}

public class FireblocksProvider : ICryptoProvider
{
    public CryptoProvider ProviderType => CryptoProvider.Fireblocks;

    public async Task<Result<WalletInfo>> CreateWalletAsync(string userId, Currency currency)
    {
        // Custodial wallet via Fireblocks vault
        var vault = await _fireblocksClient.CreateVaultAccountAsync(userId);
        return Result.Ok(new WalletInfo(vault.DepositAddress, vault.VaultId));
    }
}
```

**Provider selection service:**

```csharp
public class CalculateProviderService : ICalculateProviderService
{
    public async Task<CryptoProvider> GetCryptoProviderAsync(
        Currency currency,
        CryptoNetwork network,
        ProviderSelectionCriteria? criteria = null)
    {
        // Provider routing logic based on:
        // - Currency/network support
        // - Fee optimization
        // - Compliance requirements
        // - User preferences (custodial vs non-custodial)

        return (currency, network) switch
        {
            (Currency.TON, CryptoNetwork.TON) => CryptoProvider.TonDirect,
            (Currency.USDT, CryptoNetwork.TON) => CryptoProvider.TonDirect,  // Jetton
            (Currency.ETH, CryptoNetwork.Ethereum) => CryptoProvider.Fireblocks,
            (Currency.USDT, CryptoNetwork.Ethereum) => CryptoProvider.Fireblocks,  // ERC-20
            _ => CryptoProvider.Fireblocks  // Default to custodial
        };
    }
}
```

---

## Webhook Handling

**Signature validation for webhook security:**

```csharp
public class FireblocksWebhookSignatureValidator : IWebhookSignatureValidator
{
    private readonly string _webhookSecret;

    public bool ValidateSignature(string payload, string signature, string timestamp)
    {
        var expectedSignature = ComputeHmacSha256(
            $"{timestamp}.{payload}",
            _webhookSecret);

        return CryptographicOperations.FixedTimeEquals(
            Encoding.UTF8.GetBytes(signature),
            Encoding.UTF8.GetBytes(expectedSignature));
    }

    private static string ComputeHmacSha256(string data, string secret)
    {
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret));
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(data));
        return Convert.ToBase64String(hash);
    }
}

// Authentication handler for webhook endpoints
public class WebhookSignatureAuthenticationHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.TryGetValue("X-Signature", out var signature))
            return AuthenticateResult.Fail("Missing signature header");

        Request.EnableBuffering();
        using var reader = new StreamReader(Request.Body, leaveOpen: true);
        var body = await reader.ReadToEndAsync();
        Request.Body.Position = 0;

        if (!_validator.ValidateSignature(body, signature, timestamp))
            return AuthenticateResult.Fail("Invalid signature");

        var claims = new[] { new Claim(ClaimTypes.Name, "webhook") };
        var identity = new ClaimsIdentity(claims, Scheme.Name);
        return AuthenticateResult.Success(new AuthenticationTicket(
            new ClaimsPrincipal(identity), Scheme.Name));
    }
}
```

**Webhook controller:**

```csharp
[ApiController]
[Route("v1/webhooks")]
public class WebhookController : ControllerBase
{
    [HttpPost("fireblocks/transactions")]
    [Authorize(AuthenticationSchemes = "FireblocksWebhook")]
    public async Task<IActionResult> HandleFireblocksTransaction(
        [FromBody] FireblocksTransactionWebhook webhook)
    {
        // Publish to Kafka for async processing
        await _kafkaProducer.PublishAsync(new FireblocksTransactionMessage
        {
            TransactionId = webhook.Data.Id,
            Status = webhook.Data.Status,
            TxHash = webhook.Data.TxHash
        });

        return Ok();  // Always return 200 to acknowledge receipt
    }
}
```

---

## Event-Driven Architecture with Kafka

**Message contracts (Protobuf):**

```protobuf
syntax = "proto3";

message CryptoPaymentReceivedMessage {
    string payment_id = 1;
    string user_id = 2;
    string amount = 3;
    string currency = 4;
    string tx_hash = 5;
    int64 timestamp = 6;
}

message CryptoUserWalletCreatedMessage {
    string wallet_id = 1;
    string user_id = 2;
    string address = 3;
    string network = 4;
}
```

**Producer pattern:**

```csharp
public class CryptoPaymentNotificationHandler
    : INotificationHandler<CryptoPaymentCompletedNotification>
{
    private readonly IKafkaProducer<string, CryptoPaymentReceivedMessage> _producer;

    public async Task Handle(
        CryptoPaymentCompletedNotification notification,
        CancellationToken cancellationToken)
    {
        var message = new CryptoPaymentReceivedMessage
        {
            PaymentId = notification.PaymentId.ToString(),
            UserId = notification.UserId,
            Amount = notification.Amount.ToString(),
            Currency = notification.Currency.ToString(),
            TxHash = notification.TxHash,
            Timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
        };

        await _producer.PublishAsync(
            topic: "crypto.payments.received",
            key: notification.PaymentId.ToString(),
            value: message,
            cancellationToken);
    }
}
```

**Consumer pattern:**

```csharp
public class FireblocksTransactionMessageHandler
    : IMessageHandler<FireblocksTransactionWebhookMessage>
{
    private readonly IMediator _mediator;

    public async Task HandleAsync(
        ConsumeResult<string, FireblocksTransactionWebhookMessage> message,
        CancellationToken cancellationToken)
    {
        var result = await _mediator.Send(
            new ProcessFireblocksTransactionCommand(
                message.Message.Value.TransactionId,
                message.Message.Value.Status),
            cancellationToken);

        if (result.IsFailed)
        {
            _logger.LogError("Failed to process transaction: {Errors}",
                result.Errors);
            throw new MessageProcessingException(result.Errors.First().Message);
        }
    }
}
```

---

## Transaction Lifecycle Management

**State machine for transactions:**

```csharp
public enum TransactionStatus
{
    Created,
    Pending,
    Confirming,
    Completed,
    Failed,
    Cancelled
}

public class TransactionStateMachine
{
    private static readonly Dictionary<(TransactionStatus, TransactionEvent), TransactionStatus>
        _transitions = new()
    {
        { (TransactionStatus.Created, TransactionEvent.Submitted), TransactionStatus.Pending },
        { (TransactionStatus.Pending, TransactionEvent.Broadcast), TransactionStatus.Confirming },
        { (TransactionStatus.Confirming, TransactionEvent.Confirmed), TransactionStatus.Completed },
        { (TransactionStatus.Pending, TransactionEvent.Rejected), TransactionStatus.Failed },
        { (TransactionStatus.Confirming, TransactionEvent.Reverted), TransactionStatus.Failed },
    };

    public Result<TransactionStatus> TryTransition(
        TransactionStatus current,
        TransactionEvent evt)
    {
        if (_transitions.TryGetValue((current, evt), out var next))
            return Result.Ok(next);

        return Result.Fail($"Invalid transition: {current} + {evt}");
    }
}
```

**Transaction monitoring service:**

```csharp
public class TransactionMonitoringService : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var pendingTransactions = await _repository
                .GetPendingTransactionsAsync(stoppingToken);

            foreach (var tx in pendingTransactions)
            {
                var status = await _blockchainClient
                    .GetTransactionStatusAsync(tx.TxHash);

                if (status != tx.Status)
                {
                    await _mediator.Send(new UpdateTransactionStatusCommand(
                        tx.Id, status), stoppingToken);
                }
            }

            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
        }
    }
}
```

---

## Wallet Management

**Wallet entity with multi-network support:**

```csharp
public class CryptoWallet
{
    public Guid Id { get; set; }
    public string UserId { get; set; }
    public string Address { get; set; }
    public CryptoNetwork Network { get; set; }
    public WalletType Type { get; set; }  // Custodial, NonCustodial
    public CryptoProvider Provider { get; set; }
    public WalletStatus Status { get; set; }
    public DateTime CreatedAt { get; set; }

    // Provider-specific data
    public string? VaultAccountId { get; set; }  // Fireblocks
    public int? SubWalletId { get; set; }  // TON
}

public enum WalletType
{
    Custodial,      // Provider holds keys (Fireblocks)
    NonCustodial,   // User holds keys
    Embedded        // App-embedded wallet
}
```

**Address derivation for TON:**

```csharp
public class TonWalletAddressService
{
    public string DeriveWalletAddress(byte[] publicKey, int subWalletId, WalletVersion version)
    {
        return version switch
        {
            WalletVersion.V4R2 => DeriveV4R2Address(publicKey, subWalletId),
            WalletVersion.V5R1 => DeriveV5R1Address(publicKey, subWalletId),
            _ => throw new NotSupportedException($"Wallet version {version} not supported")
        };
    }

    private string DeriveV4R2Address(byte[] publicKey, int subWalletId)
    {
        // TON address derivation logic
        var stateInit = BuildWalletV4StateInit(publicKey, subWalletId);
        var hash = ComputeStateInitHash(stateInit);
        return EncodeAddress(hash, workchain: 0, bounceable: true);
    }
}
```

---

## HTTP Client Resilience

**Polly-based resilience policies:**

```csharp
public static class HttpClientExtensions
{
    public static IHttpClientBuilder AddCryptoResilienceHandler(
        this IHttpClientBuilder builder,
        HttpClientResilienceOptions options)
    {
        return builder.AddResilienceHandler("crypto-resilience", pipeline =>
        {
            // Retry policy
            pipeline.AddRetry(new HttpRetryStrategyOptions
            {
                MaxRetryAttempts = options.Retry.MaxRetryAttempts,
                BackoffType = DelayBackoffType.Exponential,
                UseJitter = true,
                Delay = TimeSpan.FromSeconds(1),
                ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
                    .Handle<HttpRequestException>()
                    .HandleResult(r => r.StatusCode >= HttpStatusCode.InternalServerError)
            });

            // Circuit breaker
            pipeline.AddCircuitBreaker(new HttpCircuitBreakerStrategyOptions
            {
                FailureRatio = options.CircuitBreaker.FailureRatio,
                SamplingDuration = TimeSpan.FromSeconds(30),
                MinimumThroughput = 10,
                BreakDuration = TimeSpan.FromSeconds(30)
            });

            // Timeout
            pipeline.AddTimeout(options.AttemptTimeout.Timeout);
        });
    }
}

// Usage in DI
services.AddHttpClient<ITonCenterClient, TonCenterClient>(client =>
{
    client.BaseAddress = new Uri(configuration["TonCenter:BaseUrl"]);
})
.AddCryptoResilienceHandler(options);
```

---

## Configuration Patterns

**Strongly-typed options:**

```csharp
public sealed record CryptoPayoutOptions
{
    public required TimeSpan ResendDelay { get; init; }
    public required TimeSpan RetryTimeout { get; init; }
    public required int MaxRetryAttempts { get; init; }
}

public sealed record TonWalletOptions
{
    public required string MasterSeedVaultKey { get; init; }  // Vault reference
    public required WalletVersion DefaultVersion { get; init; }
    public required Dictionary<string, JettonConfig> Jettons { get; init; }
}

public sealed record JettonConfig
{
    public required string MasterAddress { get; init; }
    public required int Decimals { get; init; }
}
```

**appsettings.json structure:**

```json
{
  "CryptoPayoutOptions": {
    "ResendDelay": "00:05:00",
    "RetryTimeout": "1.00:00:00",
    "MaxRetryAttempts": 3
  },
  "TonWalletOptions": {
    "MasterSeedVaultKey": "crypto/ton/master-seed",
    "DefaultVersion": "V4R2",
    "Jettons": {
      "USDT": {
        "MasterAddress": "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs",
        "Decimals": 6
      }
    }
  },
  "FireblocksOptions": {
    "ApiKey": "${FIREBLOCKS_API_KEY}",
    "ApiSecretVaultKey": "crypto/fireblocks/api-secret",
    "BaseUrl": "https://api.fireblocks.io"
  }
}
```

---

## Testing Patterns

**Unit test with fixtures:**

```csharp
[TestFixture]
public class CreatePaymentCommandHandlerTests
{
    private CreatePaymentCommandHandlerFixture _fixture;

    [SetUp]
    public void SetUp() => _fixture = new CreatePaymentCommandHandlerFixture();

    [Test]
    public async Task Handle_WhenValidRequest_ShouldCreatePayment()
    {
        // Arrange
        var command = _fixture.CreateValidCommand();
        _fixture.SetupWalletExists();
        _fixture.SetupProviderSuccess();

        // Act
        var result = await _fixture.Handler.Handle(command, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value.PaymentId.Should().NotBeEmpty();
        _fixture.VerifyPaymentSaved();
    }
}

public class CreatePaymentCommandHandlerFixture
{
    public Mock<ICryptoUnitOfWork> UnitOfWorkMock { get; } = new();
    public Mock<IWalletService> WalletServiceMock { get; } = new();
    public CreatePaymentCommandHandler Handler { get; }

    public CreatePaymentCommandHandlerFixture()
    {
        Handler = new CreatePaymentCommandHandler(
            UnitOfWorkMock.Object,
            WalletServiceMock.Object);
    }

    public CreatePaymentCommand CreateValidCommand() =>
        new AutoFixture.Fixture().Create<CreatePaymentCommand>();

    public void SetupWalletExists() =>
        WalletServiceMock
            .Setup(x => x.GetWalletAsync(It.IsAny<string>()))
            .ReturnsAsync(Result.Ok(new WalletInfo()));
}
```

**Integration test with Wiremock:**

```csharp
[TestFixture]
public class TonCenterClientIntegrationTests
{
    private WireMockServer _server;
    private TonCenterClient _client;

    [SetUp]
    public void SetUp()
    {
        _server = WireMockServer.Start();
        _client = new TonCenterClient(new HttpClient
        {
            BaseAddress = new Uri(_server.Urls[0])
        });
    }

    [Test]
    public async Task GetBalance_ShouldReturnBalance()
    {
        // Arrange
        _server
            .Given(Request.Create()
                .WithPath("/v2/getAddressBalance")
                .WithParam("address", "EQ..."))
            .RespondWith(Response.Create()
                .WithStatusCode(200)
                .WithBody(@"{""result"": ""1000000000""}"));

        // Act
        var balance = await _client.GetBalanceAsync("EQ...");

        // Assert
        balance.Should().Be(1_000_000_000);
    }
}
```

---

## Security Checklist

**For crypto integration backends:**

- [ ] Webhook signatures validated with constant-time comparison
- [ ] Private keys stored in vault (never in config files)
- [ ] Rate limiting on all public endpoints
- [ ] Input validation on all addresses and amounts
- [ ] Decimal precision handling for different assets
- [ ] Idempotency keys for payment creation
- [ ] Transaction confirmation thresholds per network
- [ ] AML/KYC integration for compliance
- [ ] Audit logging for all financial operations
- [ ] Circuit breakers for external provider calls
- [ ] Dead letter queues for failed message processing
- [ ] Health checks for all external dependencies

---

## Observability

**Structured logging:**

```csharp
public class PaymentService
{
    public async Task<Result<PaymentInfo>> ProcessPaymentAsync(ProcessPaymentRequest request)
    {
        using var scope = _logger.BeginScope(new Dictionary<string, object>
        {
            ["PaymentId"] = request.PaymentId,
            ["UserId"] = request.UserId,
            ["Amount"] = request.Amount,
            ["Currency"] = request.Currency
        });

        _logger.LogInformation("Processing payment");

        try
        {
            var result = await ProcessInternalAsync(request);

            if (result.IsSuccess)
                _logger.LogInformation("Payment processed successfully");
            else
                _logger.LogWarning("Payment processing failed: {Errors}", result.Errors);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Payment processing exception");
            throw;
        }
    }
}
```

**Metrics:**

```csharp
public class CryptoMetricsService
{
    private readonly Counter<long> _paymentsProcessed;
    private readonly Histogram<double> _paymentDuration;

    public CryptoMetricsService(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Crypto.Payments");

        _paymentsProcessed = meter.CreateCounter<long>(
            "crypto.payments.processed",
            description: "Number of payments processed");

        _paymentDuration = meter.CreateHistogram<double>(
            "crypto.payments.duration",
            unit: "ms",
            description: "Payment processing duration");
    }

    public void RecordPaymentProcessed(Currency currency, PaymentStatus status)
    {
        _paymentsProcessed.Add(1,
            new KeyValuePair<string, object?>("currency", currency.ToString()),
            new KeyValuePair<string, object?>("status", status.ToString()));
    }
}
```
