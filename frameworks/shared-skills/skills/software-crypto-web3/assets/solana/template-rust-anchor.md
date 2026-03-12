# Solana Program Development — Anchor Framework Template

Production-grade Solana program development with Anchor, Rust, and TypeScript testing.

---

## Project Overview

This template provides a complete development environment for building, testing, and deploying Solana programs using:

- **Anchor** - Solana development framework (v0.29+)
- **Rust** - Systems programming language for on-chain programs
- **TypeScript** - Client-side testing and deployment
- **Solana CLI** - Command-line tools for Solana
- **SPL Token** - Token program integration

**Use cases:** DeFi protocols, NFT projects, gaming, DAOs, token contracts, staking systems

---

## Project Structure

```
anchor-project/
├── programs/
│   └── my_program/
│       ├── src/
│       │   ├── lib.rs
│       │   ├── state.rs
│       │   ├── instructions/
│       │   │   ├── mod.rs
│       │   │   ├── initialize.rs
│       │   │   └── update.rs
│       │   └── errors.rs
│       └── Cargo.toml
├── tests/
│   └── my_program.ts
├── app/
│   └── client.ts
├── target/
├── migrations/
│   └── deploy.ts
├── Anchor.toml
└── package.json
```

---

## Environment Setup

### 1. Install Prerequisites

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
rustup update

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Verify Solana installation
solana --version

# Install Anchor
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest

# Verify Anchor installation
anchor --version

# Install Node.js dependencies
npm install -g yarn
```

### 2. Initialize Project

```bash
# Create new Anchor project
anchor init my_project
cd my_project

# Install dependencies
yarn install

# Build project
anchor build

# Test project
anchor test
```

### 3. Configure Cluster

```bash
# Set cluster to devnet
solana config set --url devnet

# Create wallet (or use existing)
solana-keygen new --outfile ~/.config/solana/id.json

# Check balance
solana balance

# Airdrop SOL (devnet only)
solana airdrop 2
```

**Anchor.toml:**
```toml
[features]
seeds = false
skip-lint = false

[programs.localnet]
my_program = "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"

[programs.devnet]
my_program = "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"

[programs.mainnet]
my_program = "YOUR_MAINNET_PROGRAM_ID"

[registry]
url = "https://api.apr.dev"

[provider]
cluster = "Devnet"
wallet = "~/.config/solana/id.json"

[scripts]
test = "yarn run ts-mocha -p ./tsconfig.json -t 1000000 tests/**/*.ts"
```

---

## Basic Program Structure

### Main Program File

**programs/my_program/src/lib.rs:**
```rust
use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod my_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, data: u64) -> Result<()> {
        let account = &mut ctx.accounts.account;
        account.data = data;
        account.authority = ctx.accounts.authority.key();
        account.bump = ctx.bumps.account;
        msg!("Initialized with data: {}", data);
        Ok(())
    }

    pub fn update(ctx: Context<Update>, new_data: u64) -> Result<()> {
        let account = &mut ctx.accounts.account;
        account.data = new_data;
        msg!("Updated data to: {}", new_data);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 8 + 32 + 1,
        seeds = [b"account", authority.key().as_ref()],
        bump
    )]
    pub account: Account<'info, MyAccount>,

    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Update<'info> {
    #[account(
        mut,
        seeds = [b"account", authority.key().as_ref()],
        bump = account.bump,
        has_one = authority
    )]
    pub account: Account<'info, MyAccount>,
    pub authority: Signer<'info>,
}

