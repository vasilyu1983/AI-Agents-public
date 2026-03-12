# Core Blockchain Patterns

## Table of Contents

1. [Pattern: Smart Contract Architecture](#pattern-smart-contract-architecture)
2. [Pattern: Security-First Development](#pattern-security-first-development)
3. [Pattern: Gas Optimization](#pattern-gas-optimization)
4. [Pattern: Testing Strategy](#pattern-testing-strategy)
5. [Pattern: Upgradeable Contracts](#pattern-upgradeable-contracts)
6. [Pattern: DeFi Protocol Patterns](#pattern-defi-protocol-patterns)
7. [Pattern: Token Standards](#pattern-token-standards)
8. [Pattern: Multi-Provider Architecture](#pattern-multi-provider-architecture)
9. [Pattern: CQRS with MediatR](#pattern-cqrs-with-mediatr)
10. [Pattern: Webhook Security](#pattern-webhook-security)
11. [Pattern: Transaction Lifecycle](#pattern-transaction-lifecycle)
12. [Pattern: Event-Driven Crypto Payments](#pattern-event-driven-crypto-payments)
13. [On-Chain vs Off-Chain Data](#on-chain-vs-off-chain-data)

## Pattern: Smart Contract Architecture

**Use when:** Designing production smart contracts.

**Principles:**
- Separation of concerns (logic, storage, access control)
- Minimal trust assumptions
- Fail-safe defaults (whitelist vs blacklist)
- Circuit breakers for emergency stops
- Upgradeable patterns when needed
- Immutable core logic when possible

**Standard Architecture:**
```
Contracts/
├── interfaces/          # External interfaces
├── libraries/           # Reusable logic
├── tokens/              # ERC20, ERC721, ERC1155
├── core/                # Protocol logic
├── governance/          # DAO and voting
├── utils/               # Helpers
└── mocks/               # Test contracts
```

**Checklist:**
- [ ] Access control (OpenZeppelin AccessControl/Ownable)
- [ ] Reentrancy guards on state-changing functions
- [ ] Input validation and bounds checking
- [ ] Events for all state changes
- [ ] NatSpec documentation
- [ ] Gas optimization review
- [ ] Emergency pause mechanism
- [ ] Upgrade strategy documented

---

## Pattern: Security-First Development

**Use when:** Building any smart contract (security is non-negotiable).

**Critical Vulnerabilities to Prevent:**

**1. Reentrancy**
```solidity
// BAD: VULNERABLE
function withdraw() public {
    uint amount = balances[msg.sender];
    (bool success,) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] = 0;
}

// GOOD: SECURE (Checks-Effects-Interactions)
function withdraw() public nonReentrant {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;  // Update state BEFORE external call
    (bool success,) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

**2. Integer Overflow/Underflow**
```solidity
// GOOD: Use Solidity 0.8.0+ (automatic overflow checks)
// Or OpenZeppelin SafeMath for <0.8.0
```

**3. Access Control**
```solidity
// BAD: VULNERABLE
function setAdmin(address newAdmin) public {
    admin = newAdmin;
}

// GOOD: SECURE
function setAdmin(address newAdmin) public onlyOwner {
    require(newAdmin != address(0), "Zero address");
    emit AdminChanged(admin, newAdmin);
    admin = newAdmin;
}
```

**4. Frontrunning/MEV**
```solidity
// GOOD: Use commit-reveal schemes or Flashbots for sensitive operations
function commitOrder(bytes32 commitment) external;
function revealOrder(uint256 amount, bytes32 salt) external;
```

**5. Delegatecall to Untrusted Contracts**
```solidity
// BAD: VULNERABLE
target.delegatecall(data);

// GOOD: SECURE (whitelist known implementations)
require(isApprovedImplementation[target], "Untrusted target");
target.delegatecall(data);
```

**Security Checklist:**
- [ ] All external calls use checks-effects-interactions pattern
- [ ] Reentrancy guards on all state-changing functions
- [ ] Access control on privileged functions
- [ ] Input validation with custom errors
- [ ] No unchecked external calls
- [ ] Events emitted for all state changes
- [ ] Gas limits considered for loops
- [ ] Oracle data validated and not stale
- [ ] Upgradeable contracts use storage gaps
- [ ] Tested with fork tests against mainnet state

---

## Pattern: Gas Optimization

**Use when:** Optimizing contract deployment and execution costs.

**Storage Optimization:**
```solidity
// BAD: EXPENSIVE (multiple storage slots)
uint8 a;
uint256 b;
uint8 c;

// GOOD: OPTIMIZED (packed into single slot)
uint8 a;
uint8 c;
uint256 b;

// GOOD: OPTIMIZED (use uint256 for small numbers if not packing)
uint256 counter;  // cheaper than uint8 if standalone
```

**Memory vs Storage:**
```solidity
// BAD: EXPENSIVE
function sum(uint[] storage arr) internal returns (uint) {
    uint total = 0;
    for(uint i = 0; i < arr.length; i++) {
        total += arr[i];  // SLOAD each iteration
    }
    return total;
}

// GOOD: OPTIMIZED
function sum(uint[] storage arr) internal returns (uint) {
    uint total = 0;
    uint length = arr.length;  // Cache length
    for(uint i = 0; i < length;) {
        total += arr[i];
        unchecked { ++i; }  // Save gas on overflow check
    }
    return total;
}
```

**Calldata vs Memory:**
```solidity
// BAD: MORE EXPENSIVE
function process(uint[] memory data) external { }

// GOOD: CHEAPER (for external functions)
function process(uint[] calldata data) external { }
```

**Custom Errors:**
```solidity
// BAD: EXPENSIVE
require(amount > 0, "Amount must be greater than zero");

// GOOD: CHEAPER
error InvalidAmount();
if (amount == 0) revert InvalidAmount();
```

**Gas Optimization Checklist:**
- [ ] Pack storage variables into 32-byte slots
- [ ] Use `calldata` for external function parameters
- [ ] Cache storage variables in memory/stack
- [ ] Use `unchecked` for safe arithmetic
- [ ] Custom errors instead of require strings
- [ ] Immutable variables when possible
- [ ] Batch operations to reduce transaction count
- [ ] Use events instead of storage where applicable

---

## Pattern: Testing Strategy

**Use when:** Ensuring contract correctness and security.

**Testing Pyramid:**
```
Unit Tests (80%)      - Individual functions, edge cases
Integration Tests (15%) - Multi-contract interactions
Fork Tests (5%)        - Mainnet state, protocol integrations
Invariant Tests        - Fuzzing, property-based testing
```

**Foundry Example (Solidity):**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Token.sol";

contract TokenTest is Test {
    Token token;
    address alice = address(0x1);
    address bob = address(0x2);

    function setUp() public {
        token = new Token("Test", "TST");
        deal(alice, 100 ether);
    }

    function testTransfer() public {
        vm.startPrank(alice);
        token.transfer(bob, 100);
        assertEq(token.balanceOf(bob), 100);
        vm.stopPrank();
    }

    function testFuzzTransfer(uint256 amount) public {
        vm.assume(amount <= token.balanceOf(alice));
        vm.prank(alice);
        token.transfer(bob, amount);
        assertEq(token.balanceOf(bob), amount);
    }

    function invariant_totalSupplyConstant() public {
        assertEq(token.totalSupply(), 1_000_000e18);
    }
}
```

**Anchor Example (Rust/Solana):**
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use anchor_lang::prelude::*;

    #[test]
    fn test_initialize() {
        let program_id = Pubkey::new_unique();
        let mut accounts = initialize_accounts();

        let result = initialize(
            Context::new(&program_id, &mut accounts, &[], BTreeMap::new()),
            100
        );

        assert!(result.is_ok());
    }
}
```

**Testing Checklist:**
- [ ] Unit tests for all functions
- [ ] Edge cases (zero values, max uint256, empty arrays)
- [ ] Access control tests (unauthorized calls fail)
- [ ] Reentrancy attack tests
- [ ] Fuzz testing with randomized inputs
- [ ] Fork tests against live protocols
- [ ] Gas benchmarking
- [ ] Integration tests for multi-contract flows
- [ ] Invariant tests for protocol properties
- [ ] Test coverage >90%

---

## Pattern: Upgradeable Contracts

**Use when:** Protocol needs future improvements or bug fixes.

**Proxy Patterns:**

- **Transparent Proxy** (OpenZeppelin): Admin/user separation, implementation upgrades
- **UUPS** (EIP-1822): Upgrade logic in implementation, gas efficient
- **Diamond Standard** (EIP-2535): Multiple facets, modular functionality
- **Beacon Proxy**: Multiple proxies share one implementation

**Critical Considerations:**
```solidity
// GOOD: Use initializer instead of constructor
function initialize(uint256 _supply) public initializer {
    __Ownable_init();
    totalSupply = _supply;
}

// GOOD: Storage gaps for future variables
uint256[50] private __gap;

// GOOD: Namespace storage (EIP-7201)
bytes32 private constant STORAGE_LOCATION = keccak256("myprotocol.storage");
```

**Upgradeability Checklist:**

- [ ] Use initializer instead of constructor
- [ ] Include storage gaps in base contracts
- [ ] Never change order of existing state variables
- [ ] Test upgrade scenarios in fork tests
- [ ] Timelocks on upgrade functions (24-48 hours)
- [ ] Emergency pause independent of upgrade

See [references/solidity-best-practices.md](solidity-best-practices.md) for detailed proxy implementations and upgrade patterns.

---

## Pattern: DeFi Protocol Patterns

**Use when:** Building decentralized finance applications.

**Core DeFi Patterns:**

- **AMM (Automated Market Maker)**: Constant product formula (x * y = k), liquidity pools
- **Lending**: Collateralized borrowing, liquidation mechanisms, interest rate models
- **Staking**: Reward distribution, time-weighted rewards, early withdrawal penalties
- **Yield Farming**: Multi-token rewards, boosted staking, vesting schedules

**Critical DeFi Security:**
```solidity
// GOOD: Slippage protection
function swap(uint amountIn, uint minAmountOut) external {
    uint amountOut = calculateSwap(amountIn);
    require(amountOut >= minAmountOut, "Slippage exceeded");
}

// GOOD: Oracle validation
function getPrice() internal view returns (uint) {
    uint price = oracle.latestAnswer();
    require(block.timestamp - oracle.latestTimestamp() < 1 hours, "Stale price");
    return price;
}
```

**DeFi Checklist:**
- [ ] Slippage protection on swaps
- [ ] Price oracle integration (TWAP/Chainlink)
- [ ] Flash loan protection (balance checks)
- [ ] Liquidation mechanisms tested
- [ ] Interest rate models validated
- [ ] Emergency withdrawal function

See [references/solidity-best-practices.md](solidity-best-practices.md) for detailed DeFi implementations (AMM, lending, staking).

---

## Pattern: Token Standards

**Use when:** Implementing fungible or non-fungible tokens.

**Standard Implementations:**

- **ERC20**: Fungible tokens (use OpenZeppelin ERC20)
- **ERC721**: NFTs with unique IDs (ERC721URIStorage for metadata)
- **ERC1155**: Multi-token (fungible + NFT in one contract)
- **SPL Token**: Solana fungible tokens (via Anchor)
- **Jetton**: TON fungible tokens (FunC/Tact)

**Quick Reference:**
```solidity
// ERC20 with OpenZeppelin
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
contract MyToken is ERC20 {
    constructor() ERC20("MyToken", "MTK") {
        _mint(msg.sender, 1_000_000e18);
    }
}
```

**Token Checklist:**

- [ ] Decimal precision defined (typically 18 for ERC20)
- [ ] Total supply cap or mint authority control
- [ ] Burn functionality if needed
- [ ] Pausable for emergencies (OpenZeppelin Pausable)
- [ ] Permit (EIP-2612) for gasless approvals

See [references/solidity-best-practices.md](solidity-best-practices.md) for ERC721, ERC1155, and chain-specific token implementations.

---

# Templates

See `assets/` directory for blockchain-specific implementations, organized by chain:

- `ethereum/template-solidity-hardhat.md` - Ethereum/EVM with Hardhat, OpenZeppelin, Ethers.js
- `ethereum/template-solidity-foundry.md` - Ethereum/EVM with Foundry, Forge, Cast
- `solana/template-rust-anchor.md` - Solana with Anchor framework, SPL tokens
- `cosmos/template-cosmwasm.md` - Cosmos ecosystem with CosmWasm smart contracts
- `bitcoin/template-bitcoin-core.md` - Bitcoin development with Bitcoin Core

More templates can be added for other chains (Polkadot Substrate, Avalanche, Near, etc.)

---

# Resources

**Best Practices Guides** (`references/`)

- `backend-integration-best-practices.md` - .NET/C# crypto integration patterns including:
  - CQRS with MediatR for payment/wallet commands
  - Railway-oriented programming with FluentResults
  - Multi-provider architecture (TON, Fireblocks, TG Wallet)
  - Webhook signature validation (HMAC, constant-time comparison)
  - Event-driven architecture with Kafka
  - Transaction lifecycle state machines
  - HTTP client resilience (Polly policies)
  - Testing patterns (fixtures, Wiremock, testcontainers)
- `blockchain-best-practices.md` - Universal blockchain patterns including:
  - Smart contract architecture and design
  - Security patterns and vulnerability prevention
  - Gas optimization techniques
  - Testing strategies (unit, integration, fork, invariant)
  - Deployment and verification workflows
  - Multi-chain considerations
- `solidity-best-practices.md` - Ethereum/EVM-specific patterns including:
  - Solidity language features and pitfalls
  - OpenZeppelin library usage
  - EVM opcodes and gas costs
  - Proxy patterns and upgradeability
  - DeFi protocol implementations
  - MEV protection strategies
- `rust-solana-best-practices.md` - Solana-specific patterns including:
  - Anchor framework patterns
  - Program Derived Addresses (PDAs)
  - Cross-Program Invocations (CPIs)
  - Account data structures
  - SPL token integration
  - Solana transaction optimization
- `cosmwasm-best-practices.md` - Cosmos-specific patterns including:
  - CosmWasm contract structure
  - IBC (Inter-Blockchain Communication)
  - Cosmos SDK integration
  - Token standards (CW20, CW721)
  - Governance modules
- `ton-best-practices.md` - TON-specific patterns including:
  - FunC and Tact language features
  - TON Virtual Machine (TVM) optimization
  - Jetton and NFT standards
  - TON Connect integration
  - Telegram Bot API patterns

**Smart Contract Security** (see [software-security-appsec](../../software-security-appsec/SKILL.md) skill):

- [../software-security-appsec/references/smart-contract-security-auditing.md](../../software-security-appsec/references/smart-contract-security-auditing.md) - Comprehensive smart contract security:
  - Common vulnerability patterns (reentrancy, access control, oracle manipulation)
  - Audit checklists and methodologies
  - Formal verification tools (Slither, Mythril, Echidna, Certora)
  - Testing frameworks and coverage strategies
  - Bug bounty program setup

**External Documentation:**
See [data/sources.json](../data/sources.json) for official documentation links and learning resources.

---

# Backend Integration Patterns

## Pattern: Multi-Provider Architecture

**Use when:** Building enterprise crypto integrations that need multiple blockchain providers.

**Provider Abstraction:**
```csharp
// Abstract interface for provider operations
public interface ICryptoProvider
{
    CryptoProvider ProviderType { get; }
    Task<Result<WalletInfo>> CreateWalletAsync(string userId, Currency currency);
    Task<Result<TransactionInfo>> CreatePayoutAsync(PayoutRequest request);
}

// Provider selection based on currency/network
public class CalculateProviderService : ICalculateProviderService
{
    public Task<CryptoProvider> GetCryptoProviderAsync(Currency currency, CryptoNetwork network)
    {
        return (currency, network) switch
        {
            (Currency.TON, CryptoNetwork.TON) => CryptoProvider.TonDirect,
            (Currency.USDT, CryptoNetwork.TON) => CryptoProvider.TonDirect,  // Jetton
            (Currency.ETH, CryptoNetwork.Ethereum) => CryptoProvider.Fireblocks,
            _ => CryptoProvider.Fireblocks  // Default custodial
        };
    }
}
```

**Provider Types:**
- **Direct blockchain** (TonDirect): Non-custodial, direct RPC calls
- **Custodial** (Fireblocks): Managed keys, compliance features, AML
- **Embedded wallets** (TG Wallet): App-integrated wallets

---

## Pattern: CQRS with MediatR

**Use when:** Building crypto payment/wallet services with complex business logic.

```csharp
// Command with railway-oriented result
public record CreatePaymentCommand(
    string UserId,
    decimal Amount,
    Currency Currency
) : IRequest<Result<PaymentInfo>>;

// Handler with provider routing
public class CreatePaymentHandler : IRequestHandler<CreatePaymentCommand, Result<PaymentInfo>>
{
    public async Task<Result<PaymentInfo>> Handle(CreatePaymentCommand request, CancellationToken ct)
    {
        var provider = await _providerService.GetCryptoProviderAsync(request.Currency);

        return provider switch
        {
            CryptoProvider.TonDirect => await _mediator.Send(new TonCreatePaymentCommand(request)),
            CryptoProvider.Fireblocks => await _mediator.Send(new FireblocksCreatePaymentCommand(request)),
            _ => Result.Fail("Unsupported provider")
        };
    }
}
```

---

## Pattern: Webhook Security

**Use when:** Receiving webhooks from custodial providers (Fireblocks, etc.).

```csharp
// HMAC signature validation with constant-time comparison
public bool ValidateSignature(string payload, string signature, string timestamp)
{
    var expectedSignature = ComputeHmacSha256($"{timestamp}.{payload}", _secret);
    return CryptographicOperations.FixedTimeEquals(
        Encoding.UTF8.GetBytes(signature),
        Encoding.UTF8.GetBytes(expectedSignature));
}

// Authentication handler for webhook endpoints
[Authorize(AuthenticationSchemes = "FireblocksWebhook")]
[HttpPost("webhooks/fireblocks")]
public async Task<IActionResult> HandleWebhook([FromBody] WebhookPayload payload)
{
    await _kafkaProducer.PublishAsync(new TransactionWebhookMessage(payload));
    return Ok();  // Always acknowledge receipt
}
```

**Security Checklist:**
- [ ] Constant-time signature comparison (prevent timing attacks)
- [ ] Timestamp validation (prevent replay attacks)
- [ ] Idempotency handling (duplicate webhook delivery)
- [ ] Async processing via message queue

---

## Pattern: Transaction Lifecycle

**Use when:** Tracking crypto transaction states from creation to completion.

```csharp
// State machine for transactions
public enum TransactionStatus { Created, Pending, Confirming, Completed, Failed }

public class TransactionStateMachine
{
    private static readonly Dictionary<(TransactionStatus, TransactionEvent), TransactionStatus>
        _transitions = new()
    {
        { (TransactionStatus.Created, TransactionEvent.Submitted), TransactionStatus.Pending },
        { (TransactionStatus.Pending, TransactionEvent.Broadcast), TransactionStatus.Confirming },
        { (TransactionStatus.Confirming, TransactionEvent.Confirmed), TransactionStatus.Completed },
        { (TransactionStatus.Pending, TransactionEvent.Rejected), TransactionStatus.Failed },
    };
}

// Background monitoring service
public class TransactionMonitoringService : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var pending = await _repository.GetPendingTransactionsAsync();
            foreach (var tx in pending)
            {
                var status = await _blockchainClient.GetTransactionStatusAsync(tx.TxHash);
                if (status != tx.Status)
                    await _mediator.Send(new UpdateTransactionStatusCommand(tx.Id, status));
            }
            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
        }
    }
}
```

---

## Pattern: Event-Driven Crypto Payments

**Use when:** Building scalable payment processing with Kafka.

```csharp
// Publish payment events
public class PaymentCompletedHandler : INotificationHandler<PaymentCompletedNotification>
{
    public async Task Handle(PaymentCompletedNotification notification, CancellationToken ct)
    {
        await _kafkaProducer.PublishAsync(new CryptoPaymentReceivedMessage
        {
            PaymentId = notification.PaymentId,
            Amount = notification.Amount.ToString(),
            Currency = notification.Currency.ToString(),
            TxHash = notification.TxHash
        });
    }
}

// Consume webhook messages
public class WebhookMessageHandler : IMessageHandler<TransactionWebhookMessage>
{
    public async Task HandleAsync(ConsumeResult<string, TransactionWebhookMessage> message, CancellationToken ct)
    {
        var result = await _mediator.Send(new ProcessTransactionCommand(message.Value));
        if (result.IsFailed)
            throw new MessageProcessingException(result.Errors.First().Message);
    }
}
```

See [references/backend-integration-best-practices.md](backend-integration-best-practices.md) for complete patterns.

---

# State Management Patterns

## On-Chain vs Off-Chain Data

**Use when:** Deciding data storage strategy.

| Data Type | Storage | Reason |
|-----------|---------|--------|
| Balances, ownership | On-chain | Security-critical, needs consensus |
| NFT metadata | IPFS + on-chain URI | Immutability + cost efficiency |
| Historical data | The Graph/subgraph | Query efficiency |
| User preferences | Off-chain DB | Mutable, non-critical |
| Large files | Arweave/Filecoin | Permanent storage |

---

# Cross-Chain Patterns

**Use when:** Building multi-chain protocols.

**Bridging Strategies:**
1. Lock-and-Mint (centralized/federated)
2. Burn-and-Mint (requires trust)
3. Liquidity Pools (Hop Protocol)
4. Atomic Swaps
5. IBC (Inter-Blockchain Communication - Cosmos)

**Bridge Security Considerations:**
- [ ] Validator set decentralization
- [ ] Fraud proof mechanisms
- [ ] Rate limiting on withdrawals
- [ ] Multi-signature requirements
- [ ] Circuit breakers for anomalies

---

# END
