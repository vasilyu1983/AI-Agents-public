# NFT and Token Standards Implementation Guide

Production patterns for implementing fungible tokens (ERC-20), non-fungible tokens (ERC-721, ERC-1155), and Solana token standards (SPL Token, Metaplex). Covers implementation details, metadata patterns, security considerations, and common vulnerabilities.

---

## Table of Contents

1. [ERC-20: Fungible Tokens](#erc-20-fungible-tokens)
2. [ERC-721: Non-Fungible Tokens](#erc-721-non-fungible-tokens)
3. [ERC-1155: Multi-Token Standard](#erc-1155-multi-token-standard)
4. [SPL Token (Solana)](#spl-token-solana)
5. [Metaplex (Solana NFTs)](#metaplex-solana-nfts)
6. [Token Gating Patterns](#token-gating-patterns)
7. [Metadata: On-Chain vs Off-Chain](#metadata-on-chain-vs-off-chain)
8. [Common Token Vulnerabilities](#common-token-vulnerabilities)
9. [Decision Framework](#decision-framework)

---

## ERC-20: Fungible Tokens

### Standard Implementation

```solidity
// Use OpenZeppelin for production tokens
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/access/Ownable2Step.sol";

contract MyToken is ERC20, ERC20Permit, Ownable2Step {
    uint256 public constant MAX_SUPPLY = 1_000_000_000e18; // 1 billion

    constructor()
        ERC20("My Token", "MTK")
        ERC20Permit("My Token")
        Ownable(msg.sender)
    {
        _mint(msg.sender, MAX_SUPPLY);
    }
}
```

### Approval Patterns

```solidity
// DANGER: Standard approve has a known race condition
// If you change approval from 100 to 50, attacker can:
// 1. Spend the 100 before the new approval
// 2. Then spend the 50 after the new approval

// SAFE: Use increaseAllowance/decreaseAllowance
token.increaseAllowance(spender, amount);
token.decreaseAllowance(spender, amount);

// BETTER: Use ERC-2612 Permit (gasless approvals)
// User signs a message off-chain, spender submits permit + transfer
function permitAndTransfer(
    address owner,
    uint256 amount,
    uint256 deadline,
    uint8 v, bytes32 r, bytes32 s
) external {
    token.permit(owner, address(this), amount, deadline, v, r, s);
    token.transferFrom(owner, address(this), amount);
}
```

### SafeERC20

```solidity
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract TokenHandler {
    using SafeERC20 for IERC20;

    // WRONG: Some tokens (USDT) don't return bool
    // token.transfer(to, amount);  // May silently fail

    // CORRECT: SafeERC20 handles non-standard tokens
    function safeTransfer(IERC20 token, address to, uint256 amount) external {
        token.safeTransfer(to, amount);  // Reverts on failure
    }
}
```

### ERC-20 Gotchas

| Issue | Description | Mitigation |
|-------|------------|------------|
| Fee-on-transfer tokens | Some tokens take a fee on transfer (actual received < sent) | Measure balance before/after transfer |
| Rebasing tokens | Balance changes without transfers (stETH) | Track shares, not balances |
| Pausable tokens | USDC can be frozen | Handle transfer failures gracefully |
| Blocklist tokens | USDC can block addresses | Handle transfer failures gracefully |
| Missing return value | USDT doesn't return bool | Use SafeERC20 |
| Decimals variation | USDC = 6, DAI = 18 | Always check `decimals()` |

---

## ERC-721: Non-Fungible Tokens

### Standard Implementation

```solidity
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/access/Ownable2Step.sol";

contract MyNFT is
    ERC721,
    ERC721Enumerable,
    ERC721URIStorage,
    ERC2981,
    Ownable2Step
{
    uint256 private _nextTokenId;
    uint256 public constant MAX_SUPPLY = 10_000;
    uint256 public mintPrice = 0.08 ether;

    constructor()
        ERC721("My NFT", "MNFT")
        Ownable(msg.sender)
    {
        // Set default royalty: 5% to owner
        _setDefaultRoyalty(msg.sender, 500); // 500 basis points = 5%
    }

    function mint(address to) external payable {
        require(msg.value >= mintPrice, "Insufficient payment");
        require(_nextTokenId < MAX_SUPPLY, "Max supply reached");

        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
    }

    // Required overrides for multiple inheritance
    function _update(address to, uint256 tokenId, address auth)
        internal override(ERC721, ERC721Enumerable)
        returns (address)
    {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 value)
        internal override(ERC721, ERC721Enumerable)
    {
        super._increaseBalance(account, value);
    }

    function tokenURI(uint256 tokenId)
        public view override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public view override(ERC721, ERC721Enumerable, ERC721URIStorage, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
```

### Metadata Standards (ERC-721)

```json
{
  "name": "My NFT #1",
  "description": "Description of the NFT",
  "image": "ipfs://QmHash/1.png",
  "animation_url": "ipfs://QmHash/1.mp4",
  "external_url": "https://mynft.com/1",
  "attributes": [
    { "trait_type": "Background", "value": "Blue" },
    { "trait_type": "Rarity", "value": "Legendary" },
    { "trait_type": "Level", "display_type": "number", "value": 5 },
    { "trait_type": "Power", "display_type": "boost_percentage", "value": 10 }
  ]
}
```

### Royalties (EIP-2981)

```solidity
// EIP-2981: NFT Royalty Standard
// Returns (receiver, royaltyAmount) for a given sale price
function royaltyInfo(uint256 tokenId, uint256 salePrice)
    external view returns (address receiver, uint256 royaltyAmount)
{
    // Default: 5% royalty to creator
    return (creator, salePrice * 500 / 10000);
}

// Per-token royalties (for collaborations)
function setTokenRoyalty(
    uint256 tokenId,
    address receiver,
    uint96 feeNumerator  // basis points (e.g., 500 = 5%)
) external onlyOwner {
    _setTokenRoyalty(tokenId, receiver, feeNumerator);
}
```

**Note**: EIP-2981 is informational -- marketplaces can choose to ignore it. OpenSea enforces royalties through its operator filter, but enforcement is not guaranteed on all platforms.

---

## ERC-1155: Multi-Token Standard

### When to Use ERC-1155

| Feature | ERC-721 | ERC-1155 |
|---------|---------|----------|
| Token type | One NFT per contract | Fungible + non-fungible in one contract |
| Batch operations | Not native | Native batch transfer/mint |
| Gas efficiency | Higher per transfer | Lower per transfer (batch) |
| Best for | PFP collections, art | Gaming items, memberships, tickets |
| Metadata | Per-token URI | URI template with `{id}` substitution |

### Implementation

```solidity
import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable2Step.sol";

contract GameItems is ERC1155, Ownable2Step {
    // Token IDs
    uint256 public constant GOLD = 0;       // Fungible
    uint256 public constant SILVER = 1;     // Fungible
    uint256 public constant SWORD = 2;      // Non-fungible (supply: 1 each)
    uint256 public constant SHIELD = 3;     // Semi-fungible (limited supply)

    constructor()
        ERC1155("https://game.example/api/item/{id}.json")
        Ownable(msg.sender)
    {}

    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts
    ) external onlyOwner {
        _mintBatch(to, ids, amounts, "");
    }

    // Batch transfer: multiple items in one transaction
    // safeTransferFrom -> single item
    // safeBatchTransferFrom -> multiple items (gas efficient)
}
```

### Metadata Pattern

```text
ERC-1155 URI template:
  Base URI: https://game.example/api/item/{id}.json

  Token ID 0 -> https://game.example/api/item/0.json
  Token ID 1 -> https://game.example/api/item/1.json

  The {id} is substituted with the hex-encoded token ID (lowercase, 64 chars):
  Token ID 0 -> .../{0000000000000000000000000000000000000000000000000000000000000000}.json
```

---

## SPL Token (Solana)

### Creating SPL Tokens

```bash
# Create a new token mint
spl-token create-token
# Output: Creating token <MINT_ADDRESS>

# Create an associated token account
spl-token create-account <MINT_ADDRESS>

# Mint tokens
spl-token mint <MINT_ADDRESS> 1000000

# Transfer tokens
spl-token transfer <MINT_ADDRESS> 100 <RECIPIENT_ADDRESS>
```

### Anchor Program (Rust)

```rust
use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount, Transfer};

#[program]
pub mod token_program {
    use super::*;

    pub fn initialize_mint(ctx: Context<InitializeMint>, decimals: u8) -> Result<()> {
        // Mint is initialized by Anchor's init constraint
        Ok(())
    }

    pub fn mint_tokens(ctx: Context<MintTokens>, amount: u64) -> Result<()> {
        let cpi_accounts = token::MintTo {
            mint: ctx.accounts.mint.to_account_info(),
            to: ctx.accounts.token_account.to_account_info(),
            authority: ctx.accounts.authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        token::mint_to(CpiContext::new(cpi_program, cpi_accounts), amount)?;
        Ok(())
    }

    pub fn transfer_tokens(ctx: Context<TransferTokens>, amount: u64) -> Result<()> {
        let cpi_accounts = Transfer {
            from: ctx.accounts.from.to_account_info(),
            to: ctx.accounts.to.to_account_info(),
            authority: ctx.accounts.authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        token::transfer(CpiContext::new(cpi_program, cpi_accounts), amount)?;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct MintTokens<'info> {
    #[account(mut)]
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub token_account: Account<'info, TokenAccount>,
    pub authority: Signer<'info>,
    pub token_program: Program<'info, Token>,
}
```

### Associated Token Accounts

```text
Solana token account model:
  Wallet Address -> Associated Token Account (ATA) -> Token Balance

  Unlike EVM (one mapping per token):
  - Each token requires a separate account
  - ATA: deterministic address derived from (wallet, mint)
  - Created on first transfer (rent-exempt: ~0.002 SOL)
  - findProgramAddress([wallet, TOKEN_PROGRAM, mint])
```

---

## Metaplex (Solana NFTs)

### Metaplex Standards

| Standard | Use Case | Key Feature |
|----------|----------|-------------|
| Token Metadata | NFT metadata | On-chain metadata with off-chain JSON |
| Candy Machine | NFT minting | Configurable minting (allowlists, phases) |
| Core (new) | Simplified NFTs | Lower cost, simpler accounts |
| Bubblegum | Compressed NFTs | Merkle tree for millions of NFTs at low cost |

### Candy Machine Configuration

```typescript
// Candy Machine v3 setup (using Umi)
import { createCandyMachine } from '@metaplex-foundation/mpl-candy-machine';

const candyMachine = await createCandyMachine(umi, {
  itemsAvailable: 10000,
  collectionMint: collectionNft.publicKey,
  guards: {
    botTax: { lamports: sol(0.01), lastInstruction: true },
    solPayment: { lamports: sol(1.5), destination: treasury },
    startDate: { date: dateTime('2026-03-01T00:00:00Z') },
    mintLimit: { id: 1, limit: 3 },  // Max 3 per wallet
    allowList: {
      merkleRoot: getMerkleRoot(allowlistedWallets),
    },
  },
});
```

### Metadata Structure (Metaplex)

```json
{
  "name": "Solana NFT #1",
  "symbol": "SNFT",
  "description": "A Solana NFT",
  "seller_fee_basis_points": 500,
  "image": "https://arweave.net/hash",
  "animation_url": "https://arweave.net/hash",
  "external_url": "https://example.com",
  "attributes": [
    { "trait_type": "Background", "value": "Blue" }
  ],
  "properties": {
    "files": [
      { "uri": "https://arweave.net/hash", "type": "image/png" }
    ],
    "creators": [
      { "address": "Creator1...", "share": 100 }
    ]
  }
}
```

### Compressed NFTs (cNFTs)

```text
Compressed NFTs (Bubblegum):
  - Store NFT data in a Merkle tree (on-chain root only)
  - Cost: ~$0.0001 per NFT (vs ~$2 for standard)
  - Ideal for: airdrops, gaming items, loyalty programs
  - Trade-off: Transfers require Merkle proof (RPC indexer needed)
  - Tree sizes: 2^14 = 16,384 to 2^30 = 1 billion NFTs
```

---

## Token Gating Patterns

### On-Chain Token Gating

```solidity
// Gate access based on token ownership
contract GatedContent {
    IERC721 public nftContract;
    mapping(uint256 => bool) public claimed;

    function claimReward(uint256 tokenId) external {
        require(nftContract.ownerOf(tokenId) == msg.sender, "Not owner");
        require(!claimed[tokenId], "Already claimed");
        claimed[tokenId] = true;
        // Distribute reward
    }
}
```

### Off-Chain Token Gating

```typescript
// Server-side token gate verification
async function verifyTokenOwnership(
  walletAddress: string,
  contractAddress: string,
  requiredBalance: number = 1
): Promise<boolean> {
  const contract = new ethers.Contract(
    contractAddress,
    ['function balanceOf(address) view returns (uint256)'],
    provider
  );
  const balance = await contract.balanceOf(walletAddress);
  return balance.gte(requiredBalance);
}

// API middleware
async function tokenGateMiddleware(req, res, next) {
  const { walletAddress, signature } = req.headers;
  // 1. Verify signature proves wallet ownership
  // 2. Check token balance
  // 3. Allow or deny access
}
```

---

## Metadata: On-Chain vs Off-Chain

### Storage Comparison

| Storage | Cost | Permanence | Speed | Best For |
|---------|------|------------|-------|----------|
| On-chain (contract storage) | Very high | Permanent | Instant | Small data (traits, scores) |
| IPFS (pinned) | Low-medium | Depends on pinning | Medium | Images, metadata JSON |
| Arweave | One-time fee | Permanent | Medium | Archival, permanent collections |
| Centralized (S3, CDN) | Low | Depends on provider | Fast | Mutable metadata, games |

### IPFS Best Practices

```text
IPFS content addressing:
  1. Upload image -> get CID: QmImageHash
  2. Create metadata JSON with image CID
  3. Upload metadata JSON -> get CID: QmMetadataHash
  4. Set tokenURI to ipfs://QmMetadataHash

  Pin with: Pinata, NFT.Storage, Filebase
  Use CID v1 for better compatibility
```

### On-Chain Metadata (Fully On-Chain NFTs)

```solidity
// Base64-encoded SVG metadata (no external dependency)
function tokenURI(uint256 tokenId) public view returns (string memory) {
    string memory svg = generateSVG(tokenId);
    string memory json = string(abi.encodePacked(
        '{"name":"Token #', toString(tokenId),
        '","description":"On-chain NFT",',
        '"image":"data:image/svg+xml;base64,',
        Base64.encode(bytes(svg)),
        '"}'
    ));
    return string(abi.encodePacked(
        "data:application/json;base64,",
        Base64.encode(bytes(json))
    ));
}
```

---

## Common Token Vulnerabilities

| Vulnerability | Token Type | Description | Prevention |
|---------------|-----------|-------------|------------|
| Reentrancy on mint | ERC-721 | `_safeMint` calls `onERC721Received` | ReentrancyGuard, CEI |
| Unlimited minting | All | Missing supply cap or auth check | `MAX_SUPPLY`, access control |
| Front-running mint | All | Bots snipe limited mints | Commit-reveal, allowlists |
| Metadata manipulation | All | Centralized metadata changed post-mint | IPFS/Arweave, metadata freeze |
| Approval phishing | ERC-20/721 | User tricked into approving malicious contract | Clear approval UX, permit2 |
| Integer overflow in price | All | `price * quantity` overflows | Solidity 0.8.x, explicit checks |
| Missing zero-address check | All | Minting to address(0) | `require(to != address(0))` |

### ERC-721 Reentrancy via safeMint

```solidity
// VULNERABLE: State not updated before safeMint callback
function mint() external payable {
    uint256 tokenId = _nextTokenId;
    _safeMint(msg.sender, tokenId);  // Calls onERC721Received -> reentrant
    _nextTokenId++;  // Too late! Attacker can re-enter before this
}

// SECURE: Update state before external call
function mint() external payable nonReentrant {
    uint256 tokenId = _nextTokenId++;  // State updated first
    _safeMint(msg.sender, tokenId);
}
```

---

## Decision Framework

### Which Token Standard to Use

```text
Token type decision:
  |
  +-- Fungible (identical, divisible)?
  |   +-- EVM -> ERC-20
  |   +-- Solana -> SPL Token
  |
  +-- Non-fungible (unique)?
  |   +-- Simple collection -> ERC-721 (EVM) or Metaplex (Solana)
  |   +-- Large-scale (millions) -> Compressed NFTs (Solana) or ERC-721A
  |   +-- Fully on-chain art -> On-chain SVG + ERC-721
  |
  +-- Semi-fungible (categories with quantities)?
  |   +-- Gaming items -> ERC-1155
  |   +-- Tickets/memberships -> ERC-1155
  |
  +-- Multi-chain?
      +-- Bridge existing -> LayerZero OFT (fungible) or ONFT (NFT)
      +-- Native multi-chain -> Deploy on each chain with bridge
```

---

## Cross-References

- [solidity-best-practices.md](solidity-best-practices.md) -- Solidity security and gas patterns
- [rust-solana-best-practices.md](rust-solana-best-practices.md) -- Solana/Anchor patterns
- [blockchain-best-practices.md](blockchain-best-practices.md) -- Universal blockchain patterns
- [defi-protocol-patterns.md](defi-protocol-patterns.md) -- DeFi composability with tokens
- [cross-chain-bridges.md](cross-chain-bridges.md) -- Cross-chain token bridging
