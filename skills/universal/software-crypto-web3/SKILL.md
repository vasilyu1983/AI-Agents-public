---
name: software-crypto-web3
description: "Guides secure blockchain development across EVM, Bitcoin, Solana, Cosmos, and TON. Use when building contracts, wallets, custody flows, bridges, or on-chain backends."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Software Crypto/Web3 Engineering

## Quick Reference

| Task | Default | Use When |
|------|---------|----------|
| EVM contracts | Foundry first, Hardhat when plugin-heavy TS workflows matter | Solidity, DeFi, token standards, upgradeable systems |
| Solana programs | Anchor + current Solana SDK guidance | Rust programs, SPL assets, high-throughput apps |
| Cosmos contracts | CosmWasm | IBC-native or Cosmos appchain ecosystems |
| TON contracts | Tolk for new contracts; verify supported toolkit in TON docs | Telegram distribution, TON-native wallets and assets |
| Bitcoin/Lightning | Bitcoin Core + BDK/LND patterns | Wallets, PSBT, settlement, payment rails |
| Account abstraction | ERC-7702 for EOAs (delegation persists; guard callers), ERC-4337 for smart accounts | Batched txs, gas sponsorship, session keys, social recovery |
| Security review | Slither, Echidna, Medusa, Halmos, Certora; [audit guide](references/smart-contract-security-auditing.md) | Audits, pre-deploy review, invariant enforcement |
| Cross-chain | Chainlink CCIP, LayerZero, Wormhole, IBC | Token bridges, cross-chain messaging, interoperability |
| Backend integration | Queue-backed RPC clients + idempotent handlers | Custody, deposits, withdrawals, webhook/event ingestion |
| Research | Official docs/specs first, then ecosystem analytics | Chain selection, framework choice, current best practice |

## When to Use This Skill

- Smart contract and blockchain program development
- DeFi, token, NFT, governance, and bridge integrations
- Backend crypto infrastructure, custody, and signing workflows
- Chain and framework tradeoff analysis
- Security reviews, audit preparation, and production hardening

## When NOT to Use This Skill

- **General backend work with no blockchain component** → [software-backend](../software-backend/SKILL.md)
- **Pure frontend UI work with no wallet/protocol integration** → [software-frontend](../software-frontend/SKILL.md)
- **Generic application security outside smart contracts and crypto ops** → [software-security-appsec](../software-security-appsec/SKILL.md)
- **Move implementations on Sui/Aptos** are outside this skill's chain coverage. Start from [Sui Move](https://docs.sui.io/concepts/sui-move-concepts) or [Aptos Move](https://aptos.dev/en/build/smart-contracts); use this skill only for shared custody and operational risk controls, and do not transplant EVM/Anchor code.

## Workflow

