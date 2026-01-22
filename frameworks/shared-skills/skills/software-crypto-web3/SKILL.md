---
name: software-crypto-web3
description: Production-grade blockchain and Web3 development with Solidity (Ethereum/EVM), Rust (Solana), CosmWasm (Cosmos), including smart contract architecture, security patterns, gas optimization, testing strategies, DeFi protocols, and deployment workflows.
---

# Blockchain & Web3 Development Skill — Quick Reference

This skill equips blockchain developers with execution-ready patterns for building secure, gas-optimized smart contracts and decentralized applications. Apply these patterns when you need smart contract development, DeFi protocols, NFT implementations, security audits, or Web3 architecture.

**Modern Best Practices (Jan 2026)**: Solidity 0.8.33+, security-first development, explicit threat models, comprehensive testing (unit, integration, fork, invariant), audits/formal methods where warranted, upgrade safety (timelocks, governance, rollback plans), and defense-in-depth for key custody and signing.

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| Solidity Development | Hardhat/Foundry | `npx hardhat init` or `forge init` | Ethereum/EVM smart contracts |
| Solana Programs | Anchor | `anchor init` | Solana blockchain development |
| Cosmos Contracts | CosmWasm | `cargo generate --git cosmwasm-template` | Cosmos ecosystem contracts |
| TON Contracts | Tact/FunC + Blueprint | `npm create ton@latest` | TON blockchain development |
| Testing (Solidity) | Foundry/Hardhat | `forge test` or `npx hardhat test` | Unit, fork, invariant tests |
| Security Audit | Slither/Aderyn/Echidna | `slither .` or `aderyn .` | Static analysis, fuzzing |
| AI-Assisted Audit | Sherlock AI/Olympix | Integrated platforms | Pre-audit, CI/CD security |
| Fuzzing | Echidna/Medusa | `echidna .` or `medusa fuzz` | Property-based fuzzing |
| Gas Optimization | Foundry Gas Snapshots | `forge snapshot` | Benchmark and optimize gas |
| Deployment | Hardhat Deploy/Forge Script | `npx hardhat deploy` | Mainnet/testnet deployment |
| Verification | Etherscan API | `npx hardhat verify` | Source code verification |
| Upgradeable Contracts | OpenZeppelin Upgrades | `@openzeppelin/hardhat-upgrades` | Proxy-based upgrades |
| Smart Wallets | ERC-4337 + EIP-7702 | Account abstraction SDKs | Gasless UX, batch txns |

# When to Use This Skill

Use this skill when you need:

