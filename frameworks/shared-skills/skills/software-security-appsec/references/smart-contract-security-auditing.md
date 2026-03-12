# Smart Contract Security Auditing — Comprehensive Methodology

Production-grade security audit framework for blockchain smart contracts across all major platforms.

---

## Table of Contents

1. [Audit Process Overview](#audit-process-overview)
2. [Pre-Audit Preparation](#pre-audit-preparation)
3. [Automated Analysis Tools](#automated-analysis-tools)
4. [Manual Review Methodology](#manual-review-methodology)
5. [Platform-Specific Checklists](#platform-specific-checklists)
6. [Severity Classification](#severity-classification)
7. [Report Structure](#report-structure)
8. [Post-Audit Verification](#post-audit-verification)

---

## Audit Process Overview

### Five-Phase Audit Methodology

```
Phase 1: Preparation (10% of time)
├── Repository setup
├── Documentation review
├── Threat modeling
└── Scope definition

Phase 2: Automated Analysis (15% of time)
├── Static analysis (Slither, Mythril)
├── Linting and style checks
├── Dependency vulnerability scanning
└── Gas profiling

Phase 3: Manual Review (50% of time)
├── Line-by-line code review
├── Architecture analysis
├── Business logic verification
└── Access control validation

Phase 4: Testing & Exploitation (20% of time)
├── Exploit POC development
├── Fuzz testing
├── Invariant testing
└── Integration testing

Phase 5: Reporting (5% of time)
├── Finding documentation
├── Severity classification
├── Remediation recommendations
└── Final report delivery
```

---

## Pre-Audit Preparation

### Initial Questionnaire

**Project Information:**
1. What is the primary purpose of the smart contract(s)?
2. What are the expected user flows?
3. What assets are managed (tokens, NFTs, funds)?
4. What are the critical invariants that must hold?
5. Are there any known issues or concerns?

**Technical Details:**
1. Which blockchain(s) will this deploy to?
2. What is the expected transaction volume?
3. Are contracts upgradeable? If so, how?
4. What external dependencies exist (oracles, DEXs, etc.)?
5. What previous audits have been conducted?

### Repository Setup

```bash
# Clone repository
git clone https://github.com/project/contracts.git
cd contracts

# Install dependencies (Solidity example)
npm install

# Compile contracts
npx hardhat compile

# Run existing tests
npx hardhat test

# Check test coverage
npx hardhat coverage

# Generate documentation
npx hardhat docgen
```

### Threat Modeling

**Asset Identification:**
- ETH/SOL/native tokens held
- ERC20/SPL tokens managed
- NFTs (ERC721, ERC1155, Metaplex)
- User data and permissions
- Protocol configuration parameters

**Attack Surfaces:**
- Public/external functions
- Cross-contract calls (CPI, delegatecall)
- Oracle dependencies
- Admin/governance functions
- Upgrade mechanisms

**Trust Boundaries:**
- User inputs (untrusted)
- Oracle data (semi-trusted)
- Multi-sig operators (trusted)
- Protocol developers (trusted)

---

## Automated Analysis Tools

### Solidity/EVM Tools

**Slither (Static Analysis):**
```bash
slither . --print human-summary
slither . --print contract-summary
slither . --print function-summary
slither . --detect reentrancy-eth
slither . --detect uninitialized-state
slither . --detect controlled-delegatecall

# Generate report
slither . --json slither-report.json
```

**Mythril (Symbolic Execution):**
```bash
myth analyze contracts/Token.sol --solv 0.8.20
myth analyze contracts/ --execution-timeout 600
```

**Echidna (Fuzz Testing):**
```bash
# echidna.yaml
testMode: assertion
testLimit: 50000
deployer: "0x30000"
sender: ["0x10000", "0x20000", "0x30000"]

# Run fuzzer
echidna-test contracts/Token.sol --contract Token --config echidna.yaml
```

**Manticore (Dynamic Analysis):**
```bash
manticore contracts/Token.sol --contract Token
```

**Solhint (Linting):**
```bash
solhint 'contracts/**/*.sol'
```

### Solana/Rust Tools

**Anchor Verify:**
```bash
anchor build --verifiable
solana-verify verify-from-repo --program-id <PROGRAM_ID> https://github.com/project/program
```

**Cargo Audit:**
```bash
cargo audit
```

**Clippy (Linting):**
```bash
cargo clippy -- -D warnings
```

**Sec3 Auto-Audit:**
```bash
# Solana security scanner
sec3-cli audit .
```

### Dependency Scanning

```bash
# NPM audit
npm audit

# Yarn audit
yarn audit

# Check for known vulnerabilities
npx snyk test
```

---

## Manual Review Methodology

### Line-by-Line Review Process

**Step 1: Entry Points (15 minutes per contract)**
- Identify all public/external functions
- Map user-accessible attack surface
- Document expected vs actual access control

**Step 2: State Variables (10 minutes per contract)**
- Review storage layout
- Check initialization
- Verify mutability (constant, immutable)
- Look for unprotected state changes

**Step 3: Critical Logic (30-60 minutes per function)**
For each critical function:
1. **Input Validation:** Are all inputs validated?
2. **Authorization:** Is caller properly authorized?
3. **State Changes:** Are state changes in correct order (CEI pattern)?
4. **External Calls:** Are external calls safe (reentrancy, return values)?
5. **Arithmetic:** Are calculations safe from overflow/underflow/precision loss?
6. **Events:** Are all state changes logged?

**Step 4: Integration Points (20 minutes per dependency)**
- Oracle calls: staleness checks, price manipulation
- DEX integrations: slippage protection, flash loan attacks
- Token transfers: check return values, approve-transfer pattern

### Architecture Review

**Separation of Concerns:**
- [ ] Logic separated from storage
- [ ] Access control isolated
- [ ] Treasury/funds management separate
- [ ] Upgradability cleanly implemented

**Upgrade Mechanisms:**
- [ ] Proxy pattern correctly implemented (UUPS, Transparent, Diamond)
- [ ] Storage collisions avoided
- [ ] Initializers protected (`_disableInitializers()`)
- [ ] Upgrade authorization secured

**Gas Efficiency:**
- [ ] Storage reads cached
- [ ] Loops bounded
- [ ] Storage packing optimized
- [ ] Events used instead of storage for historical data

### Business Logic Verification

**Protocol Invariants:**
- Total supply == sum of balances
- Reserves maintain constant product (AMM)
- Collateral ratio always >= minimum
- User withdrawals never exceed deposits

**Economic Security:**
- Fee calculations round in protocol's favor
- Rewards distributed fairly
- No economic exploits (flash loans, oracle manipulation)

---

## Platform-Specific Checklists

### Ethereum/Solidity Checklist

**Critical (P0):**
- [ ] Reentrancy protection (CEI pattern, ReentrancyGuard)
- [ ] Access control on privileged functions
- [ ] Safe arithmetic (Solidity 0.8+ or SafeMath)
- [ ] External call return values checked
- [ ] No delegatecall to untrusted contracts
- [ ] Oracle data validated (staleness, price bounds)

**High (P1):**
- [ ] ERC20 approve-transfer pattern used correctly
- [ ] No tx.origin for authentication
- [ ] Timestamp manipulation considered
- [ ] Front-running mitigated (commit-reveal, slippage limits)
- [ ] Gas griefing prevented (no transfer/send, use call)

**Medium (P2):**
- [ ] Storage variables packed efficiently
- [ ] Events emitted for state changes
- [ ] Pausable for emergencies
- [ ] Upgradeable contracts follow proxy standards
- [ ] NatSpec documentation complete

**Low (P3):**
- [ ] Custom errors instead of require strings
- [ ] Immutable/constant where applicable
- [ ] No floating pragma
- [ ] Solhint warnings addressed

### Solana/Anchor Checklist

**Critical (P0):**
- [ ] All accounts validated (owner, signer, program ID)
- [ ] PDA seeds unique and collision-resistant
- [ ] Checked arithmetic used (no overflow)
- [ ] Signer enforcement with `Signer<'info>`
- [ ] Account type validation (TokenAccount, Mint, etc.)
- [ ] CPI targets validated (program IDs, account ownership)

**High (P1):**
- [ ] No reinitialization attacks (`init` constraint used)
- [ ] Authority checks (has_one, constraint)
- [ ] Mint/token account validation
- [ ] Bump seeds verified in PDAs
- [ ] Close account security (rent reclaim)

**Medium (P2):**
- [ ] Account sizes minimized
- [ ] Zero-copy for large accounts
- [ ] Compute budget within limits
- [ ] Custom errors for all failure cases

**Low (P3):**
- [ ] Clippy warnings addressed
- [ ] Documentation complete
- [ ] Test coverage >90%

### CosmWasm Checklist

**Critical (P0):**
- [ ] All `ExecuteMsg` variants validate sender
- [ ] Funds handling secure (accept_funds, send_tokens)
- [ ] Query functions don't modify state
- [ ] Reentrancy protection (no state between submessages)

**High (P1):**
- [ ] Integer overflow protection
- [ ] Decimal precision handled correctly
- [ ] IBC packet validation
- [ ] Migration function secured

---

## Severity Classification

### CVSS-Based Scoring

**Critical (9.0-10.0):**
- Direct theft of funds
- Unauthorized minting/burning
- Protocol manipulation leading to loss

**Example:**
```solidity
// CRITICAL: Reentrancy allows draining contract
function withdraw() public {
    uint amount = balances[msg.sender];
    (bool success,) = msg.sender.call{value: amount}("");
    balances[msg.sender] = 0;  // State change AFTER call
}
```

**High (7.0-8.9):**
- Potential fund loss under specific conditions
- Access control bypass
- Oracle manipulation

**Example:**
```solidity
// HIGH: Missing access control
function setAdmin(address newAdmin) public {
    admin = newAdmin;  // Anyone can become admin
}
```

**Medium (4.0-6.9):**
- State inconsistency
- DoS attacks
- Griefing attacks

**Example:**
```solidity
// MEDIUM: Unbounded loop DoS
function distributeRewards() public {
    for (uint i = 0; i < users.length; i++) {
        users[i].transfer(reward);  // Can exceed gas limit
    }
}
```

**Low (1.0-3.9):**
- Gas inefficiency
- Code quality issues
- Best practice violations

**Example:**
```solidity
// LOW: Gas inefficiency
uint256 public balance;
function getBalance() public view returns (uint256) {
    return balance;  // Redundant getter (auto-generated)
}
```

**Informational (0.0):**
- Code style
- Documentation
- Suggestions

---

## Report Structure

### Executive Summary Template

```markdown
# Security Audit Report

## Project: [Project Name]
**Audit Period:** [Start Date] - [End Date]
**Auditors:** [Names]
**Commit Hash:** [Git commit hash]

### Summary
- **Total Issues:** X
- **Critical:** X
- **High:** X
- **Medium:** X
- **Low:** X
- **Informational:** X

### Scope
The audit covered the following contracts:
- `ContractA.sol` (XXX lines)
- `ContractB.sol` (XXX lines)

### Key Findings
1. [Critical Issue #1 Summary]
2. [High Issue #1 Summary]
3. [High Issue #2 Summary]

### Recommendations
- Fix all Critical and High severity issues before deployment
- Implement additional test coverage for [specific area]
- Consider [architectural improvement]
```

### Finding Template

```markdown
## [Severity] [Finding ID]: [Title]

### Description
[Detailed description of the vulnerability]

### Location
- **File:** `contracts/Token.sol`
- **Lines:** 123-145
- **Function:** `withdraw()`

### Impact
[What could an attacker achieve? What's the potential loss?]

### Proof of Concept
[Code demonstrating the exploit]

bash
# Setup
npx hardhat test test/exploit.test.ts

### Recommendation
[How to fix the issue]

solidity
// BEFORE (vulnerable)
function withdraw() public {
    uint amount = balances[msg.sender];
    msg.sender.call{value: amount}("");
    balances[msg.sender] = 0;
}

// AFTER (fixed)
function withdraw() public nonReentrant {
    uint amount = balances[msg.sender];
    balances[msg.sender] = 0;
    (bool success,) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}


### References
- [CWE-XXXX](https://cwe.mitre.org/data/definitions/XXX.html)
- [SWC-XXX](https://swcregistry.io/docs/SWC-XXX)
```

### Gas Optimization Template

```markdown
## Gas Optimization: [Description]

### Current Implementation
solidity
// Uses 50,000 gas
for (uint i = 0; i < array.length; i++) {
    data[i] = array[i];
}


### Optimized Implementation
solidity
// Uses 35,000 gas
uint length = array.length;
for (uint i = 0; i < length;) {
    data[i] = array[i];
    unchecked { ++i; }
}


### Gas Savings
- **Before:** 50,000 gas
- **After:** 35,000 gas
- **Savings:** 15,000 gas (30%)
```

---

## Post-Audit Verification

### Fix Verification Process

1. **Receive Updated Code:**
   - New commit hash provided
   - Developer summary of changes

2. **Verify Each Fix:**
   - [ ] Issue completely resolved
   - [ ] No new issues introduced
   - [ ] Tests added for the fix
   - [ ] Gas impact measured

3. **Regression Testing:**
   ```bash
   # Run all automated tools again
   slither .
   echidna-test contracts/
   npx hardhat test
   npx hardhat coverage
   ```

4. **Final Report:**
   ```markdown
   ## Fix Verification Summary

   | Finding ID | Status | Notes |
   |------------|--------|-------|
   | CRIT-01 | [OK] Fixed | Implemented ReentrancyGuard |
   | HIGH-01 | [OK] Fixed | Added access control |
   | MED-01 | [WARNING] Partially | Loop bounded, but limit too high |
   | LOW-01 | [FAIL] Not Fixed | Developer deferred to v2 |
   ```

### Final Checklist

**Before Mainnet Deployment:**
- [ ] All Critical and High issues resolved
- [ ] Medium issues resolved or accepted as known risks
- [ ] Tests updated to cover all fixes
- [ ] Gas profiling confirms no major regressions
- [ ] Documentation updated
- [ ] Multi-sig setup for admin functions
- [ ] Monitoring and alerting configured
- [ ] Emergency pause mechanism tested
- [ ] Upgrade procedures documented
- [ ] Bug bounty program launched

---

## Tools Reference

### Ethereum/Solidity
- **Slither:** https://github.com/crytic/slither
- **Mythril:** https://github.com/ConsenSys/mythril
- **Echidna:** https://github.com/crytic/echidna
- **Manticore:** https://github.com/trailofbits/manticore
- **Certora Prover:** https://www.certora.com/
- **Halmos:** https://github.com/a16z/halmos

### Solana/Rust
- **Sec3:** https://www.sec3.dev/
- **Soteria:** https://github.com/blocksecteam/soteria
- **Cargo Audit:** https://github.com/rustsec/rustsec
- **Clippy:** Built into Rust toolchain

### General
- **Semgrep:** https://semgrep.dev/
- **CodeQL:** https://codeql.github.com/
- **Snyk:** https://snyk.io/

---

## Audit Report Examples

### Public Audit Reports
- [Trail of Bits](https://github.com/trailofbits/publications)
- [OpenZeppelin](https://blog.openzeppelin.com/security-audits)
- [Consensys Diligence](https://consensys.io/diligence/audits/)
- [Certora](https://www.certora.com/audits/)
- [Quantstamp](https://github.com/quantstamp/audits)

### Learning Resources
- [Smart Contract Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [SWC Registry](https://swcregistry.io/)
- [Secureum Bootcamp](https://secureum.substack.com/)
- [DeFi Hack Labs](https://github.com/SunWeb3Sec/DeFiHackLabs)
- [Rekt News](https://rekt.news/)

---

## Conclusion

A thorough security audit combines:
1. **Automated tools** for breadth (catch common issues fast)
2. **Manual review** for depth (understand complex logic)
3. **Testing** for validation (prove exploits work)
4. **Documentation** for clarity (enable fixes and future audits)

**Remember:** An audit is a snapshot in time. Continuous security monitoring, bug bounties, and regular re-audits are essential for production systems managing significant value.
