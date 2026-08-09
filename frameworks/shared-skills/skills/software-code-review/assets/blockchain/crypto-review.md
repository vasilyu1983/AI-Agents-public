# Smart Contract Code Review Checklist

Comprehensive code review checklist for blockchain smart contracts (Solidity, Rust, FunC, Tact).

---

## Standards (Core)

- Clean code standard (cite `CC-*` IDs): [../../../software-clean-code-standard/references/clean-code-standard.md](../../../software-clean-code-standard/references/clean-code-standard.md)
- Review comments: use labeled intent and cite `CC-*` IDs when applicable ([../core/review-comment-guidelines.md](../core/review-comment-guidelines.md)).

## Critical Security Issues (P0)

### Reentrancy
- [ ] All state changes before external calls (Checks-Effects-Interactions)
- [ ] ReentrancyGuard modifier on state-changing functions
- [ ] No external calls in loops
- [ ] ETH transfers use `.call{value:}` with success check

### Access Control
- [ ] All privileged functions have access modifiers (`onlyOwner`, `onlyRole`)
- [ ] Zero address validation on admin transfers
- [ ] Multi-signature or timelock for critical operations
- [ ] Role revocation properly implemented

### Integer Overflow/Underflow
- [ ] Solidity 0.8+ or SafeMath for older versions
- [ ] `unchecked` blocks only where mathematically safe
- [ ] No arithmetic with user input in unchecked blocks

### Oracle Manipulation
- [ ] Price data validated (not zero, not stale)
- [ ] TWAP (Time-Weighted Average Price) for critical operations
- [ ] Multiple oracle sources for redundancy
- [ ] Staleness checks (timestamp validation)
- [ ] Circuit breakers for anomalous prices

---

## High Severity Issues (P1)

### Frontrunning/MEV
- [ ] Commit-reveal schemes for sensitive operations
- [ ] Flashbots integration for MEV-sensitive transactions
- [ ] Slippage protection on swaps
- [ ] Deadline parameters on time-sensitive calls

### Delegatecall Safety
- [ ] No delegatecall to untrusted addresses
- [ ] Proxy implementation whitelisting
- [ ] Storage collision checks in upgradeable contracts

### External Call Safety
- [ ] Return values checked for all external calls
- [ ] Gas stipends appropriate (avoid `.transfer()` and `.send()`)
- [ ] Reentrancy protection where needed
- [ ] Proper error handling with try/catch

### Flash Loan Protection
- [ ] State changes within single transaction validated
- [ ] Balance checks at transaction end
- [ ] No reliance on `balanceOf` for critical logic
- [ ] Atomic invariants enforced

---

## Medium Severity Issues (P2)

### Gas Optimization
- [ ] Storage variables packed into 32-byte slots
- [ ] `calldata` used for external function arrays
- [ ] Storage reads cached in memory/stack
- [ ] Custom errors instead of require strings
- [ ] `immutable` and `constant` where applicable
- [ ] `unchecked` for safe arithmetic (loop counters)

### Input Validation
- [ ] All user inputs validated (bounds, zero checks, array lengths)
- [ ] Address parameters checked for zero address
- [ ] Array length limits to prevent DoS
- [ ] Percentage/ratio parameters validated

### Event Emission
- [ ] Events emitted for all state changes
- [ ] Indexed parameters for important values
- [ ] Events emitted before external calls
- [ ] Consistent event naming convention

### Timestamp Manipulation
- [ ] No reliance on `block.timestamp` for short periods (<15 minutes)
- [ ] Use `block.number` for short time periods
- [ ] Document acceptable timestamp drift

---

## Upgradeable Contract Review

### Proxy Pattern Checks
- [ ] Storage gaps in base contracts (`uint256[50] private __gap`)
- [ ] Initializer functions protected (`initializer` modifier)
- [ ] Constructor disables initializers (`_disableInitializers()`)
- [ ] No new variables before existing ones in upgrades
- [ ] `_authorizeUpgrade` properly protected

### Storage Layout
- [ ] No storage variable reordering
- [ ] Namespaced storage for new variables
- [ ] Diamond storage pattern for complex upgrades
- [ ] Storage slot collision checks

---

## DeFi-Specific Checks

### AMM/DEX
- [ ] Constant product formula correct (`x * y = k`)
- [ ] Slippage calculation accurate
- [ ] Fee collection doesn't break invariants
- [ ] Price impact calculated correctly
- [ ] Liquidity addition/removal safe
- [ ] No rounding errors favoring attackers

### Lending/Borrowing
- [ ] Collateral ratio enforced
- [ ] Liquidation threshold correct
- [ ] Health factor calculation accurate
- [ ] Interest accrual correct
- [ ] No borrowing with same asset as collateral
- [ ] Flash loan protection

