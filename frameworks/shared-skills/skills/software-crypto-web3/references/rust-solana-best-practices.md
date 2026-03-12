# Rust + Solana Best Practices - Anchor Framework

Production-grade patterns for secure, efficient Solana program development with Anchor.

---

## Table of Contents

1. [Anchor Framework Patterns](#anchor-framework-patterns)
2. [Account Security](#account-security)
3. [Program Derived Addresses (PDAs)](#program-derived-addresses-pdas)
4. [Cross-Program Invocations (CPIs)](#cross-program-invocations-cpis)
5. [SPL Token Integration](#spl-token-integration)
6. [Error Handling](#error-handling)
7. [Testing Strategies](#testing-strategies)
8. [Gas Optimization (Compute Units)](#gas-optimization-compute-units)
9. [Common Pitfalls](#common-pitfalls)

---

## Anchor Framework Patterns

### Basic Program Structure

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
        Ok(())
    }

    pub fn update(ctx: Context<Update>, new_data: u64) -> Result<()> {
        let account = &mut ctx.accounts.account;
        account.data = new_data;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 8 + 32
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
        has_one = authority
    )]
    pub account: Account<'info, MyAccount>,
    pub authority: Signer<'info>,
}

#[account]
pub struct MyAccount {
    pub data: u64,
    pub authority: Pubkey,
}
```

### Account Size Calculation

```rust
// CRITICAL: Always calculate exact space requirements
#[account]
pub struct GameState {
    pub authority: Pubkey,      // 32 bytes
    pub score: u64,              // 8 bytes
    pub level: u8,               // 1 byte
    pub active: bool,            // 1 byte
    pub players: Vec<Pubkey>,    // 4 + (n * 32) bytes
}

// Space calculation:
// 8 (discriminator) + 32 + 8 + 1 + 1 + 4 + (10 * 32) = 374 bytes

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 8 + 1 + 1 + 4 + (10 * 32)  // Explicit calculation
    )]
    pub game: Account<'info, GameState>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}
```

---

## Account Security

### Signer Validation

```rust
// GOOD: SECURE: Enforce signer with Signer type
#[derive(Accounts)]
pub struct Transfer<'info> {
    #[account(mut)]
    pub from: Signer<'info>,  // Must sign transaction
    #[account(mut)]
    pub to: AccountInfo<'info>,
}

// BAD: VULNERABLE: No signer enforcement
#[derive(Accounts)]
pub struct Vulnerable<'info> {
    #[account(mut)]
    pub from: AccountInfo<'info>,  // Anyone can pass any account
    #[account(mut)]
    pub to: AccountInfo<'info>,
}
```

### Owner and Authority Checks

```rust
// GOOD: SECURE: Multiple validation layers
#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(
        mut,
        has_one = authority,           // Checks account.authority == authority.key()
        constraint = vault.amount >= amount @ ErrorCode::InsufficientFunds
    )]
    pub vault: Account<'info, Vault>,
    pub authority: Signer<'info>,
}

// GOOD: SECURE: Owner validation
#[derive(Accounts)]
pub struct OwnerCheck<'info> {
    #[account(
        constraint = token_account.owner == authority.key() @ ErrorCode::InvalidOwner
    )]
    pub token_account: Account<'info, TokenAccount>,
    pub authority: Signer<'info>,
}
```

### Account Type Validation

```rust
use anchor_spl::token::{Token, TokenAccount, Mint};