- Smart contract development (Solidity, Rust, CosmWasm)
- DeFi protocol implementation (AMM, lending, staking, yield farming)
- NFT and token standards (ERC20, ERC721, ERC1155, SPL tokens)
- DAO governance systems
- Cross-chain bridges and interoperability
- Gas optimization and storage patterns
- Smart contract security audits
- Testing strategies (Foundry, Hardhat, Anchor)
- Oracle integration (Chainlink, Pyth)
- Upgradeable contract patterns (proxies, diamonds)
- Web3 frontend integration (ethers.js, web3.js, @solana/web3.js)
- Blockchain indexing (The Graph, subgraphs)
- MEV protection and flashbots
- Layer 2 scaling solutions (Base, Arbitrum, Optimism, zkSync)
- Account abstraction (ERC-4337, EIP-7702, smart wallets)
- **Backend crypto integration** (.NET/C#, multi-provider architecture, CQRS)
- Webhook handling and signature validation (Fireblocks, custodial providers)
- Event-driven architecture with Kafka for crypto payments
- Transaction lifecycle management and monitoring
- Wallet management (custodial vs non-custodial)

## Decision Tree: Blockchain Platform Selection

```text
Project needs: [Use Case]
    ├─ EVM-compatible smart contracts?
    │   ├─ Complex testing needs → Foundry (Solidity tests, fuzzing, gas snapshots)
    │   ├─ TypeScript ecosystem → Hardhat (plugins, TypeScript, Ethers.js)
    │   └─ Enterprise features → NestJS + Hardhat
    │
    ├─ High throughput/low fees?
    │   ├─ Rust-based → Solana (Anchor framework)
    │   ├─ EVM L2 → Arbitrum/Optimism (Ethereum security, lower gas)
    │   └─ Telegram integration → TON (Tact/FunC contracts)
    │
    ├─ Interoperability across chains?
    │   ├─ Cosmos ecosystem → CosmWasm (IBC protocol)
    │   ├─ Multi-chain DeFi → LayerZero or Wormhole
    │   └─ Bridge development → Custom bridge contracts
    │
    ├─ Token standard implementation?
    │   ├─ Fungible tokens → ERC20 (OpenZeppelin), SPL Token (Solana)
    │   ├─ NFTs → ERC721/ERC1155 (OpenZeppelin), Metaplex (Solana)
    │   └─ Semi-fungible → ERC1155 (gaming, fractionalized NFTs)
    │
    ├─ DeFi protocol development?
    │   ├─ AMM/DEX → Uniswap V3 fork or custom (x*y=k, concentrated liquidity)
    │   ├─ Lending → Compound/Aave fork (collateralized borrowing)
    │   └─ Staking/Yield → Custom reward distribution contracts
    │
    ├─ Upgradeable contracts required?
    │   ├─ Transparent Proxy → OpenZeppelin (admin/user separation)
    │   ├─ UUPS → Gas-efficient (upgrade logic in implementation)
    │   └─ Diamond Standard → Modular functionality (EIP-2535)
    │
    └─ Backend integration?
        ├─ .NET/C# → Multi-provider architecture (see Backend Integration Patterns)
        ├─ Node.js → Ethers.js/Web3.js + Prisma
        └─ Python → Web3.py + FastAPI
```

**Chain-Specific Considerations:**

- **Ethereum/EVM**: Security-first, higher gas costs, largest ecosystem
- **Solana**: Performance-first, Rust required, lower fees
- **Cosmos**: Interoperability-first, IBC native, growing ecosystem
- **TON**: Telegram-first, async contracts, unique architecture

See [references/](references/) for chain-specific best practices.

---

## Security-First Patterns (Jan 2026)

> **Security baseline**: Assume an adversarial environment. Treat contracts and signing infrastructure as public, attackable APIs.

### Custody, Keys, and Signing (Core)

Key management is the dominant risk driver in production crypto systems. Use general key management guidance as a baseline (NIST SP 800-57) https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final

| Model | Who holds keys | Typical use | Primary risks | Default controls |
|------|-----------------|------------|---------------|------------------|
| Non-custodial | End user wallet | Consumer apps, self-custody | Phishing, approvals, UX errors | Hardware wallet support, clear signing UX, allowlists |
| Custodial | Your service (HSM/MPC) | Exchanges, payments, B2B | Key theft, insider threat, ops mistakes | HSM/MPC, separation of duties, limits/approvals, audit logs |
| Hybrid | Split responsibility | Enterprises | Complex failure modes | Explicit recovery/override paths, runbooks |

Do:
- Separate hot/warm/cold signing paths with limits and approvals [Inference]
- Require dual control for high-value transfers (policy engine + human approval) [Inference]
- Keep an immutable audit trail for signing requests (who/what/when/why) [Inference]

Avoid:
- Storing private keys in databases or application config
- Reusing signing keys across environments (dev/staging/prod)
- Hot-wallet automation without rate limits and circuit breakers [Inference]

### Checks-Effects-Interactions (CEI) Pattern

**Mandatory** for all state-changing functions.

```solidity
// Correct: CEI pattern
function withdraw(uint256 amount) external {
    // 1. CHECKS: Validate conditions
    require(balances[msg.sender] >= amount, "Insufficient balance");

    // 2. EFFECTS: Update state BEFORE external calls
    balances[msg.sender] -= amount;

    // 3. INTERACTIONS: External calls LAST
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}

// Wrong: External call before state update (reentrancy risk)
function withdrawUnsafe(uint256 amount) external {
    require(balances[msg.sender] >= amount);
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] -= amount; // Too late!
}
```

### Security Tools (Jan 2026)

| Category | Tool | Purpose | When to Use |
|----------|------|---------|-------------|
| Static Analysis | Slither | Vulnerability detection, 92+ detectors | Every contract |
| Static Analysis | Aderyn | Rust-based, faster for large codebases | Large projects |
| Fuzzing | Echidna | Property-based fuzzing | Complex state |
| Fuzzing | Medusa | Parallelized Go fuzzer | CI/CD pipelines |
| Formal Verification | SMTChecker | Built-in Solidity checker | Every contract |
| Formal Verification | Certora | Property-based proofs (CVL) | DeFi, high-value |
| Formal Verification | Halmos | Symbolic testing | Complex invariants |
| AI-Assisted | Sherlock AI | ML vulnerability detection | Pre-audit prep |
| AI-Assisted | Olympix | DevSecOps integration | CI/CD security |
| AI-Assisted | AuditBase | 423+ detectors, LLM-powered | Business logic |
| Mutation Testing | SuMo | Test suite quality assessment | Test validation |

```solidity
// Certora CVL rule example
rule balanceNeverNegative(address user) {
    env e;
    require balances[user] >= 0;
    deposit(e);
    assert balances[user] >= 0;
}
```

> **AI Auditor Landscape (2026)**: AI auditing tools have cut average audit time by 30%+. Sherlock AI (released Sept 2025) combines rule-based scanning with supervised learning. Use AI tools for pre-audit preparation; they complement, not replace, human auditors.

### MEV Protection

| Strategy | Implementation |
|----------|----------------|
| Private mempool | Flashbots Protect, MEV Blocker |
| Commit-reveal | Hash commitment, reveal after deadline |
| Batch auctions | CoW Protocol, Gnosis Protocol |
| Encrypted mempools | Shutter Network |

```solidity
// Commit-reveal pattern
mapping(address => bytes32) public commitments;

function commit(bytes32 hash) external {
    commitments[msg.sender] = hash;
}

function reveal(uint256 value, bytes32 salt) external {
    require(
        keccak256(abi.encodePacked(value, salt)) == commitments[msg.sender],
        "Invalid reveal"
    );
    // Process revealed value
}
```

---

## Account Abstraction (Jan 2026)

> **Adoption**: 40M+ smart accounts deployed, 100M+ UserOperations processed. EIP-7702 live since Pectra upgrade (May 2025).

### ERC-4337 vs EIP-7702

| Standard | Type | Key Feature | Use Case |
|----------|------|-------------|----------|
| ERC-4337 | Smart contract wallets | Full AA without protocol changes | New wallets, DeFi, gaming |
| EIP-7702 | EOA enhancement | EOAs execute smart contract code | Existing wallets, batch txns |
| ERC-6900 | Modular accounts | Plugin management for AA wallets | Extensible wallet features |

**ERC-4337 Architecture:**
```text
User → UserOperation → Bundler → EntryPoint → Smart Account → Target Contract
                          ↓
                      Paymaster (gas sponsorship)
```

**EIP-7702 (Pectra Upgrade):**
- EOAs can temporarily delegate to smart contracts
- Enables batch transactions, sponsored gas for existing addresses
- Complementary to ERC-4337 (uses same bundler/paymaster infra)
- Supported by Ambire, Trust Wallet, and growing

**Key Capabilities:**
- **Gasless transactions**: Paymasters sponsor gas in ERC-20 or fiat
- **Batch operations**: Multiple actions in single transaction
- **Social recovery**: Multi-sig or guardian-based key recovery
- **Session keys**: Limited permissions for dApps without full wallet access

### Smart Wallet Development

```solidity
// Minimal ERC-4337 Account (simplified)
import "@account-abstraction/contracts/core/BaseAccount.sol";

contract SimpleAccount is BaseAccount {
    address public owner;

    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external override returns (uint256 validationData) {
        // Verify signature
        require(_validateSignature(userOp, userOpHash), "Invalid sig");
        // Pay prefund if needed
        if (missingAccountFunds > 0) {
            (bool success,) = payable(msg.sender).call{value: missingAccountFunds}("");
            require(success);
        }
        return 0; // Valid
    }
}
```

---

## Layer 2 Development (Jan 2026)

> **Market Share**: Base (46.58%) + Arbitrum (30.86%) = 75%+ of L2 DeFi TVL. All major optimistic rollups now Stage 1 with live fraud proofs.

### L2 Selection Guide

| L2 | Type | Best For | Key Feature |
|----|------|----------|-------------|
| Base | Optimistic | Consumer apps, mainstream adoption | Coinbase integration, low fees |
| Arbitrum | Optimistic | DeFi, mature ecosystem | Largest TVL, DAO grants |
| Optimism | Optimistic | Public goods, Superchain | OP Stack, grant programs |
| zkSync Era | ZK-Rollup | Fast finality, native AA | zkEVM, no withdrawal delay |
| StarkNet | ZK-Rollup | Cairo development, ZK-native | STARK proofs, custom VM |

### Enterprise Rollups (2025-2026 Trend)

Major institutions launching L2s on OP Stack:
- **Kraken INK** - Exchange-native L2
- **Uniswap UniChain** - DeFi-optimized
- **Sony Soneium** - Gaming and media
- **Robinhood** - Arbitrum integration

### EIP-4844 Blob Optimization

Since March 2024, rollups use blob-based data posting:
```text
Before: calldata posting → expensive
After:  blob posting → 50%+ DA cost reduction
```

Optimism, zkSync optimized batching for blobs in 2025.

---

### LLM Limitations in Smart Contracts

**Do not rely on LLMs for:**

- Security-critical logic verification
- Gas optimization calculations
- Complex mathematical proofs

**Use LLMs for:**

- Boilerplate generation (tests, docs)
- Code explanation and review prep
- Initial vulnerability hypotheses (verify manually)

---

## Navigation

**Resources**

- [references/blockchain-best-practices.md](references/blockchain-best-practices.md) — Universal blockchain patterns and security
- [references/backend-integration-best-practices.md](references/backend-integration-best-practices.md) — .NET/C# crypto integration patterns (CQRS, Kafka, multi-provider)
- [references/solidity-best-practices.md](references/solidity-best-practices.md) — Solidity/EVM-specific guidance
- [references/rust-solana-best-practices.md](references/rust-solana-best-practices.md) — Solana + Anchor patterns
- [references/cosmwasm-best-practices.md](references/cosmwasm-best-practices.md) — Cosmos/CosmWasm guidance
- [references/ton-best-practices.md](references/ton-best-practices.md) — TON contracts (Tact/Fift/FunC) and deployment
- [../software-security-appsec/references/smart-contract-security-auditing.md](../software-security-appsec/references/smart-contract-security-auditing.md) — Smart contract audit workflows and tools (see software-security-appsec skill)
- [README.md](README.md) — Folder overview and usage notes
- [data/sources.json](data/sources.json) — Curated external references per chain
- Shared secure review checklist: [../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md)

**Templates**
- Ethereum/EVM: [assets/ethereum/template-solidity-hardhat.md](assets/ethereum/template-solidity-hardhat.md), [assets/ethereum/template-solidity-foundry.md](assets/ethereum/template-solidity-foundry.md)
- Solana: [assets/solana/template-rust-anchor.md](assets/solana/template-rust-anchor.md)
- Cosmos: [assets/cosmos/template-cosmwasm.md](assets/cosmos/template-cosmwasm.md)
- TON: [assets/ton/template-tact-blueprint.md](assets/ton/template-tact-blueprint.md), [assets/ton/template-func-blueprint.md](assets/ton/template-func-blueprint.md)
- Bitcoin: [assets/bitcoin/template-bitcoin-core.md](assets/bitcoin/template-bitcoin-core.md)

**Related Skills**

- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Security hardening, threat modeling, OWASP vulnerabilities
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System decomposition, modularity, dependency design
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — Infrastructure, CI/CD, observability for blockchain nodes
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API integration with smart contracts, RPC nodes, indexers
- [../qa-resilience/SKILL.md](../qa-resilience/SKILL.md) — Resilience, circuit breakers, retry logic for chains
- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) — Code review patterns and quality gates
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) — RESTful design for Web3 APIs and dApp backends

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about Web3/crypto development, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best blockchain for [use case]?"
- "What should I use for [smart contracts/DeFi/NFTs]?"
- "What's the latest in Web3 development?"
- "Current best practices for [Solidity/auditing/gas optimization]?"
- "Is [chain/protocol] still relevant in 2026?"
- "[Ethereum] vs [Solana] vs [other L1/L2]?"
- "Best framework for [smart contract development]?"

### Required Searches

1. Search: `"Web3 development best practices 2026"`
2. Search: `"[Ethereum/Solana/Base] development updates 2026"`
3. Search: `"smart contract security 2026"`
4. Search: `"[Hardhat/Foundry] comparison 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What chains/tools are popular NOW
- **Emerging trends**: New protocols or patterns gaining traction
- **Deprecated/declining**: Chains or approaches losing relevance
- **Recommendation**: Based on fresh data and ecosystem activity

### Example Topics (verify with fresh search)

- L2 ecosystem growth (Base, Arbitrum, Optimism)
- Solidity vs Rust for smart contracts
- Foundry vs Hardhat tooling
- Account abstraction (ERC-4337) adoption
- Cross-chain bridges and interoperability
- DeFi security patterns and audit practices

---

## Operational Playbooks
- [references/operational-playbook.md](references/operational-playbook.md) — Smart contract architecture, security-first workflows, and platform-specific patterns