### Staking/Yield Farming
- [ ] Reward calculation correct
- [ ] No reward manipulation via deposits/withdrawals
- [ ] Compound interest math accurate
- [ ] Emergency withdrawal mechanism
- [ ] No loss of rewards on edge cases

---

## Token-Specific Checks

### ERC20
- [ ] Total supply tracking correct
- [ ] Transfer returns boolean
- [ ] Approve/TransferFrom race condition mitigated
- [ ] Decimals properly defined
- [ ] Burn/mint properly updates totalSupply

### ERC721/ERC1155
- [ ] Token ID uniqueness enforced
- [ ] Metadata URI properly implemented
- [ ] Safe transfer callbacks implemented
- [ ] Batch operations safe
- [ ] Enumeration extension if needed

---

## Testing Coverage

- [ ] Unit tests for all functions
- [ ] Edge case tests (zero, max uint, empty arrays)
- [ ] Access control tests (unauthorized calls fail)
- [ ] Reentrancy attack tests
- [ ] Fuzz tests with random inputs
- [ ] Fork tests for mainnet integrations
- [ ] Invariant tests for protocol properties
- [ ] Test coverage >90%
- [ ] Gas benchmarks documented

---

## Documentation Review

- [ ] NatSpec comments on all public/external functions
- [ ] Architecture diagrams present
- [ ] Known limitations documented
- [ ] Upgrade procedure documented
- [ ] Emergency procedures defined
- [ ] Deployment checklist complete

---

## Deployment Preparation

- [ ] No floating pragma (version locked)
- [ ] Compiler warnings addressed
- [ ] Optimizer runs configured appropriately
- [ ] Contract verified on block explorer
- [ ] Multi-sig wallet as owner
- [ ] Timelock for critical operations
- [ ] Monitoring and alerting configured
- [ ] Professional audit completed
- [ ] Bug bounty program prepared

---

## Solana-Specific Checks (Rust/Anchor)

### Account Validation
- [ ] All accounts validated (ownership, signer, mutability)
- [ ] PDA (Program Derived Address) seeds validated
- [ ] Account discriminators checked
- [ ] Account size constraints enforced

### Signer Checks
- [ ] Required signers properly enforced
- [ ] No missing `is_signer` constraints
- [ ] Authority validation on privileged operations

### CPI (Cross-Program Invocation)
- [ ] CPI signer seeds validated
- [ ] Program ID validation
- [ ] Account ownership validated post-CPI

---

## TON-Specific Checks (FunC/Tact)

### Message Handling
- [ ] Bounce flag properly set
- [ ] Message value validation
- [ ] Excess gas refunded
- [ ] Internal message handling correct

### State Management
- [ ] Persistent data properly saved
- [ ] Cell references valid
- [ ] Gas limits appropriate

---

## Clean Code (Core)

- Standards: cite `CC-*` IDs; do not restate rules.
- Common `CC-*` IDs for contracts: `CC-NAM-01`, `CC-FUN-01`, `CC-FUN-05`, `CC-FLOW-03`, `CC-ERR-01`, `CC-ERR-02`, `CC-TYP-04`, `CC-DOC-01`, `CC-DOC-04`, `CC-TST-01`

---

## Review Process (Core)

1. **Manual Review:**
   - Read contract line-by-line
   - Check against this checklist
   - Verify test coverage
   - Review deployment scripts

2. **Testing:**
   - Run all unit tests
   - Run fork tests if applicable
   - Verify gas costs
   - Check coverage reports

3. **Documentation Review:**
   - Verify NatSpec completeness
   - Check README accuracy
   - Validate deployment guide

---

## Severity Ratings

- **P0 (Critical):** Funds at risk, immediate exploit possible
- **P1 (High):** Security vulnerability, complex exploit
- **P2 (Medium):** Logic error, gas inefficiency, poor UX
- **P3 (Low):** Code quality, best practices, documentation

---

## Common Anti-Patterns to Avoid

```solidity
// BAD: Using tx.origin for authorization
require(tx.origin == owner);

// BAD: Unprotected ether transfer
payable(msg.sender).transfer(amount);

// BAD: Reentrancy vulnerability
balances[msg.sender] -= amount;
msg.sender.call{value: amount}("");

// BAD: Unprotected self-destruct
selfdestruct(payable(owner));

// BAD: Floating pragma
pragma solidity ^0.8.0;

// BAD: Missing access control
function mint(address to, uint amount) public {
    _mint(to, amount);
}
```

---

## Optional: AI / Automation

- Automated analysis: Slither/Mythril/Manticore; lint rules (Solhint/Ethlint) where relevant.
- Fuzzing and invariants: Echidna, Foundry invariant tests.
- Formal verification (when warranted): Certora Prover, K Framework.
- Monitoring/defense in depth: Tenderly, OpenZeppelin Defender.