#[derive(Accounts)]
pub struct TransferTokens<'info> {
    #[account(
        mut,
        constraint = from.mint == mint.key() @ ErrorCode::MintMismatch,
        constraint = from.owner == authority.key() @ ErrorCode::InvalidOwner
    )]
    pub from: Account<'info, TokenAccount>,

    #[account(
        mut,
        constraint = to.mint == mint.key() @ ErrorCode::MintMismatch
    )]
    pub to: Account<'info, TokenAccount>,

    pub mint: Account<'info, Mint>,
    pub authority: Signer<'info>,
    pub token_program: Program<'info, Token>,
}
```

---

## Program Derived Addresses (PDAs)

### Basic PDA Pattern

```rust
// GOOD: RECOMMENDED: Use seeds for deterministic addresses
#[derive(Accounts)]
#[instruction(bump: u8)]
pub struct InitializeVault<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 8,
        seeds = [b"vault", authority.key().as_ref()],
        bump
    )]
    pub vault: Account<'info, Vault>,

    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

// Deriving PDA in client:
// let [vault_pda, bump] = PublicKey::findProgramAddressSync(
//     [Buffer.from("vault"), authority.toBuffer()],
//     program.programId
// );
```

### PDA Signing (CPI with Authority)

```rust
use anchor_lang::solana_program::program::invoke_signed;

pub fn transfer_from_vault(
    ctx: Context<TransferFromVault>,
    amount: u64,
    bump: u8,
) -> Result<()> {
    let authority_seeds = &[
        b"vault",
        ctx.accounts.authority.key().as_ref(),
        &[bump],
    ];
    let signer_seeds = &[&authority_seeds[..]];

    // Transfer SOL using PDA as signer
    anchor_lang::system_program::transfer(
        CpiContext::new_with_signer(
            ctx.accounts.system_program.to_account_info(),
            anchor_lang::system_program::Transfer {
                from: ctx.accounts.vault.to_account_info(),
                to: ctx.accounts.recipient.to_account_info(),
            },
            signer_seeds,
        ),
        amount,
    )?;

    Ok(())
}

#[derive(Accounts)]
#[instruction(bump: u8)]
pub struct TransferFromVault<'info> {
    #[account(
        mut,
        seeds = [b"vault", authority.key().as_ref()],
        bump
    )]
    pub vault: Account<'info, Vault>,

    pub authority: Signer<'info>,

    #[account(mut)]
    /// CHECK: Recipient can be any account
    pub recipient: AccountInfo<'info>,

    pub system_program: Program<'info, System>,
}
```

### Multiple PDAs with Different Seeds

```rust
#[derive(Accounts)]
pub struct CreateGame<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 8 + 1,
        seeds = [b"game", game_id.to_le_bytes().as_ref()],
        bump
    )]
    pub game: Account<'info, Game>,

    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 4,
        seeds = [b"player", game.key().as_ref(), authority.key().as_ref()],
        bump
    )]
    pub player: Account<'info, Player>,

    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}
```

---

## Cross-Program Invocations (CPIs)

### SPL Token CPI

```rust
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

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
    Ok(())
}
```

### CPI with PDA Signer

```rust
pub fn burn_from_vault(
    ctx: Context<BurnFromVault>,
    amount: u64,
    bump: u8,
) -> Result<()> {
    let authority_seeds = &[
        b"vault",
        ctx.accounts.mint.key().as_ref(),
        &[bump],
    ];
    let signer_seeds = &[&authority_seeds[..]];

    token::burn(
        CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            token::Burn {
                mint: ctx.accounts.mint.to_account_info(),
                from: ctx.accounts.vault_token_account.to_account_info(),
                authority: ctx.accounts.vault_pda.to_account_info(),
            },
            signer_seeds,
        ),
        amount,
    )?;

    Ok(())
}
```

### Invoking Another Program

```rust
use anchor_lang::solana_program::program::invoke;

pub fn call_external_program(ctx: Context<CallExternal>) -> Result<()> {
    let ix = anchor_lang::solana_program::instruction::Instruction {
        program_id: ctx.accounts.external_program.key(),
        accounts: vec![
            AccountMeta::new(ctx.accounts.account.key(), false),
            AccountMeta::new_readonly(ctx.accounts.authority.key(), true),
        ],
        data: vec![1, 2, 3],  // Instruction data
    };

    invoke(
        &ix,
        &[
            ctx.accounts.account.to_account_info(),
            ctx.accounts.authority.to_account_info(),
        ],
    )?;

    Ok(())
}
```

---

## SPL Token Integration

### Creating Token Mint

```rust
use anchor_spl::token::{Mint, Token};

