# Smart Contract Security Audit Checklist

Comprehensive security audit checklist for blockchain smart contracts focusing on vulnerability detection and exploit prevention.

---

## OWASP Smart Contract Top 10

### SC-1: Reentrancy
**Description:** External contract calls that allow attackers to recursively call back into the calling contract.

**Detection:**
```solidity
// VULNERABLE PATTERN
function withdraw() public {
    uint amount = balances[msg.sender];
    (bool success,) = msg.sender.call{value: amount}("");  // External call
    balances[msg.sender] = 0;  // State change AFTER call
}
```

**Exploit Scenario:**
1. Attacker calls `withdraw()`
2. During the `.call()`, attacker's fallback is triggered
3. Fallback calls `withdraw()` again before balance is zeroed
4. Attacker drains contract

**Mitigation:**
- Use Checks-Effects-Interactions pattern
- Apply ReentrancyGuard modifier
- Update state before external calls

**Test:**
```solidity
function testReentrancyAttack() public {
    // Deploy attack contract
    // Verify attack fails with ReentrancyGuard
}
```

---

### SC-2: Access Control
**Description:** Missing or improper access control on privileged functions.

**Vulnerable Patterns:**
```solidity
// BAD: No access control
function mint(address to, uint amount) public {
    _mint(to, amount);
}

// BAD: Using tx.origin
function withdraw() public {
    require(tx.origin == owner);  // Phishing vulnerable
}
```

**Mitigation:**
```solidity
// GOOD: Proper access control
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Secure is AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    function mint(address to, uint amount) public onlyRole(MINTER_ROLE) {
        _mint(to, amount);
    }
}
```

---

### SC-3: Arithmetic Issues
**Description:** Integer overflow/underflow vulnerabilities.

**Detection:**
- Solidity <0.8: Check for SafeMath usage
- Solidity ≥0.8: Verify appropriate use of `unchecked`
- Look for unchecked blocks with user input

**Vulnerable:**
```solidity
// Solidity 0.7.x
uint256 balance = 100;
balance = balance - 200;  // Underflows to MAX_UINT256
```

**Secure:**
```solidity
// Solidity 0.8+
uint256 balance = 100;
balance = balance - 200;  // Reverts automatically
```

---

### SC-4: Unchecked Return Values
**Description:** Not checking return values of external calls.

**Vulnerable:**
```solidity
// BAD: Ignores return value
token.transfer(recipient, amount);
```

**Secure:**
```solidity
// GOOD: Checks return value
require(token.transfer(recipient, amount), "Transfer failed");

// GOOD: Using SafeERC20
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
using SafeERC20 for IERC20;

token.safeTransfer(recipient, amount);
```

---

### SC-5: Denial of Service
**Description:** Attackers cause contract functions to become unusable.

**Patterns:**
```solidity
// BAD: VULNERABLE: Unbounded loop
function distributeRewards() public {
    for (uint i = 0; i < users.length; i++) {  // Can exceed gas limit
        users[i].transfer(reward);
    }
}

// BAD: VULNERABLE: Revert on failure
function withdraw() public {
    for (uint i = 0; i < recipients.length; i++) {
        recipients[i].transfer(amounts[i]);  // One failure = all fail
    }
}
```

**Mitigation:**
```solidity
// GOOD: Pull over push
mapping(address => uint) public pendingRewards;

function claimReward() public {
    uint reward = pendingRewards[msg.sender];
    pendingRewards[msg.sender] = 0;
    payable(msg.sender).transfer(reward);
}
```

---

### SC-6: Front-Running / MEV
**Description:** Attackers observe pending transactions and submit their own with higher gas to profit.

**Vulnerable Scenarios:**
- DEX trades without slippage protection
- Dutch auctions
- Commit-reveal schemes without proper implementation