#[account]
pub struct MyAccount {
    pub data: u64,
    pub authority: Pubkey,
    pub bump: u8,
}
```

---

## Token Program Integration

### SPL Token Mint and Transfer

**programs/my_program/src/lib.rs:**
```rust
use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Mint, MintTo, Transfer};

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod token_program {
    use super::*;

    pub fn mint_tokens(ctx: Context<MintTokens>, amount: u64) -> Result<()> {
        token::mint_to(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                MintTo {
                    mint: ctx.accounts.mint.to_account_info(),
                    to: ctx.accounts.token_account.to_account_info(),
                    authority: ctx.accounts.authority.to_account_info(),
                },
            ),
            amount,
        )?;

        msg!("Minted {} tokens", amount);
        Ok(())
    }

    pub fn transfer_tokens(ctx: Context<TransferTokens>, amount: u64) -> Result<()> {
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.from.to_account_info(),
                    to: ctx.accounts.to.to_account_info(),
                    authority: ctx.accounts.authority.to_account_info(),
                },
            ),
            amount,
        )?;

        msg!("Transferred {} tokens", amount);
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

#[derive(Accounts)]
pub struct TransferTokens<'info> {
    #[account(
        mut,
        constraint = from.mint == to.mint @ ErrorCode::MintMismatch
    )]
    pub from: Account<'info, TokenAccount>,

    #[account(mut)]
    pub to: Account<'info, TokenAccount>,

    pub authority: Signer<'info>,
    pub token_program: Program<'info, Token>,
}
```

---

## NFT (Metaplex) Integration

```rust
use anchor_lang::prelude::*;
use anchor_spl::{
    associated_token::AssociatedToken,
    token::{Mint, Token, TokenAccount},
};
use mpl_token_metadata::{
    instructions::{CreateMetadataAccountV3Cpi, CreateMetadataAccountV3CpiAccounts, CreateMetadataAccountV3InstructionArgs},
    types::DataV2,
};

#[program]
pub mod nft_program {
    use super::*;

    pub fn create_nft(
        ctx: Context<CreateNFT>,
        name: String,
        symbol: String,
        uri: String,
    ) -> Result<()> {
        // Create metadata account
        let data_v2 = DataV2 {
            name,
            symbol,
            uri,
            seller_fee_basis_points: 500, // 5%
            creators: Some(vec![mpl_token_metadata::types::Creator {
                address: ctx.accounts.authority.key(),
                verified: true,
                share: 100,
            }]),
            collection: None,
            uses: None,
        };

        let create_metadata_ix = CreateMetadataAccountV3Cpi::new(
            &ctx.accounts.metadata_program,
            CreateMetadataAccountV3CpiAccounts {
                metadata: &ctx.accounts.metadata,
                mint: &ctx.accounts.mint,
                mint_authority: &ctx.accounts.authority,
                payer: &ctx.accounts.authority,
                update_authority: (&ctx.accounts.authority, true),
                system_program: &ctx.accounts.system_program,
                rent: None,
            },
            CreateMetadataAccountV3InstructionArgs {
                data: data_v2,
                is_mutable: true,
                collection_details: None,
            },
        );

        create_metadata_ix.invoke()?;

        msg!("NFT created successfully");
        Ok(())
    }
}

#[derive(Accounts)]
pub struct CreateNFT<'info> {
    #[account(
        init,
        payer = authority,
        mint::decimals = 0,
        mint::authority = authority,
    )]
    pub mint: Account<'info, Mint>,

    /// CHECK: Validated by Metaplex program
    #[account(mut)]
    pub metadata: UncheckedAccount<'info>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,

    /// CHECK: Metaplex metadata program
    pub metadata_program: UncheckedAccount<'info>,
    pub rent: Sysvar<'info, Rent>,
}
```

---

## Error Handling

**programs/my_program/src/errors.rs:**
```rust
use anchor_lang::prelude::*;

#[error_code]
pub enum ErrorCode {
    #[msg("The provided amount exceeds the maximum allowed")]
    AmountTooLarge,

    #[msg("Insufficient funds in the vault")]
    InsufficientFunds,

    #[msg("The game has already started")]
    GameAlreadyStarted,

    #[msg("Only the authority can perform this action")]
    Unauthorized,

    #[msg("Invalid mint provided")]
    InvalidMint,

    #[msg("Mint mismatch between accounts")]
    MintMismatch,
}
```

**Usage:**
```rust
use crate::errors::ErrorCode;

pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {
    require!(
        ctx.accounts.vault.balance >= amount,
        ErrorCode::InsufficientFunds
    );

    require!(
        amount <= MAX_WITHDRAWAL,
        ErrorCode::AmountTooLarge
    );

    // Process withdrawal
    Ok(())
}
```

---

## TypeScript Testing

**tests/my_program.ts:**
```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MyProgram } from "../target/types/my_program";
import { expect } from "chai";

describe("my_program", () => {
  // Configure the client to use the local cluster
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.MyProgram as Program<MyProgram>;

  it("Initializes account", async () => {
    const [accountPDA] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("account"), provider.wallet.publicKey.toBuffer()],
      program.programId
    );

    const tx = await program.methods
      .initialize(new anchor.BN(1000))
      .accounts({
        account: accountPDA,
        authority: provider.wallet.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .rpc();

    console.log("Transaction signature:", tx);

    // Fetch account data
    const accountData = await program.account.myAccount.fetch(accountPDA);

    expect(accountData.data.toNumber()).to.equal(1000);
    expect(accountData.authority.toString()).to.equal(
      provider.wallet.publicKey.toString()
    );
  });

  it("Updates account data", async () => {
    const [accountPDA] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("account"), provider.wallet.publicKey.toBuffer()],
      program.programId
    );

    await program.methods
      .update(new anchor.BN(2000))
      .accounts({
        account: accountPDA,
        authority: provider.wallet.publicKey,
      })
      .rpc();

    const accountData = await program.account.myAccount.fetch(accountPDA);
    expect(accountData.data.toNumber()).to.equal(2000);
  });

  it("Fails when unauthorized", async () => {
    const [accountPDA] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("account"), provider.wallet.publicKey.toBuffer()],
      program.programId
    );

    const unauthorized = anchor.web3.Keypair.generate();

    // Airdrop to unauthorized user
    await provider.connection.requestAirdrop(
      unauthorized.publicKey,
      2 * anchor.web3.LAMPORTS_PER_SOL
    );

    try {
      await program.methods
        .update(new anchor.BN(3000))
        .accounts({
          account: accountPDA,
          authority: unauthorized.publicKey,
        })
        .signers([unauthorized])
        .rpc();

      expect.fail("Expected error not thrown");
    } catch (err) {
      expect(err.error.errorCode.code).to.equal("ConstraintHasOne");
    }
  });
});
```

---

## Client-Side Integration

**app/client.ts:**
```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program, AnchorProvider, web3 } from "@coral-xyz/anchor";
import { MyProgram } from "../target/types/my_program";
import fs from "fs";

async function main() {
  // Configure the client
  const connection = new web3.Connection("https://api.devnet.solana.com", "confirmed");

  // Load wallet
  const keypair = web3.Keypair.fromSecretKey(
    Uint8Array.from(JSON.parse(fs.readFileSync("/path/to/wallet.json", "utf-8")))
  );

  const wallet = new anchor.Wallet(keypair);
  const provider = new AnchorProvider(connection, wallet, {
    commitment: "confirmed",
  });

  // Load program
  const programId = new web3.PublicKey("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");
  const idl = JSON.parse(fs.readFileSync("./target/idl/my_program.json", "utf-8"));
  const program = new Program(idl, programId, provider) as Program<MyProgram>;

  // Derive PDA
  const [accountPDA, bump] = web3.PublicKey.findProgramAddressSync(
    [Buffer.from("account"), provider.wallet.publicKey.toBuffer()],
    program.programId
  );

  console.log("Account PDA:", accountPDA.toString());
  console.log("Bump:", bump);

  // Initialize account
  const tx = await program.methods
    .initialize(new anchor.BN(1000))
    .accounts({
      account: accountPDA,
      authority: provider.wallet.publicKey,
      systemProgram: web3.SystemProgram.programId,
    })
    .rpc();

  console.log("Transaction signature:", tx);

  // Fetch account data
  const accountData = await program.account.myAccount.fetch(accountPDA);
  console.log("Account data:", accountData);
}