1. Identify the chain, product surface, custody model, and attack surface before recommending tooling.
2. Route generic backend, frontend, or non-crypto AppSec work to the adjacent skill when blockchain is incidental.
3. Pick the smallest viable protocol or framework from the decision tree.
4. Apply execution defaults for contracts, signing, settlement, and operational controls before discussing implementation detail.
5. Re-check network support and tool maturity with the relevant official source before final guidance. For Solana, load [toolchain and extension gates](references/rust-solana-best-practices.md#solana-toolchain-and-token-extensions); for TON, load [language/toolkit selection](references/ton-best-practices.md#language-and-toolkit-selection).


## Decision Tree

Choose the smallest surface area that meets the product need:

- EVM if ecosystem depth, audits, and tooling maturity dominate
- Solana if throughput and low fees dominate and the team can operate Rust safely
- CosmWasm if IBC-native interoperability is a core requirement
- TON if Telegram-native distribution is a product requirement; check Tolk and toolkit guidance before choosing a language
- Bitcoin/Lightning if the system is payment-settlement or wallet heavy rather than contract heavy

Prefer:
- Foundry for EVM testing, fuzzing, invariants, and gas snapshots
- Hardhat 3 (runs Solidity tests natively; check hardhat.org for its current release status) when plugin ecosystem or TS-heavy workflows are the real driver; Nomic Foundation will not upgrade Hardhat 2 for every future hardfork, so plan the migration off Hardhat 2
- A reviewed Solidity compiler compatible with the target EVM. Read [releases](https://github.com/ethereum/solidity/releases) and [known bugs](https://docs.soliditylang.org/en/latest/bugs.html) for the chosen optimizer/IR pipeline, including transient-storage handling; pin the exact compiler and keep every pragma compatible.
- ERC-7702 for EOA migration (retains existing address history, live since the Pectra upgrade; the delegation **persists** until re-delegated or cleared by delegating to the zero address, so delegate code must check `msg.sender == address(this)` or a signature before executing, and wallets must treat delegation requests as high-risk phishing targets); ERC-4337 for new smart accounts or when full bundler/paymaster infrastructure is required — the two are complementary and increasingly deployed together, not mutually exclusive
- Chainlink CCIP when bridge security (independent Risk Management Network) is the top priority; LayerZero or Wormhole for broader chain coverage — verify current DVN/guardian set and audit status before trusting a bridge with material value
- L2s only after verifying current network support, bridge assumptions, and operational maturity; check L2Beat or DefiLlama for current liquidity rather than trusting a remembered market-share figure
- Existing audited protocol components over custom bridge or custom cryptography work

## Execution Defaults

- Treat contracts, signing services, and webhook endpoints as public attack surfaces
- Require idempotency for deposit, withdrawal, and settlement handlers
- Separate read paths from transaction-submission paths
- Rate-limit hot wallet automation and require approvals for high-risk transfers
- Prefer allowlists, timelocks, pausability, and rollback plans where they reduce blast radius
- Never trust ecosystem popularity claims without fresh verification

## Pre-Deploy Security Checklist

Before deploying a contract or custody flow to production:

- [ ] Reentrancy guards on all external-call paths (CEI pattern or `ReentrancyGuard`)
- [ ] Access control: every privileged function has an explicit owner/role check
- [ ] Integer overflow: Solidity 0.8+ checked arithmetic (no SafeMath needed); every `unchecked` block justified in review
- [ ] Replay protection: nonce/expiry consumption plus domain binding (chain, verifying contract, action); EIP-712 formatting alone does not stop same-domain replay
- [ ] Deposit/withdrawal handlers: idempotency key, confirmation threshold, and DLQ defined
- [ ] Oracle inputs: freshness check (max age); no single source of price truth
- [ ] Emergency controls: pause mechanism or time-lock tested in rehearsal
- [ ] Upgrade path: proxy admin key held by multisig, not EOA; upgrade procedure documented
- [ ] Fuzz and invariant tests pass (Foundry, Echidna, or Medusa) with a run/depth budget set per protocol risk; raise it above tool defaults for value-bearing code

## Custody, Key Management, and On-Chain Judgment

**Privileged-control gate.**

Inventory every upgrade, pause, mint, freeze, oracle, bridge, and fee-setting authority as part of the protocol surface. For each authority, record the signer set, quorum, delay, scope, rotation path, and failure consequence. Test compromised-signer, unavailable-signer, and malicious-upgrade scenarios on a fork or local chain; a multisig label alone does not prove that privileged actions are constrained or recoverable.

- **When NOT to put something on-chain**: personally identifiable data, anything requiring later deletion/correction (right-to-erasure conflicts), high-frequency state that is cheaper and equally trustworthy off-chain with a periodic on-chain checkpoint/root, and business logic whose only requirement is internal auditability rather than public verifiability or trustless settlement. On-chain is a cost/trust tradeoff, not a default.
- **Custody decision gates**:
  - Solo/EOA signing — prototypes and non-custodial personal wallets only; never for pooled user funds.
  - Multisig (Safe or equivalent) — the default for treasury and admin/upgrade keys; transparent on-chain quorum, but every signer's device and review discipline becomes part of the trust boundary (see signing gates below).
  - MPC (threshold signatures) — preferred for hot-wallet operational signing at scale: the protocol can sign using distributed key shares without reconstructing a complete key. Verify threshold, independent share/control domains, recovery, policy bypass paths, and vendor trust; share refresh and changing the public key have different migration consequences.
  - HSM — for cold/root keys and where a compliance regime requires FIPS-validated hardware custody; pair with M-of-N operator access, not a single operator.
  - Choose based on: value at risk, signing frequency, regulatory custody requirements, and whether the failure mode you're defending against is key theft, insider collusion, or vendor compromise — these call for different controls.
- **Clear-signing gate**: decode destination, chain, value, method, recipients, allowances, and nested calls against independently obtained contract/ABI data before a privileged signature. Use [ERC-7730](https://ercs.ethereum.org/ERCS/erc-7730) descriptors where the wallet supports them; verify its supported schema and bind the descriptor to chain/address/signature type. Unknown/mismatched descriptors and opaque critical fields block privileged signing until independently decoded. A readable display cannot prove safe intent: descriptor registries and external metadata are trust boundaries too.
- **Wallet front-end supply chain**: lock and review dependencies/build inputs, constrain mutable third-party scripts, protect release/CDN credentials, verify served asset provenance, and rehearse a compromised-UI case. For treasury/admin flows, compare the actual payload on an independent signing path; a compromised dApp can render a benign summary while requesting another signature.
- **Testnet-vs-mainnet deployment discipline**: never assume testnet gas, mempool, MEV, or reorg behavior predicts mainnet behavior. Require a mainnet-fork simulation (Foundry/Anvil or Tenderly) pass before any mainnet deploy touching real value, and gate mainnet deploy keys and upgrade keys separately from testnet keys so a testnet compromise cannot reach production.
- **Oracle-manipulation failure modes**: single-block spot prices (raw DEX reserves, single-source feeds) are manipulable within one transaction via flash loans; prefer time-weighted averages (TWAP) or aggregated push/pull oracles (Chainlink, Pyth) with staleness and deviation checks, and treat "no single source of price truth" (see checklist above) as a hard requirement, not a nice-to-have, for anything gating liquidations or borrowing power.
- **LLM or agent with signing authority** (trading, swaps, treasury moves): assume the model will at some point be talked into a harmful transaction by on-chain text, token names, feeds, or webhooks, and make every control below hold regardless of model output. Keyword filters for prompt injection are easy to bypass; do not count them as a control.
  - Per-transaction and rolling-window spend caps, enforced in code between the model and the signer, with limits set in local policy.
  - Simulate each transaction (`eth_call` or a fork) and refuse to sign unless a minimum-output and a deadline are set and the simulated result meets them.
  - A drawdown and loss-streak breaker that halts trading and requires a human to resume; it also halts on invalid state (zero or missing baseline value).
  - A dedicated hot wallet funded only for the session, never the treasury, with keys from a secret manager. Use protected routing (private mempool) where sandwich risk applies.
  - An audit log of every model decision, including refused and failed ones, not only sent transactions.

## Known Traps

- Relying on local or testnet behavior for gas, mempool, and reorg assumptions that fail on the target network.
- Treating indexed events as the source of truth when the contract state, wallet balance, or final settlement system is authoritative.
- Building deposit and withdrawal handlers without replay protection, confirmation thresholds, and idempotent bookkeeping.
- Assuming bridge, relayer, or paymaster trust boundaries are infrastructure details rather than core product risk.
- Upgrading proxies, account abstraction flows, or signer policies without rehearsed rollback and frozen-state procedures.
- Treating wallet UX failure as harmless when incorrect chain selection, stale allowance state, or signature confusion can burn funds.

## Navigation

Resources:
- [references/blockchain-best-practices.md](references/blockchain-best-practices.md) - Universal blockchain architecture and security patterns
- [references/backend-integration-best-practices.md](references/backend-integration-best-practices.md) - Backend custody, webhooks, queues, CQRS, provider abstraction (.NET/C# examples; architecture patterns are language-agnostic)
- [references/solidity-best-practices.md](references/solidity-best-practices.md) - EVM and Solidity guidance
- [references/rust-solana-best-practices.md](references/rust-solana-best-practices.md) - Solana + Anchor patterns
- [references/cosmwasm-best-practices.md](references/cosmwasm-best-practices.md) - CosmWasm and IBC guidance
- [references/ton-best-practices.md](references/ton-best-practices.md) - TON contract and wallet integration patterns
- [references/defi-protocol-patterns.md](references/defi-protocol-patterns.md) - AMMs, lending, vaults, staking, oracles
- [references/nft-token-standards.md](references/nft-token-standards.md) - ERC-20/721/1155, SPL assets, NFT metadata
- [references/cross-chain-bridges.md](references/cross-chain-bridges.md) - Bridge models, trust assumptions, and risk controls
- [references/operational-playbook.md](references/operational-playbook.md) - Topic-to-reference index plus the on-chain vs off-chain data table
- [data/sources.json](data/sources.json) - Curated external references and research starting points

Templates:
- Ethereum/EVM: [assets/ethereum/template-solidity-hardhat.md](assets/ethereum/template-solidity-hardhat.md), [assets/ethereum/template-solidity-foundry.md](assets/ethereum/template-solidity-foundry.md)
- Solana: [assets/solana/template-rust-anchor.md](assets/solana/template-rust-anchor.md)
- Cosmos: [assets/cosmos/template-cosmwasm.md](assets/cosmos/template-cosmwasm.md)
- TON: [assets/ton/template-tact-blueprint.md](assets/ton/template-tact-blueprint.md), [assets/ton/template-func-blueprint.md](assets/ton/template-func-blueprint.md)
- Bitcoin: [assets/bitcoin/template-bitcoin-core.md](assets/bitcoin/template-bitcoin-core.md)

Related skills:
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) - Threat modeling and security hardening
- [../software-backend/SKILL.md](../software-backend/SKILL.md) - Backend services, APIs, queues, persistence
- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) - Review process and correctness checks
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) - Infra, CI/CD, observability, node operations
- [../qa-resilience/SKILL.md](../qa-resilience/SKILL.md) - Failure modes, retries, circuit breakers
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) - API boundaries for custody and blockchain-facing services

