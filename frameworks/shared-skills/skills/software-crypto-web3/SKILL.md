---
name: software-crypto-web3
description: "Guides secure blockchain development across EVM, Bitcoin, Solana, Cosmos, and TON. Use when building contracts, wallets, custody flows, bridges, or on-chain backends."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Software Crypto/Web3 Engineering

Use this skill to design, implement, and review production blockchain systems: contracts and programs, signing and custody, protocol integrations, testing, audits, and operational controls.

Defaults to:
- Security-first design with explicit threat models
- Comprehensive testing: unit, integration, fork/simulation, fuzzing, invariants
- Formal methods for high-value paths
- Conservative key custody and signing controls
- Fresh web verification for volatile ecosystem facts

## Quick Reference

| Task | Default | Use When |
|------|---------|----------|
| EVM contracts | Foundry first, Hardhat when plugin-heavy TS workflows matter | Solidity, DeFi, token standards, upgradeable systems |
| Solana programs | Anchor + current Solana SDK guidance | Rust programs, SPL assets, high-throughput apps |
| Cosmos contracts | CosmWasm | IBC-native or Cosmos appchain ecosystems |
| TON contracts | Tact or FunC + Blueprint | Telegram distribution, TON-native wallets and assets |
| Bitcoin/Lightning | Bitcoin Core + BDK/LND patterns | Wallets, PSBT, settlement, payment rails |
| Account abstraction | ERC-7702 for EOAs, ERC-4337 for smart accounts | Batched txs, gas sponsorship, session keys, social recovery |
| Security review | Slither, Echidna, Medusa, Halmos, Certora | Audits, pre-deploy review, invariant enforcement |
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

## Workflow

1. Identify the chain, product surface, custody model, and attack surface before recommending tooling.
2. Route generic backend, frontend, or non-crypto AppSec work to the adjacent skill when blockchain is incidental.
3. Pick the smallest viable protocol or framework from the decision tree.
4. Apply execution defaults for contracts, signing, settlement, and operational controls before discussing implementation detail.
5. Re-check volatile ecosystem claims, network support, and tool maturity with the navigation sources before final guidance.

## ASCII Flow

```text
Crypto or Web3 task
  -> Define asset, chain, wallet, contract, or custody boundary
  -> Classify risk: key, transaction, smart contract, bridge, or compliance
  -> Design least-privilege signing and replay protection
  -> Add monitoring, rollback, and incident response hooks
  -> Verify current protocol, wallet, and chain behavior
  -> Hand off legal or audit needs explicitly
```

## Decision Tree

Choose the smallest surface area that meets the product need:

- EVM if ecosystem depth, audits, and tooling maturity dominate
- Solana if throughput and low fees dominate and the team can operate Rust safely
- CosmWasm if IBC-native interoperability is a core requirement
- TON if Telegram-native distribution is a product requirement
- Bitcoin/Lightning if the system is payment-settlement or wallet heavy rather than contract heavy

Prefer:
- Foundry for EVM testing, fuzzing, invariants, and gas snapshots
- Hardhat when plugin ecosystem or TS-heavy workflows are the real driver
- Latest stable Solidity 0.8.x (0.8.36 as of July 2026 — always confirm at soliditylang.org/releases; the patch version moves roughly monthly) for transient storage (EIP-1153), Pectra/Fusaka-era EVM features, and ERC-7201 namespace builtins
- ERC-7702 for EOA migration (retains existing address history, live since Pectra mainnet activation May 2025); ERC-4337 for new smart accounts or when full bundler/paymaster infrastructure is required — the two are complementary and increasingly deployed together, not mutually exclusive
- Chainlink CCIP when bridge security (independent Risk Management Network) is the top priority; LayerZero or Wormhole for broader chain coverage — verify current DVN/guardian set and audit status before trusting a bridge with material value
- L2s only after verifying current network support, bridge assumptions, and operational maturity — Arbitrum One and Base currently account for roughly three-quarters of L2 DeFi liquidity, with OP Mainnet, Starknet, Linea, and zkSync Era trailing; treat any specific TVL/market-share figure as a snapshot to re-verify, not a durable fact
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
- [ ] Integer overflow: confirmed Solidity 0.8+ or explicit SafeMath used throughout
- [ ] Replay protection: nonces or EIP-712 domain separator on all signed payloads
- [ ] Deposit/withdrawal handlers: idempotency key, confirmation threshold, and DLQ defined
- [ ] Oracle inputs: freshness check (max age); no single source of price truth
- [ ] Emergency controls: pause mechanism or time-lock tested in rehearsal
- [ ] Upgrade path: proxy admin key held by multisig, not EOA; upgrade procedure documented
- [ ] Fuzz and invariant tests pass with ≥ 10,000 runs (Echidna or Foundry)