main().catch(console.error);
```

---

## Deployment

### Local Deployment (Validator)

```bash
# Start local validator
solana-test-validator

# In another terminal, deploy
anchor build
anchor deploy

# Test against local validator
anchor test --skip-local-validator
```

### Devnet Deployment

```bash
# Set cluster to devnet
solana config set --url devnet

# Build program
anchor build

# Get program ID
solana address -k target/deploy/my_program-keypair.json

# Update Anchor.toml and lib.rs with program ID

# Rebuild with correct ID
anchor build

# Deploy to devnet
anchor deploy

# Verify deployment
solana program show <PROGRAM_ID>
```

### Mainnet Deployment

```bash
# Set cluster to mainnet
solana config set --url mainnet-beta

# Ensure sufficient SOL for deployment
solana balance

# Deploy to mainnet
anchor deploy --provider.cluster mainnet

# IMPORTANT: Verify program after deployment
anchor verify <PROGRAM_ID>
```

---

## Program Upgrade

```bash
# Build new version
anchor build

# Upgrade program
solana program deploy --program-id <PROGRAM_KEYPAIR> target/deploy/my_program.so

# Close old buffer (reclaim rent)
solana program close <BUFFER_ADDRESS>
```

---

## Useful Commands

### Anchor Commands

```bash
# Build program
anchor build

# Test program
anchor test

# Test with logs
anchor test --skip-local-validator -- --nocapture

# Deploy program
anchor deploy

# Verify program
anchor verify <PROGRAM_ID>

# Clean build artifacts
anchor clean

# Create new program
anchor new <PROGRAM_NAME>
```

### Solana CLI Commands

```bash
# Check balance
solana balance

# Airdrop SOL (devnet/testnet only)
solana airdrop 2

# Get program info
solana program show <PROGRAM_ID>

# Get account info
solana account <ADDRESS>

# Transfer SOL
solana transfer <RECIPIENT> <AMOUNT>

# Create keypair
solana-keygen new --outfile wallet.json

# Get public key from keypair
solana-keygen pubkey wallet.json
```

### SPL Token Commands

```bash
# Create token mint
spl-token create-token

# Create token account
spl-token create-account <MINT_ADDRESS>

# Mint tokens
spl-token mint <MINT_ADDRESS> <AMOUNT>

# Transfer tokens
spl-token transfer <MINT_ADDRESS> <AMOUNT> <RECIPIENT>

# Get token balance
spl-token balance <MINT_ADDRESS>
```

---

## Production Checklist

Before deploying to mainnet:

**Security:**
- [ ] All accounts validated (owner, signer, program ID)
- [ ] Checked arithmetic for all operations
- [ ] Custom errors for all failure cases
- [ ] Access control on privileged instructions
- [ ] PDA seeds unique and collision-resistant
- [ ] Professional security audit completed
- [ ] Bug bounty program launched

**Testing:**
- [ ] 100% instruction coverage
- [ ] Negative test cases (unauthorized, invalid inputs)
- [ ] Integration tests with TypeScript client
- [ ] Fuzz testing for critical functions
- [ ] Compute unit benchmarks documented

**Deployment:**
- [ ] Program verified on Solana Explorer
- [ ] Upgrade authority secured with multi-sig
- [ ] Emergency pause mechanism implemented
- [ ] Monitoring and alerting configured
- [ ] Deployment procedure tested on devnet

**Documentation:**
- [ ] README with usage instructions
- [ ] API documentation (rustdoc)
- [ ] Architecture diagram
- [ ] Known limitations documented

---

## Resources

- [Anchor Documentation](https://www.anchor-lang.com/)
- [Solana Cookbook](https://solanacookbook.com/)
- [Solana Documentation](https://docs.solana.com/)
- [SPL Token Program](https://spl.solana.com/token)
- [Metaplex Documentation](https://docs.metaplex.com/)
- [Anchor Examples](https://github.com/coral-xyz/anchor/tree/master/tests)
- [Solana Security Best Practices](https://github.com/coral-xyz/sealevel-attacks)