## Ecosystem Lookups

Before recommending a framework, network, bridge, or wallet feature, read its official release/support documentation and the exact deployed configuration. Use ecosystem analytics only for current liquidity/adoption comparisons; quote no remembered market-share or throughput figure. Cite the source and the trust assumptions that affect the choice.

## Regulatory Traps (Engineering Controls Only)

Legal status, licensing, and deadlines are owned by the legal skills; do not restate them here. Build these controls regardless of jurisdiction:

- **Travel Rule plumbing**: configure required originator/beneficiary fields, self-hosted-wallet evidence, and exception handling from counsel-approved jurisdiction and transfer rules; model an explicit "counterparty not Travel-Rule capable" state.
- **Custody segregation and reconciliation**: client assets segregated from house assets; daily on-chain-to-ledger reconciliation gates withdrawals.
- **Stablecoin issuance systems**: counsel-approved issuer/asset eligibility, redemption rules, and per-currency-area means-of-exchange telemetry; parameterize thresholds and rehearse a "pause issuance" switch.
- **Marketing gate**: public offer pages and promotions ship only against a current white paper version; geo-gate unauthorised jurisdictions and log the decision.
- **Classification evidence**: keep admin-key, upgrade-path, fee-switch, and token-uniqueness metadata; NFT and "fully decentralised" scope are legal calls.

Checklist: [references/mica-casp-checklist.md](references/mica-casp-checklist.md). Status and deadlines: qualified EU regulatory counsel (MiCA, TFR), qualified US regulatory counsel (GENIUS Act rulemaking, CLARITY Act), qualified UK regulatory counsel (FCA cryptoasset regime).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