## Custody, Key Management, and On-Chain Judgment

- **When NOT to put something on-chain**: personally identifiable data, anything requiring later deletion/correction (right-to-erasure conflicts), high-frequency state that is cheaper and equally trustworthy off-chain with a periodic on-chain checkpoint/root, and business logic whose only requirement is internal auditability rather than public verifiability or trustless settlement. On-chain is a cost/trust tradeoff, not a default.
- **Custody decision gates**:
  - Solo/EOA signing — prototypes and non-custodial personal wallets only; never for pooled user funds.
  - Multisig (Safe or equivalent) — the default for treasury and admin/upgrade keys; transparent on-chain quorum, but every signer's device and review discipline becomes part of the trust boundary (see Bybit below).
  - MPC (threshold signatures) — preferred for hot-wallet operational signing at scale: no single key material ever exists in one place, policy engines can gate transactions pre-signature, and key rotation doesn't require an on-chain migration. Higher implementation and vendor-trust complexity than multisig.
  - HSM — for cold/root keys and where a compliance regime requires FIPS-validated hardware custody; pair with M-of-N operator access, not a single operator.
  - Choose based on: value at risk, signing frequency, regulatory custody requirements, and whether the failure mode you're defending against is key theft, insider collusion, or vendor compromise — these call for different controls.
- **Private-key operational security**: never display or transmit raw key material through a UI you don't control end-to-end; treat any "review and sign" screen (browser extension, hardware wallet display, Safe UI) as part of the attack surface — a compromised front end can present a benign-looking transaction while submitting a malicious one. The February 2025 Bybit hack ($1.5B in ETH, the largest crypto theft on record, attributed to the North Korea-linked Lazarus Group) worked exactly this way: attackers compromised a Safe{Wallet} front-end component so that multisig signers approved a malicious transfer disguised as a routine one, blind-signing what their hardware wallets could not meaningfully verify. The lesson generalizes: verify calldata against an independent source before signing, not just the UI's rendering of it.
- **Testnet-vs-mainnet deployment discipline**: never assume testnet gas, mempool, MEV, or reorg behavior predicts mainnet behavior. Require a mainnet-fork simulation (Foundry/Anvil or Tenderly) pass before any mainnet deploy touching real value, and gate mainnet deploy keys and upgrade keys separately from testnet keys so a testnet compromise cannot reach production.
- **Oracle-manipulation failure modes**: single-block spot prices (raw DEX reserves, single-source feeds) are manipulable within one transaction via flash loans; prefer time-weighted averages (TWAP) or aggregated push/pull oracles (Chainlink, Pyth) with staleness and deviation checks, and treat "no single source of price truth" (see checklist above) as a hard requirement, not a nice-to-have, for anything gating liquidations or borrowing power.

## Known Traps

- Relying on local or testnet behavior for gas, mempool, and reorg assumptions that fail on the target network.
- Treating indexed events as the source of truth when the contract state, wallet balance, or final settlement system is authoritative.
- Building deposit and withdrawal handlers without replay protection, confirmation thresholds, and idempotent bookkeeping.
- Assuming bridge, relayer, or paymaster trust boundaries are infrastructure details rather than core product risk.
- Upgrading proxies, account abstraction flows, or signer policies without rehearsed rollback and frozen-state procedures.
- Treating wallet UX failure as harmless when incorrect chain selection, stale allowance state, or signature confusion can burn funds.

## Common Anti-Patterns

- Writing custom crypto, bridge, or signing schemes where audited primitives and provider controls already exist.
- Using one hot wallet or signer path for every operational action instead of role separation, limits, and approvals.
- Optimizing for chain novelty, throughput, or token narrative before confirming liquidity, custody, and incident response viability.
- Treating audits as a substitute for invariants, simulations, and operational kill switches.
- Assuming off-chain jobs are eventually consistent by default rather than proving ordering, retries, and reconciliation behavior.

## Output Guidelines

When using this skill, prefer answers that:
- Start with the safest viable architecture
- Separate protocol facts from implementation opinion
- Make trust assumptions explicit
- Recommend concrete tests, invariants, and operational controls
- Mark volatile claims as verified or unverified

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
- [references/operational-playbook.md](references/operational-playbook.md) - Condensed cross-topic pattern reference (contract architecture, DeFi, token standards, backend/webhook integration) — a quick-recall summary, not a standalone deployment/monitoring runbook; see the dedicated reference files above for full depth
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

## Freshness Protocol

