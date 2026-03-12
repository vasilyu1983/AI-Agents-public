# Solidity Best Practices - Ethereum/EVM Development

Production-grade patterns for secure, gas-optimized Solidity smart contracts.

**Last Updated:** 2026-01-17 (includes Jan 2026 AI auditing tools, security patterns)

---

## Table of Contents

1. [2024-2025 Industry Updates](#2024-2025-industry-updates)
2. [Security Patterns](#security-patterns)
3. [Gas Optimization](#gas-optimization)
4. [Design Patterns](#design-patterns)
5. [Testing Strategies](#testing-strategies)
6. [Upgradeable Contracts](#upgradeable-contracts)
7. [Common Pitfalls](#common-pitfalls)

---

## 2024-2025 Industry Updates

### Critical Statistics

**Reality check (numbers change quickly)**:

- Security incidents regularly cause large losses across the ecosystem
- Access control, signing/custody, and integration bugs remain top incident drivers
- Use WebSearch before quoting specific figures or rankings

### Solidity Version Recommendations

**Use Solidity 0.8.x (latest stable)** for built-in protections:

- Automatic overflow/underflow checks (no SafeMath needed)
- Custom errors (gas efficient error handling)
- Improved ABI encoder

```solidity
// RECOMMENDED: Pin to the latest stable 0.8.x in your toolchain (Foundry/Hardhat).
// Keep the pragma compatible with your pinned compiler version.
pragma solidity ^0.8.0;

error InvalidAmount();  // Custom errors are standard

contract ModernContract {
    function transfer(uint256 amount) external {
        if (amount == 0) revert InvalidAmount();  // Gas efficient
        // Overflow protection built-in
    }
}
```

### Security Tools (Jan 2026)

**Static Analysis:**

| Tool | Language | Key Feature | Best For |
|------|----------|-------------|----------|
| Slither 0.10.x+ | Python | 92+ detectors, cross-contract reentrancy | Every project |
| Aderyn | Rust | 2-5x faster than Slither | Large codebases |
| MythX | Cloud | Integrates Slither, Mythril, Oyente | Comprehensive scans |

**Fuzzing:**

| Tool | Type | Key Feature | Best For |
|------|------|-------------|----------|
| Echidna | Property-based | Haskell-powered, stateful fuzzing | Complex state machines |
| Medusa | Parallelized | Go-based, multi-core fuzzing | CI/CD pipelines |
| Foundry Fuzz | Inline | Native Solidity, fast iteration | Daily development |

**AI-Assisted Auditing (New in 2025-2026):**

| Tool | Key Feature | When to Use |
|------|-------------|-------------|
| Sherlock AI | ML + rule-based | Pre-audit preparation |
| Olympix | DevSecOps integration | CI/CD security gates |
| AuditBase | 423+ detectors, LLM-powered | Business logic review |
| Almanax | "AI Security Engineer", Web3 Atlas dataset | Deep vulnerability analysis |

> **AI-assisted review**: Use AI tooling for pre-audit preparation and coverage, not for final security decisions. Treat outputs as untrusted and reproduce findings with deterministic tools, tests, and manual review.

**Mutation Testing:**

- **SuMo**: Solidity-specific mutation testing to assess test suite quality. Injects faults and verifies tests catch them.

### Modern Development Practices (2025)

**Explicit Visibility (Critical)**:
```solidity
// BAD: Implicit visibility
function transfer() { }  // Defaults to public (dangerous)

// GOOD: Always explicit
function transfer() external { }  // Clear intent
function _internal() internal { }  // Private helpers
```

**Trusted Libraries**:

- OpenZeppelin Contracts 5.x (updated for 0.8.x)
- Solady (gas-optimized alternatives)
- Solmate (minimalist implementations)

### 84-Point Security Framework (2025)

Recent research consolidated into comprehensive framework:

- 36 design patterns
- 48 best practices
- 12 security categories
- Covers Ethereum and EVM-compatible chains

**Categories**: Access Control, Arithmetic Safety, Reentrancy Protection, Oracle Security, Proxy Patterns, Gas Optimization, Testing Strategies, Deployment Safety, Monitoring, Incident Response, Governance, Upgradeability

---

## Security Patterns

### Reentrancy Protection

**Always use Checks-Effects-Interactions pattern:**

```solidity
// VULNERABLE: State change after external call
function withdraw() public {
    uint amount = balances[msg.sender];
    (bool success,) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] = 0;  // State change AFTER external call
}

// SECURE: State change before external call
function withdraw() public nonReentrant {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;  // State change BEFORE external call
    (bool success,) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

**Use OpenZeppelin ReentrancyGuard:**
```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract MyContract is ReentrancyGuard {
    function withdraw() public nonReentrant {
        // Protected function
    }
}
```

### Access Control

```solidity
import "@openzeppelin/contracts/access/AccessControl.sol";

contract MyContract is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) {
        _mint(to, amount);
    }
}
```

### Integer Safety (Solidity 0.8+)

```solidity
// GOOD: Automatic overflow checks in 0.8+
uint256 public count;

function increment() public {
    count += 1;  // Reverts on overflow
}

// Use unchecked only when safe
function _calculateFee(uint256 amount) internal pure returns (uint256) {
    unchecked {
        return amount / 100;  // Safe, won't overflow
    }
}
```

### Oracle Security

```solidity
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceConsumer {
    AggregatorV3Interface internal priceFeed;
    uint256 private constant STALE_PRICE_DELAY = 3600; // 1 hour

    function getLatestPrice() public view returns (int) {
        (
            uint80 roundId,
            int price,
            ,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        require(price > 0, "Invalid price");
        require(updatedAt > 0, "Round not complete");
        require(answeredInRound >= roundId, "Stale price");
        require(block.timestamp - updatedAt < STALE_PRICE_DELAY, "Price too old");

        return price;
    }
}
```

---

## Gas Optimization

### 2024-2025 Gas Optimization Insights

**Storage is 100x More Expensive Than Memory**:

- SSTORE (write new value): 20,000 gas
- SSTORE (update existing): 5,000 gas
- SLOAD (read): ~800 gas
- Memory operations: ~3-6 gas

**Data Type Selection (Critical)**:

```solidity
// EXPENSIVE: uint8 requires conversion to uint256
uint8 counter;  // EVM converts to 256-bit, costs extra gas

// CHEAPER: uint256 is native EVM word size
uint256 counter;  // No conversion needed

// EXCEPTION: Use smaller types ONLY when packing
struct Packed {
    uint128 a;  // Fits in one slot with b
    uint128 b;  // Together = 256 bits = 1 slot
}
```

**Custom Errors (Solidity 0.8.x+)**:

```solidity
// EXPENSIVE: String storage in bytecode
require(amount > 0, "Amount must be greater than zero");

// CHEAP: Custom errors with ABI encoding
error InsufficientAmount(uint256 provided, uint256 required);
if (amount == 0) revert InsufficientAmount(amount, minAmount);
```

**Calculation vs Storage Trade-off**:

```solidity
// EXPENSIVE: Store derived values
uint256 public halfSupply = totalSupply / 2;  // SSTORE cost

// CHEAP: Calculate on-demand
function halfSupply() public view returns (uint256) {
    return totalSupply / 2;  // Computation << storage
}
```

### Storage Packing

```solidity
// EXPENSIVE: 3 storage slots
contract Inefficient {
    uint8 a;      // Slot 0
    uint256 b;    // Slot 1
    uint8 c;      // Slot 2
}

// OPTIMIZED: 2 storage slots
contract Efficient {
    uint8 a;      // Slot 0
    uint8 c;      // Slot 0 (packed)
    uint256 b;    // Slot 1
}
```

### Calldata vs Memory

```solidity
// MORE EXPENSIVE: Copies to memory
function process(uint[] memory data) external {
    // Copies to memory
}

// CHEAPER: For external functions
function process(uint[] calldata data) external {
    // No copy, reads directly
}
```

### Custom Errors

```solidity
// EXPENSIVE: String in bytecode
require(amount > 0, "Amount must be greater than zero");

// CHEAPER: Custom error
error InvalidAmount();
if (amount == 0) revert InvalidAmount();
```

### Caching Storage Reads

```solidity
// EXPENSIVE: Multiple SLOADs
function badExample() public {
    for (uint i = 0; i < array.length; i++) {  // SLOAD every iteration
        // process array[i]
    }
}

// OPTIMIZED: Cache length
function goodExample() public {
    uint length = array.length;  // Single SLOAD
    for (uint i = 0; i < length;) {
        // process array[i]
        unchecked { ++i; }
    }
}
```

### Immutable and Constant

```solidity
contract Optimized {
    // Embedded in bytecode (no storage)
    uint256 public constant MAX_SUPPLY = 1_000_000;

    // Set once in constructor, then embedded
    address public immutable owner;

    constructor() {
        owner = msg.sender;
    }
}
```

---

## Design Patterns

### Factory Pattern

```solidity
contract TokenFactory {
    event TokenCreated(address indexed token, address indexed creator);

    function createToken(string memory name, string memory symbol) public returns (address) {
        Token token = new Token(name, symbol, msg.sender);
        emit TokenCreated(address(token), msg.sender);
        return address(token);
    }
}
```

### Pull Over Push Pattern

```solidity
// RECOMMENDED: Users withdraw (pull pattern)
contract Auction {
    mapping(address => uint256) public pendingReturns;

    function bid() public payable {
        if (highestBid != 0) {
            pendingReturns[highestBidder] += highestBid;  // Record debt
        }
        highestBid = msg.value;
        highestBidder = msg.sender;
    }

    function withdraw() public {
        uint amount = pendingReturns[msg.sender];
        pendingReturns[msg.sender] = 0;
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
    }
}
```

### Circuit Breaker

```solidity
import "@openzeppelin/contracts/security/Pausable.sol";

contract EmergencyStop is Pausable, Ownable {
    function deposit() public payable whenNotPaused {
        // Normal operation
    }

    function emergencyStop() public onlyOwner {
        _pause();
    }

    function resume() public onlyOwner {
        _unpause();
    }
}
```

---

## Testing Strategies

### Foundry Test Example

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
        token = new Token();
        deal(alice, 100 ether);
        deal(bob, 100 ether);
    }

    function testTransfer() public {
        vm.prank(alice);
        token.transfer(bob, 100);
        assertEq(token.balanceOf(bob), 100);
    }

    function testFuzzTransfer(uint256 amount) public {
        vm.assume(amount <= token.balanceOf(alice));
        vm.prank(alice);
        token.transfer(bob, amount);
        assertEq(token.balanceOf(bob), amount);
    }

    function testRevertUnauthorized() public {
        vm.expectRevert(Unauthorized.selector);
        vm.prank(bob);
        token.mint(alice, 1000);
    }

    function invariant_totalSupplyConstant() public {
        assertEq(token.totalSupply(), 1_000_000e18);
    }
}
```

### Fork Testing

```solidity
contract ForkTest is Test {
    IERC20 dai = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);

    function testFork() public {
        vm.createSelectFork("mainnet");
        assertEq(dai.decimals(), 18);
    }
}
```

---

## Upgradeable Contracts

### UUPS Proxy Pattern

```solidity
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract TokenV1 is Initializable, UUPSUpgradeable, OwnableUpgradeable {
    uint256 public totalSupply;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(uint256 _supply) public initializer {
        __Ownable_init();
        __UUPSUpgradeable_init();
        totalSupply = _supply;
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}

    // Storage gap for future variables
    uint256[49] private __gap;
}

// Upgrade
contract TokenV2 is TokenV1 {
    uint256 public newFeature;  // Uses first gap slot
    uint256[48] private __gap;
}
```

---

## Common Pitfalls

### tx.origin vs msg.sender

```solidity
// VULNERABLE: Phishing attack possible
function transfer(address to, uint amount) public {
    require(tx.origin == owner);  // WRONG
}

// CORRECT: Use msg.sender
function transfer(address to, uint amount) public {
    require(msg.sender == owner);
}
```

### Timestamp Manipulation

```solidity
// VULNERABLE: Miners can manipulate ~15 seconds
function claim() public {
    require(block.timestamp > deadline);  // Risky for short periods
}

// BETTER: Use block.number for short periods
function claim() public {
    require(block.number > deadlineBlock);
}
```

### Denial of Service

```solidity
// VULNERABLE: Unbounded loop can exceed gas limit
function payEveryone() public {
    for (uint i = 0; i < users.length; i++) {  // Can exceed gas limit
        users[i].transfer(amount);
    }
}

// SECURE: Pull pattern
mapping(address => uint) public balances;

function withdraw() public {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;
    msg.sender.transfer(amount);
}
```

---

## Production Checklist

Before deploying to mainnet:

**Security:**
- [ ] Reentrancy guards on all state-changing functions
- [ ] Access control on privileged functions
- [ ] Input validation with custom errors
- [ ] Oracle data validation
- [ ] No delegatecall to untrusted contracts
- [ ] Events emitted for all state changes
- [ ] Pausable for emergencies
- [ ] Audited by professional firm

**Gas Optimization:**
- [ ] Storage variables packed
- [ ] Calldata used for external functions
- [ ] Storage reads cached
- [ ] Custom errors instead of strings
- [ ] Immutable/constant where applicable
- [ ] Unchecked arithmetic where safe

**Testing:**
- [ ] 100% test coverage
- [ ] Fuzz tests for critical functions
- [ ] Fork tests for mainnet integrations
- [ ] Invariant tests for protocol properties
- [ ] Gas benchmarks documented

**Deployment:**
- [ ] No floating pragma (lock version)
- [ ] Verified on Etherscan
- [ ] Multi-sig for ownership
- [ ] Timelock for upgrades
- [ ] Monitoring and alerting setup
- [ ] Emergency response plan

---

## Resources

- [Solidity Documentation](https://docs.soliditylang.org/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Smart Contract Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [SWC Registry](https://swcregistry.io/)
- [Foundry Book](https://book.getfoundry.sh/)