#[derive(Accounts)]
pub struct CreateMint<'info> {
    #[account(
        init,
        payer = payer,
        mint::decimals = 9,
        mint::authority = mint_authority,
    )]
    pub mint: Account<'info, Mint>,

    /// CHECK: This account will be the mint authority
    pub mint_authority: AccountInfo<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
    pub rent: Sysvar<'info, Rent>,
}
```

### Minting Tokens

```rust
use anchor_spl::token::{self, MintTo};

pub fn mint_tokens(ctx: Context<MintTokens>, amount: u64) -> Result<()> {
    token::mint_to(
        CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            MintTo {
                mint: ctx.accounts.mint.to_account_info(),
                to: ctx.accounts.token_account.to_account_info(),
                authority: ctx.accounts.mint_authority.to_account_info(),
            },
        ),
        amount,
    )?;
    Ok(())
}

#[derive(Accounts)]
pub struct MintTokens<'info> {
    #[account(mut)]
    pub mint: Account<'info, Mint>,

    #[account(mut)]
    pub token_account: Account<'info, TokenAccount>,

    pub mint_authority: Signer<'info>,
    pub token_program: Program<'info, Token>,
}
```

### Associated Token Accounts

```rust
use anchor_spl::associated_token::AssociatedToken;
use anchor_spl::token::{TokenAccount, Mint};

#[derive(Accounts)]
pub struct CreateAssociatedTokenAccount<'info> {
    #[account(
        init,
        payer = payer,
        associated_token::mint = mint,
        associated_token::authority = owner,
    )]
    pub token_account: Account<'info, TokenAccount>,

    pub mint: Account<'info, Mint>,

    /// CHECK: This account will own the token account
    pub owner: AccountInfo<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}
```

---

## Error Handling

### Custom Error Codes

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
}

// Usage:
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

### Require Macros

```rust
// GOOD: Use require! for validation
pub fn update_game(ctx: Context<UpdateGame>, new_score: u64) -> Result<()> {
    let game = &mut ctx.accounts.game;

    // Simple boolean check
    require!(game.active, ErrorCode::GameNotActive);

    // Comparison check
    require!(
        new_score > game.score,
        ErrorCode::ScoreMustIncrease
    );

    // Key equality check
    require_keys_eq!(
        game.authority,
        ctx.accounts.authority.key(),
        ErrorCode::Unauthorized
    );

    game.score = new_score;
    Ok(())
}
```

---

## Testing Strategies

### Basic Test Structure

```rust
use anchor_lang::prelude::*;
use anchor_spl::token::{TokenAccount, Mint};

#[cfg(test)]
mod tests {
    use super::*;
    use anchor_lang::InstructionData;
    use solana_program_test::*;
    use solana_sdk::{
        signature::Keypair,
        signer::Signer,
        transaction::Transaction,
    };

    #[tokio::test]
    async fn test_initialize() {
        let program_id = Pubkey::new_unique();
        let mut program_test = ProgramTest::new(
            "my_program",
            program_id,
            processor!(entry),
        );

        let (mut banks_client, payer, recent_blockhash) = program_test.start().await;

        // Create instruction
        let account = Keypair::new();
        let ix = initialize(
            &program_id,
            &payer.pubkey(),
            &account.pubkey(),
            1000,
        );

        // Submit transaction
        let mut transaction = Transaction::new_with_payer(
            &[ix],
            Some(&payer.pubkey()),
        );
        transaction.sign(&[&payer, &account], recent_blockhash);

        banks_client.process_transaction(transaction).await.unwrap();

        // Verify account data
        let account_data = banks_client
            .get_account(account.pubkey())
            .await
            .unwrap()
            .unwrap();

        assert_eq!(account_data.data.len(), 8 + 8 + 32);
    }
}
```

### Integration Tests with Anchor

```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { MyProgram } from "../target/types/my_program";
import { expect } from "chai";