Use web search and web fetch whenever the answer depends on:
- Current chain or framework relevance
- Tooling status, releases, support, or deprecations
- Account abstraction, L2, bridge, or wallet ecosystem changes
- Current docs paths, pricing, grants, or provider availability

Research order:
1. Official docs, standards, specs, and primary repositories
2. Canonical ecosystem analytics such as L2Beat, The Graph, Dune, DefiLlama
3. Community sources only as secondary context

When reporting fresh guidance:
- Cite the source link
- Distinguish stable principles from July 2026 ecosystem state — this domain moves fast enough that any specific version, TVL figure, or regulatory deadline should be re-verified rather than trusted from memory
- Call out trust assumptions for bridges, relayers, paymasters, and custodians

## Regulatory Traps (verified as of July 2026)

- **MiCA CASP authorisation (Title V) — applicable since 30 December 2024**: any entity providing crypto-asset services in the EU must hold a CASP licence from a national competent authority. The Article 143 national grandfathering period for firms already operating under prior national law ends **1 July 2026 at the latest** for every member state — this is the hard EU-wide backstop, not a date already in the past. Several member states set shorter national windows that closed earlier (e.g., the Netherlands, Finland, Latvia, Hungary, and Slovenia closed theirs by mid-2025; Sweden by September 2025); others used the full 18 months with their own filing-date conditions. Always confirm the specific member state's deadline and any conditions rather than assuming the 1 July 2026 backstop applies uniformly.
- **MiCA whitepaper rules (Title II/IV)**: CASPs and issuers must publish and notify a standardised crypto-asset whitepaper before offering tokens to the public; marketing materials must be consistent with the whitepaper and clearly labelled as such.
- **MiCA marketing communication rules**: all promotions must be fair, clear, and not misleading; risk warnings are mandatory; whitepaper link must appear in every marketing material.
- **Travel Rule (TFR — Transfer of Funds Regulation recast)**: since 30 December 2024, VASPs/CASPs must collect and transmit originator and beneficiary information for all crypto transfers regardless of amount; no EUR 1,000 threshold exemption that applied to fiat.
- **Stablecoin (ART/EMT) issuance caps**: asset-referenced tokens (ART) and e-money tokens (EMT) classified as "significant" by EBA face daily transaction volume caps and mandatory interoperability requirements.
- **Stablecoin reserve and custody rules**: ART/EMT issuers must hold 1:1 reserves in segregated custody; reserve composition, audit, and redemption rights are strictly prescribed — check EUR-Lex 2023/1114 (MiCA) Arts. 36–45.
- **US GENIUS Act (payment stablecoins)**: signed into law 18 July 2025, establishing a federal framework for permitted payment stablecoin issuers (bank and nonbank) with reserve, redemption, and disclosure requirements. Federal regulators (OCC, FDIC, Federal Reserve) were on a one-year rulemaking clock and were due to finalize implementing rules by **18 July 2026** — treat the exact rule text and effective dates as still-moving and verify against the current Federal Register docket before relying on specifics.
- **US CLARITY Act (market structure)**: passed the House 294-134 in July 2025 but had **not** been enacted as of mid-2026; Senate negotiations (Banking Committee markup targeted for spring 2026, a Tillis-Alsobrooks compromise on stablecoin yield) were ongoing, with floor passage, committee reconciliation, and presidential signature all still pending. Do not assume CLARITY Act obligations apply until it is signed into law — verify current status before advising on it.
- **UK position**: the UK's Financial Services and Markets Act 2023 (FSMA 2023) brought cryptoasset activities into the regulated perimeter. The FCA finalized its core cryptoasset regime rules via a package of policy statements published 30 June 2026 (stablecoin issuance, custody/safeguarding, trading and intermediation, and prudential/reporting requirements); the authorisation gateway opens 30 September 2026 and the regime is expected to take effect around 25 October 2027. Cite the specific current-year policy statement (not an older consultation paper) when advising UK-regulated firms, and re-verify the gateway/effective dates as they can shift.
- **MiCA does not cover NFTs by default**: unique, non-fungible tokens fall outside scope unless they qualify as financial instruments or are issued in large series that resemble fungible tokens.
- **DeFi and DAOs**: MiCA recital 22 provisionally excludes fully decentralised protocols from CASP obligations, but the "sufficiently decentralised" test remains guidance-dependent — do not assume exemption without a current analysis.
- **Enforcement risk**: national competent authorities have supervisory and enforcement powers against non-compliant CASPs once the grandfathering backstop closes; build compliance evidence into onboarding and product design, not post-launch.

See [references/mica-casp-checklist.md](references/mica-casp-checklist.md) for a structured CASP readiness checklist.

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