**Mitigation:**
```solidity
// Commit-Reveal Pattern
mapping(address => bytes32) public commitments;

function commit(bytes32 commitment) public {
    commitments[msg.sender] = commitment;
}

function reveal(uint256 value, bytes32 salt) public {
    require(keccak256(abi.encodePacked(value, salt)) == commitments[msg.sender]);
    // Process value
}

// Slippage Protection
function swap(uint amountIn, uint minAmountOut) public {
    uint amountOut = calculateSwapAmount(amountIn);
    require(amountOut >= minAmountOut, "Slippage too high");
}
```

---

### SC-7: Time Manipulation
**Description:** Reliance on `block.timestamp` for critical logic.

**Risk:** Miners can manipulate timestamp by ~15 seconds.

**Vulnerable:**
```solidity
// BAD: Using timestamp for short periods
function claim() public {
    require(block.timestamp > lastClaim + 1 minutes);
}
```

**Secure:**
```solidity
// GOOD: Use block.number for short periods
function claim() public {
    require(block.number > lastClaimBlock + 4);  // ~1 minute (15s blocks)
}
```

---

### SC-8: Delegatecall to Untrusted Callee
**Description:** Using delegatecall with user-controlled addresses.

**Vulnerable:**
```solidity
// BAD: CRITICAL VULNERABILITY
function execute(address target, bytes memory data) public {
    target.delegatecall(data);  // Attacker can modify storage
}
```

**Secure:**
```solidity
// GOOD: Whitelist approved implementations
mapping(address => bool) public approvedImplementations;

function execute(address target, bytes memory data) public {
    require(approvedImplementations[target], "Untrusted target");
    target.delegatecall(data);
}
```

---

### SC-9: Insufficient Gas Griefing
**Description:** Relying on gas stipends that can be insufficient.

**Vulnerable:**
```solidity
// BAD: Using .transfer() or .send()
payable(recipient).transfer(amount);  // Only 2300 gas
```

**Secure:**
```solidity
// GOOD: Using .call() with error handling
(bool success,) = payable(recipient).call{value: amount}("");
require(success, "Transfer failed");
```

---

### SC-10: Flash Loan Attacks
**Description:** Exploiting protocols using borrowed funds within single transaction.

**Attack Vectors:**
- Price oracle manipulation
- Governance manipulation
- Liquidity pool manipulation

**Mitigation:**
```solidity
// GOOD: Check balances at transaction end
uint256 balanceBefore = token.balanceOf(address(this));

// ... operations ...

require(token.balanceOf(address(this)) >= balanceBefore, "Flash loan attack detected");

// GOOD: Use TWAP oracles
function getPrice() public view returns (uint256) {
    return oracle.getTWAP(3600);  // 1-hour TWAP
}
```

---

## DeFi-Specific Vulnerabilities

### Price Oracle Manipulation
```solidity
// BAD: VULNERABLE: Using spot price
uint price = token0.balanceOf(pair) / token1.balanceOf(pair);

// GOOD: SECURE: Using Chainlink price feed
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

function getLatestPrice() public view returns (int) {
    (
        uint80 roundId,
        int price,
        ,
        uint updatedAt,
        uint80 answeredInRound
    ) = priceFeed.latestRoundData();

    require(price > 0, "Invalid price");
    require(updatedAt > 0, "Round not complete");
    require(answeredInRound >= roundId, "Stale price");
    require(block.timestamp - updatedAt < PRICE_VALIDITY, "Price too old");

    return price;
}
```

### Rounding Errors
```solidity
// BAD: VULNERABLE: Rounds in favor of user
uint fee = (amount * 3) / 1000;  // 0.3% fee rounds down

// GOOD: SECURE: Rounds in favor of protocol
uint fee = (amount * 3 + 999) / 1000;  // Rounds up
```

---

## Upgradeable Contract Vulnerabilities

### Storage Collision
```solidity
// BAD: VULNERABLE: Reordering variables
contract V1 {
    uint256 public a;
    uint256 public b;
}

contract V2 is V1 {
    uint256 public c;  // Adds before existing
    uint256 public a;  // COLLISION!
    uint256 public b;
}

// GOOD: SECURE: Append new variables
contract V2 is V1 {
    uint256 public c;  // Appends after existing
}
```

