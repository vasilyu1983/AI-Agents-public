# Blockchain Best Practices - Universal Patterns

Chain-agnostic best practices for building secure, scalable blockchain applications.

---

## Table of Contents

1. [Architecture Patterns](#architecture-patterns)
2. [Security Principles](#security-principles)
3. [State Management](#state-management)
4. [Economic Security](#economic-security)
5. [Gas Optimization (Universal)](#gas-optimization-universal)
6. [Cross-Chain Patterns](#cross-chain-patterns)
7. [Testing Strategies](#testing-strategies)
8. [Deployment Best Practices](#deployment-best-practices)
9. [Monitoring & Observability](#monitoring--observability)
10. [Governance Patterns](#governance-patterns)
11. [Common Pitfalls (All Chains)](#common-pitfalls-all-chains)
12. [Documentation Standards](#documentation-standards)
13. [Production Checklist](#production-checklist)
14. [Resources](#resources)

## Architecture Patterns

### Separation of Concerns

**Contracts should follow single responsibility principle:**

```
Protocol Architecture:
├── Core Logic (business rules)
├── Storage Layer (state management)
├── Access Control (permissions)
├── Treasury (funds management)
└── Governance (upgrades/parameters)
```

**Example (Solidity):**
```solidity
// BEST: Separated concerns
contract TokenLogic {
    function transfer(address to, uint amount) external;
}

contract TokenStorage {
    mapping(address => uint) public balances;
}

contract TokenGovernance {
    function updateParameters() external onlyGovernor;
}

// AVOID: God contract
contract MonolithicToken {
    // All logic, storage, governance in one contract
}
```

### Fail-Safe Defaults

**Whitelist over blacklist:**
```solidity
// BEST: Whitelist approved addresses
mapping(address => bool) public approvedUsers;

function transfer(address to) public {
    require(approvedUsers[to], "Not approved");
}

// AVOID: Blacklist default allows everyone
mapping(address => bool) public blockedUsers;

function transfer(address to) public {
    require(!blockedUsers[to], "Blocked");  // Default allows everyone
}
```

---

## Security Principles

### Defense in Depth

**Multiple layers of security:**

1. **Input Validation**
   ```solidity
   function withdraw(uint amount) public {
       require(amount > 0, "Zero amount");
       require(amount <= balances[msg.sender], "Insufficient balance");
       require(amount <= withdrawalLimit, "Exceeds limit");
   }
   ```

2. **State Protection**
   ```solidity
   modifier nonReentrant() {
       require(!locked, "Reentrant call");
       locked = true;
       _;
       locked = false;
   }
   ```

3. **Access Control**
   ```solidity
   modifier onlyAuthorized() {
       require(hasRole(AUTHORIZED_ROLE, msg.sender), "Unauthorized");
       _;
   }
   ```

4. **Circuit Breakers**
   ```solidity
   bool public paused;

   modifier whenNotPaused() {
       require(!paused, "Contract paused");
       _;
   }
   ```

### Least Privilege Principle

**Grant minimum necessary permissions:**

```solidity
// GOOD: GOOD: Role-based access
bytes32 public constant MINTER_ROLE = keccak256("MINTER");
bytes32 public constant BURNER_ROLE = keccak256("BURNER");
bytes32 public constant PAUSER_ROLE = keccak256("PAUSER");

function mint(address to, uint amount) public onlyRole(MINTER_ROLE) {
    _mint(to, amount);
}

// BAD: BAD: Single admin has all powers
address public admin;

function mint(address to, uint amount) public {
    require(msg.sender == admin);
    _mint(to, amount);
}
```

---

## State Management

### Atomic Transactions

**Ensure all-or-nothing operations:**

```solidity
// GOOD: GOOD: Atomic swap
function atomicSwap(address tokenA, address tokenB, uint amountA, uint amountB) public {
    require(IERC20(tokenA).transferFrom(msg.sender, address(this), amountA));
    require(IERC20(tokenB).transfer(msg.sender, amountB));
    // Both succeed or both revert
}

// BAD: BAD: Partial state changes possible
function partialSwap(address tokenA, address tokenB) public {
    IERC20(tokenA).transferFrom(msg.sender, address(this), 100);
    // If next line fails, first transfer already happened
    IERC20(tokenB).transfer(msg.sender, 100);
}
```

### Immutability Where Possible

```solidity
// GOOD: Critical parameters immutable
uint256 public immutable VESTING_DURATION;
address public immutable TREASURY;

constructor(uint256 duration, address treasury) {
    VESTING_DURATION = duration;
    TREASURY = treasury;
}

// [WARNING] Mutable parameters need governance
uint256 public feePercentage;  // Can be changed by governance
```

---

## Economic Security

### Sybil Resistance

**Prevent spam/DoS with economic costs:**

```solidity
// GOOD: Require minimum stake
mapping(address => uint) public stakes;
uint public constant MIN_STAKE = 1 ether;

function propose(bytes memory data) public {
    require(stakes[msg.sender] >= MIN_STAKE, "Insufficient stake");
    // Process proposal
}

// GOOD: Charge fees for operations
function create() public payable {
    require(msg.value >= CREATION_FEE, "Insufficient fee");
    // Create resource
}
```

### Flash Loan Protection

```solidity
// GOOD: Validate balances at transaction end
uint256 private constant SNAPSHOT_ID = type(uint256).max;

modifier noFlashLoan() {
    uint256 balanceBefore = token.balanceOf(address(this));
    _;
    require(
        token.balanceOf(address(this)) >= balanceBefore,
        "Flash loan detected"
    );
}

// GOOD: Use TWAP instead of spot prices
function getPrice() public view returns (uint256) {
    return oracle.getTWAP(3600);  // 1-hour average
}
```

---

## Gas Optimization (Universal)

### Minimize Storage Operations

**Storage is expensive across all chains:**

```solidity
// BAD: EXPENSIVE: Multiple storage writes
function badUpdate(uint[] calldata values) external {
    for (uint i = 0; i < values.length; i++) {
        data[i] = values[i];  // SSTORE each iteration
    }
}

// GOOD: OPTIMIZED: Batch operations
function goodUpdate(uint[] calldata values) external {
    uint length = values.length;
    for (uint i = 0; i < length;) {
        data[i] = values[i];
        unchecked { ++i; }
    }
}
```

### Event Over Storage

**For historical data, use events:**

```solidity
// BAD: EXPENSIVE: Store entire history
struct Trade {
    address buyer;
    uint amount;
    uint timestamp;
}
Trade[] public trades;  // Growing array in storage

function recordTrade(address buyer, uint amount) internal {
    trades.push(Trade(buyer, amount, block.timestamp));
}

// GOOD: CHEAP: Emit events
event TradeRecorded(address indexed buyer, uint amount, uint timestamp);

function recordTrade(address buyer, uint amount) internal {
    emit TradeRecorded(buyer, amount, block.timestamp);
}
```

---

## Cross-Chain Patterns

### Message Verification

```solidity
// GOOD: Verify cross-chain messages
function processMessage(
    bytes memory message,
    bytes memory signatures
) external {
    bytes32 messageHash = keccak256(message);
    require(
        verifySignatures(messageHash, signatures),
        "Invalid signatures"
    );

    // Process verified message
}
```

### Lock-and-Mint Bridge

```solidity
// Chain A: Lock tokens
function lockTokens(uint amount, bytes32 destinationChain) external {
    token.transferFrom(msg.sender, address(this), amount);
    lockedBalance += amount;

    emit TokensLocked(msg.sender, amount, destinationChain);
}

// Chain B: Mint wrapped tokens
function mintWrapped(address to, uint amount, bytes memory proof) external {
    require(verifyBridgeProof(proof), "Invalid proof");
    wrappedToken.mint(to, amount);
}
```

---

## Testing Strategies

### Invariant Testing

**Define and test protocol invariants:**

```solidity
// Invariant: Total supply equals sum of all balances
function invariant_totalSupply() public {
    uint sum = 0;
    for (uint i = 0; i < users.length; i++) {
        sum += balanceOf(users[i]);
    }
    assertEq(totalSupply(), sum);
}

// Invariant: Reserves maintain constant product
function invariant_constantProduct() public {
    uint k = reserve0 * reserve1;
    assertGe(k, MINIMUM_LIQUIDITY ** 2);
}
```

### Fork Testing

**Test against live protocols:**

```solidity
// Test interaction with mainnet Uniswap
function testForkSwap() public {
    vm.createSelectFork("mainnet", 18000000);

    IUniswapV2Router router = IUniswapV2Router(UNISWAP_ROUTER);
    // Test swap logic
}
```

---

## Deployment Best Practices

### Deterministic Deployment

**Use CREATE2 for predictable addresses:**

```solidity
function deploy(bytes32 salt) public returns (address) {
    return address(new Contract{salt: salt}());
}

// Address can be predicted before deployment
function predictAddress(bytes32 salt) public view returns (address) {
    return address(uint160(uint(keccak256(abi.encodePacked(
        bytes1(0xff),
        address(this),
        salt,
        keccak256(type(Contract).creationCode)
    )))));
}
```

### Multi-Signature Deployment

```solidity
// GOOD: Deploy with multi-sig as owner
constructor() {
    transferOwnership(MULTISIG_ADDRESS);
}

// GOOD: Timelock for critical operations
uint256 public constant TIMELOCK_DELAY = 2 days;

mapping(bytes32 => uint256) public queuedTransactions;

function queueTransaction(bytes memory data) public onlyOwner {
    bytes32 txHash = keccak256(data);
    queuedTransactions[txHash] = block.timestamp + TIMELOCK_DELAY;
}

function executeTransaction(bytes memory data) public onlyOwner {
    bytes32 txHash = keccak256(data);
    require(
        queuedTransactions[txHash] != 0 &&
        block.timestamp >= queuedTransactions[txHash],
        "Too early"
    );
    // Execute
}
```

---

## Monitoring & Observability

### Event Design

**Emit comprehensive events:**

```solidity
// GOOD: GOOD: Indexed fields for filtering, all data included
event Transfer(
    address indexed from,
    address indexed to,
    uint256 amount,
    bytes32 indexed txId,
    uint256 timestamp
);

// BAD: BAD: Missing critical data
event Transfer(address from, address to);
```

### State Validation

```solidity
// GOOD: Internal accounting checks
modifier validateState() {
    uint balanceBefore = address(this).balance;
    _;
    uint balanceAfter = address(this).balance;

    // Ensure internal accounting matches actual balance
    require(
        balanceAfter >= internalBalance,
        "State mismatch"
    );
}
```

---

## Governance Patterns

### Proposal-Vote-Execute

```solidity
enum ProposalState { Pending, Active, Succeeded, Executed, Canceled }

struct Proposal {
    uint256 id;
    address proposer;
    bytes calldatas;
    uint256 forVotes;
    uint256 againstVotes;
    ProposalState state;
    uint256 deadline;
}

function propose(bytes memory calldata_) public returns (uint256) {
    require(votingPower[msg.sender] >= PROPOSAL_THRESHOLD);

    uint256 proposalId = nextProposalId++;
    proposals[proposalId] = Proposal({
        id: proposalId,
        proposer: msg.sender,
        calldatas: calldata_,
        forVotes: 0,
        againstVotes: 0,
        state: ProposalState.Active,
        deadline: block.timestamp + VOTING_PERIOD
    });

    return proposalId;
}
```

### Quorum & Voting Power

```solidity
// GOOD: Quadratic voting to reduce whale power
function vote(uint256 proposalId, bool support) public {
    uint256 votes = sqrt(votingPower[msg.sender]);
    if (support) {
        proposals[proposalId].forVotes += votes;
    } else {
        proposals[proposalId].againstVotes += votes;
    }
}

// GOOD: Quorum requirement
function execute(uint256 proposalId) public {
    Proposal storage proposal = proposals[proposalId];
    require(proposal.state == ProposalState.Succeeded);

    uint256 totalVotes = proposal.forVotes + proposal.againstVotes;
    require(totalVotes >= QUORUM, "Quorum not reached");
    require(proposal.forVotes > proposal.againstVotes, "Votes failed");

    // Execute proposal
}
```

---

## Common Pitfalls (All Chains)

### Rounding Errors

```solidity
// BAD: VULNERABLE: Always rounds down in user's favor
uint256 fee = (amount * FEE_RATE) / 10000;

// GOOD: SECURE: Round up for fees
uint256 fee = (amount * FEE_RATE + 9999) / 10000;
```

### Precision Loss

```solidity
// BAD: VULNERABLE: Division before multiplication
uint256 result = (amount / price) * multiplier;

// GOOD: SECURE: Multiplication before division
uint256 result = (amount * multiplier) / price;
```

### External Dependency Risk

```solidity
// BAD: RISKY: Direct dependency
function getPrice() public view returns (uint256) {
    return externalOracle.latestPrice();  // What if it fails?
}

// GOOD: RESILIENT: Try-catch with fallback
function getPrice() public view returns (uint256) {
    try externalOracle.latestPrice() returns (uint256 price) {
        return price;
    } catch {
        return fallbackOracle.getPrice();
    }
}
```

---

## Documentation Standards

### NatSpec Comments

```solidity
/// @title Token Contract
/// @author Your Name
/// @notice Implements ERC20 with additional features
/// @dev Uses OpenZeppelin's ERC20 implementation

/**
 * @notice Transfer tokens to a recipient
 * @dev Emits Transfer event on success
 * @param to The recipient address
 * @param amount The amount to transfer
 * @return success True if transfer succeeded
 */
function transfer(address to, uint256 amount) public returns (bool success) {
    // Implementation
}
```

### Architecture Documentation

**Every protocol should document:**
1. System architecture diagram
2. Contract interaction flows
3. Access control matrix
4. Economic model (tokenomics)
5. Upgrade procedures
6. Emergency procedures
7. Known limitations

---

## Production Checklist

**Before mainnet deployment:**

- [ ] Professional security audit completed
- [ ] All tests passing (100% coverage)
- [ ] Fuzz tests for critical functions
- [ ] Fork tests for external integrations
- [ ] Multi-sig wallet as owner
- [ ] Timelock on critical functions
- [ ] Circuit breaker implemented
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented
- [ ] Bug bounty program prepared
- [ ] Contract verified on explorer
- [ ] Documentation complete
- [ ] Deployment procedure tested on testnet

---

## Resources

- [Smart Contract Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [DeFi Security Summit](https://defisecuritysummit.org/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Trail of Bits Security Reviews](https://github.com/trailofbits/publications)