describe("my_program", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.MyProgram as Program<MyProgram>;

  it("Initializes account", async () => {
    const account = anchor.web3.Keypair.generate();

    await program.methods
      .initialize(new anchor.BN(1000))
      .accounts({
        account: account.publicKey,
        authority: provider.wallet.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([account])
      .rpc();

    const accountData = await program.account.myAccount.fetch(
      account.publicKey
    );

    expect(accountData.data.toNumber()).to.equal(1000);
    expect(accountData.authority.toString()).to.equal(
      provider.wallet.publicKey.toString()
    );
  });

  it("Updates account data", async () => {
    const account = anchor.web3.Keypair.generate();

    // Initialize
    await program.methods
      .initialize(new anchor.BN(1000))
      .accounts({
        account: account.publicKey,
        authority: provider.wallet.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([account])
      .rpc();

    // Update
    await program.methods
      .update(new anchor.BN(2000))
      .accounts({
        account: account.publicKey,
        authority: provider.wallet.publicKey,
      })
      .rpc();

    const accountData = await program.account.myAccount.fetch(
      account.publicKey
    );

    expect(accountData.data.toNumber()).to.equal(2000);
  });

  it("Fails when unauthorized", async () => {
    const account = anchor.web3.Keypair.generate();
    const unauthorized = anchor.web3.Keypair.generate();

    await program.methods
      .initialize(new anchor.BN(1000))
      .accounts({
        account: account.publicKey,
        authority: provider.wallet.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([account])
      .rpc();

    try {
      await program.methods
        .update(new anchor.BN(2000))
        .accounts({
          account: account.publicKey,
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

## Gas Optimization (Compute Units)

### Compute Budget

```rust
// Check compute unit usage
use anchor_lang::solana_program::log::sol_log_compute_units;

pub fn expensive_operation(ctx: Context<ExpensiveOp>) -> Result<()> {
    sol_log_compute_units();  // Log compute units used

    // Expensive operation
    for i in 0..1000 {
        // Process
    }

    sol_log_compute_units();  // Log again to measure delta
    Ok(())
}
```

### Account Size Optimization

```rust
// BAD: WASTEFUL: Fixed-size arrays
#[account]
pub struct Inefficient {
    pub items: [u64; 1000],  // Always allocates 8000 bytes
}

// GOOD: OPTIMIZED: Use Vec with max_len
#[account]
pub struct Efficient {
    pub items: Vec<u64>,  // 4 + (n * 8) bytes, grows as needed
}

// When initializing:
#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + 4 + (100 * 8)  // Discriminator + Vec length + max 100 items
    )]
    pub account: Account<'info, Efficient>,
    #[account(mut)]
    pub payer: Signer<'info>,
    pub system_program: Program<'info, System>,
}
```

### Zero-Copy Deserialization

```rust
use anchor_lang::prelude::*;

// For very large accounts, use zero_copy
#[account(zero_copy)]
pub struct LargeAccount {
    pub data: [u8; 10000],
}

#[derive(Accounts)]
pub struct ProcessLarge<'info> {
    #[account(mut)]
    pub account: AccountLoader<'info, LargeAccount>,
}

pub fn process_large(ctx: Context<ProcessLarge>) -> Result<()> {
    let mut account = ctx.accounts.account.load_mut()?;
    account.data[0] = 42;
    Ok(())
}
```

---

## Common Pitfalls

### Missing Account Validation

```rust
// BAD: VULNERABLE: No mint validation
#[derive(Accounts)]
pub struct TransferBad<'info> {
    #[account(mut)]
    pub from: Account<'info, TokenAccount>,
    #[account(mut)]
    pub to: Account<'info, TokenAccount>,
    // Attacker can pass accounts with different mints!
}

// GOOD: SECURE: Validate mints match
#[derive(Accounts)]
pub struct TransferGood<'info> {
    #[account(
        mut,
        constraint = from.mint == to.mint @ ErrorCode::MintMismatch
    )]
    pub from: Account<'info, TokenAccount>,
    #[account(mut)]
    pub to: Account<'info, TokenAccount>,
}
```

### Reinitialization Attacks

```rust
// BAD: VULNERABLE: Can be called multiple times
pub fn initialize_bad(ctx: Context<InitBad>) -> Result<()> {
    let account = &mut ctx.accounts.account;
    account.authority = ctx.accounts.authority.key();
    account.balance = 0;  // Attacker can reset balance to 0!
    Ok(())
}

// GOOD: SECURE: Use init constraint
#[derive(Accounts)]
pub struct InitGood<'info> {
    #[account(
        init,  // Fails if account already initialized
        payer = authority,
        space = 8 + 32 + 8
    )]
    pub account: Account<'info, MyAccount>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}
```

### Integer Overflow

```rust
// BAD: VULNERABLE: Overflow possible
pub fn add_unchecked(ctx: Context<Add>, amount: u64) -> Result<()> {
    let account = &mut ctx.accounts.account;
    account.balance = account.balance + amount;  // Can overflow
    Ok(())
}

// GOOD: SECURE: Use checked arithmetic
pub fn add_checked(ctx: Context<Add>, amount: u64) -> Result<()> {
    let account = &mut ctx.accounts.account;
    account.balance = account
        .balance
        .checked_add(amount)
        .ok_or(ErrorCode::Overflow)?;
    Ok(())
}
```

### Signer Authorization

```rust
// BAD: VULNERABLE: No signer check
pub fn withdraw_bad(ctx: Context<WithdrawBad>, amount: u64) -> Result<()> {
    // Anyone can call this!
    let vault = &mut ctx.accounts.vault;
    vault.balance -= amount;
    Ok(())
}

// GOOD: SECURE: Require signer
#[derive(Accounts)]
pub struct WithdrawGood<'info> {
    #[account(
        mut,
        has_one = authority
    )]
    pub vault: Account<'info, Vault>,
    pub authority: Signer<'info>,  // Must sign transaction
}
```

---

## Production Checklist

Before deploying to mainnet:

**Security:**
- [ ] All accounts validated (owner, signer, mint, authority)
- [ ] Use `init` constraint to prevent reinitialization
- [ ] Checked arithmetic for all math operations
- [ ] Custom errors for all failure cases
- [ ] Access control on privileged instructions
- [ ] PDA derivation uses unique, collision-resistant seeds
- [ ] CPI targets validated (program IDs, account ownership)

**Testing:**
- [ ] 100% instruction coverage
- [ ] Negative test cases (unauthorized access, invalid inputs)
- [ ] Integration tests with TypeScript client
- [ ] Fuzz testing for critical functions
- [ ] Compute unit benchmarks documented

**Optimization:**
- [ ] Account sizes minimized (use Vec instead of arrays)
- [ ] Zero-copy for large accounts
- [ ] Unnecessary accounts removed from contexts
- [ ] Compute budget checked for expensive operations

**Deployment:**
- [ ] Upgrade authority secured with multi-sig
- [ ] Program verified on Solscan/Solana Explorer
- [ ] Emergency pause mechanism implemented
- [ ] Monitoring and alerting configured

---

## Resources

- [Anchor Documentation](https://www.anchor-lang.com/)
- [Solana Cookbook](https://solanacookbook.com/)
- [Solana Security Best Practices](https://github.com/coral-xyz/sealevel-attacks)
- [SPL Token Program](https://spl.solana.com/token)
- [Metaplex Standards](https://docs.metaplex.com/)