### Uninitialized Implementation
```solidity
// BAD: VULNERABLE: No constructor protection
contract Implementation {
    function initialize() public {
        owner = msg.sender;
    }
}

// GOOD: SECURE: Disable initializers in constructor
contract Implementation {
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize() public initializer {
        owner = msg.sender;
    }
}
```

---

## Solana-Specific Vulnerabilities

### Missing Signer Checks
```rust
// BAD: VULNERABLE
pub fn transfer(ctx: Context<Transfer>, amount: u64) -> Result<()> {
    // No signer validation
}

// GOOD: SECURE
#[derive(Accounts)]
pub struct Transfer<'info> {
    #[account(mut)]
    pub from: Signer<'info>,  // Enforces signer
    #[account(mut)]
    pub to: AccountInfo<'info>,
}
```

### Account Validation
```rust
// BAD: VULNERABLE: No ownership check
let token_account = &ctx.accounts.token_account;

// GOOD: SECURE: Validate ownership
require_keys_eq!(
    ctx.accounts.token_account.owner,
    token::ID,
    ErrorCode::InvalidTokenAccount
);
```

---

## Automated Security Tools

### Static Analysis
```bash
# Slither - Static analysis framework
slither contracts/

# Mythril - Symbolic execution
myth analyze contracts/Token.sol

# Manticore - Dynamic symbolic execution
manticore contracts/Token.sol
```

### Fuzzing
```bash
# Echidna - Property-based fuzzer
echidna-test contracts/ --contract Token --config echidna.yaml

# Foundry invariant testing
forge test --match-contract Invariant
```

### Formal Verification
```bash
# Certora Prover
certoraRun contracts/Token.sol --verify Token:specs/Token.spec
```

---

## Audit Process

1. **Preparation:**
   - Clone repository
   - Install dependencies
   - Compile contracts
   - Run existing tests

2. **Automated Analysis:**
   - Run Slither
   - Run Mythril/Manticore
   - Run fuzzing tools
   - Check Solhint/Ethlint

3. **Manual Review:**
   - Read contracts line-by-line
   - Check against this checklist
   - Identify attack vectors
   - Document findings

4. **Testing:**
   - Write exploit POCs
   - Verify mitigations
   - Test edge cases
   - Measure gas costs

5. **Reporting:**
   - Classify by severity
   - Provide exploit scenarios
   - Recommend mitigations
   - Suggest improvements

---

## Severity Classification

**Critical (9.0-10.0):**
- Direct loss of funds
- Unauthorized access to funds
- Protocol manipulation

**High (7.0-8.9):**
- Potential loss of funds under specific conditions
- Smart contract freezing
- Unauthorized state changes

**Medium (4.0-6.9):**
- State inconsistency
- Failure to deliver promised functionality
- Suboptimal design patterns

**Low (1.0-3.9):**
- Code quality issues
- Gas inefficiencies
- Best practice violations

**Informational (0.0):**
- Code style
- Documentation
- Suggestions

---

## Common Attack Patterns to Test

1. **Reentrancy:** Recursive calls
2. **Access Control:** Unauthorized function calls
3. **Front-Running:** Transaction ordering manipulation
4. **Overflow/Underflow:** Arithmetic boundaries
5. **Flash Loans:** Single-transaction exploits
6. **Oracle Manipulation:** Price feed attacks
7. **DoS:** Gas limit attacks, reverting recipients
8. **Phishing:** tx.origin usage
9. **Delegate Call:** Storage manipulation
10. **Rounding:** Precision loss exploitation

---

## Resources

- [SWC Registry](https://swcregistry.io/)
- [Consensys Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [Rekt News](https://rekt.news/)
- [DeFi Hacks Analysis](https://github.com/SunWeb3Sec/DeFiHackLabs)
- [Secureum Bootcamp](https://secureum.substack.com/)
