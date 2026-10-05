# Crypto/Web3 Pattern Index

This file used to hold a condensed copy of patterns that live in full in the dedicated references, including an outdated SafeMath recipe. It is now an index; follow the link for the current version of each pattern.

| Topic | Owner reference |
|---|---|
| Contract architecture, access control, upgradeability (UUPS/transparent proxies, ERC-7201 storage), gas optimization, Solidity pitfalls | [solidity-best-practices.md](solidity-best-practices.md) |
| Chain-agnostic design, testing strategy (unit, fork, fuzz, invariant), deployment and verification | [blockchain-best-practices.md](blockchain-best-practices.md) |
| Security review, audit workflow, tool matrix, vulnerability checklists | [smart-contract-security-auditing.md](smart-contract-security-auditing.md) |
| DeFi: AMMs, lending, ERC-4626 vaults, oracles, flash-loan resistance | [defi-protocol-patterns.md](defi-protocol-patterns.md) |
| Token and NFT standards (ERC-20/721/1155, metadata storage) | [nft-token-standards.md](nft-token-standards.md) |
| Backend integration: multi-provider RPC, CQRS commands, webhook signature checks, transaction lifecycle state machines, event-driven payments | [backend-integration-best-practices.md](backend-integration-best-practices.md) |
| Bridges and cross-chain messaging | [cross-chain-bridges.md](cross-chain-bridges.md) |
| Solana / Anchor | [rust-solana-best-practices.md](rust-solana-best-practices.md) |
| Cosmos / CosmWasm | [cosmwasm-best-practices.md](cosmwasm-best-practices.md) |
| TON | [ton-best-practices.md](ton-best-practices.md) |
| EU/US/UK regulatory engineering controls | [mica-casp-checklist.md](mica-casp-checklist.md) |

Chain templates live in `../assets/` (Foundry, Hardhat, Anchor, CosmWasm, Bitcoin Core, TON).

## On-Chain vs Off-Chain Data

| Data type | Storage | Reason |
|---|---|---|
| Balances, ownership | On-chain | Security-critical; needs consensus |
| NFT metadata | Content-addressed storage (IPFS/Arweave) + on-chain URI or hash | Immutability at lower cost |
| Historical/queryable data | Indexer (subgraph or custom) | Query efficiency; rebuildable from chain |
| User preferences | Off-chain DB | Mutable, non-critical |
| Large files | Arweave/Filecoin or object storage with on-chain hash | Cost; integrity via hash |

Anything off-chain that affects value (prices, allowlists, reserve data) needs an integrity check (signature, hash, or oracle) where it is consumed.
