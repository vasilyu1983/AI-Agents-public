# TON Best Practices - FunC, Tact, and TVM Development

Production-grade patterns for secure, efficient smart contract development on The Open Network (TON).

---

## Table of Contents

1. [TON Architecture](#ton-architecture)
2. [TVM-Specific Patterns](#tvm-specific-patterns)
3. [Message Handling](#message-handling)
4. [Gas Optimization](#gas-optimization)
5. [Jetton (Token) Standards](#jetton-token-standards)
6. [NFT Standards](#nft-standards)
7. [TON Connect Integration](#ton-connect-integration)
8. [Security Patterns](#security-patterns)
9. [Testing Strategies](#testing-strategies)
10. [Common Pitfalls](#common-pitfalls)

---

## TON Architecture

### Actor Model

TON uses an **asynchronous actor model** where:
- Each contract is an independent actor
- Communication happens via messages (no direct calls)
- Messages are processed sequentially per contract
- No reentrancy attacks (unlike Ethereum)

**Key Differences from Ethereum:**

| Feature | Ethereum | TON |
|---------|----------|-----|
| Execution | Synchronous | Asynchronous |
| Contract Calls | Direct (CALL opcode) | Message-based |
| Reentrancy | Possible | Not possible |
| State Changes | Within transaction | Across messages |
| Gas Model | EVM gas | TVM gas (compute + storage) |

### Sharding Architecture

TON uses **infinite sharding** (shardchains):
- Workchain 0: Masterchain (for validators)
- Workchain -1: Basechain (for user contracts)
- Each account can be in different shard
- Cross-shard messages have latency

**Best Practice:** Design contracts assuming message delivery is not instant.

---

## TVM-Specific Patterns

### Stack-Based Operations

TVM is a stack-based virtual machine (like Bitcoin Script, but more powerful).

**FunC Stack Operations:**
```func
;; Stack manipulation
int a = 10;
int b = 20;
int sum = a + b;  // Pushes a, b, adds, stores in sum

;; Tuple operations (multiple return values)
(int, int) swap(int a, int b) {
    return (b, a);
}

;; Inline functions (no stack overhead)
int add(int a, int b) inline {
    return a + b;
}
```

**Best Practice:** Use `inline` for small helper functions to avoid function call overhead.

### Cell Operations

Everything in TON is stored in **cells** (max 1023 bits + 4 references).

```func
;; Build cell
cell data = begin_cell()
    .store_uint(123, 32)
    .store_slice(address)
    .store_ref(another_cell)
    .end_cell();

;; Parse cell
slice ds = data.begin_parse();
int value = ds~load_uint(32);
slice addr = ds~load_msg_addr();
cell ref = ds~load_ref();

;; [OK] GOOD: Check slice is fully consumed
ds.end_parse();  // Throws if extra data remains
```

**Best Practice:** Always call `end_parse()` after loading to ensure no extra data.

### Slice Safety

```func
;; VULNERABLE: No bounds checking
int load_uint_unsafe(slice s) {
    return s~load_uint(64);  // May fail if slice too short
}

;; SECURE: Check slice size first
int load_uint_safe(slice s) {
    throw_unless(100, s.slice_bits() >= 64);
    return s~load_uint(64);
}
```

---

## Message Handling

### Message Structure

Every message has:
- **Header:** flags, source, destination, value, bounce, bounced
- **Body:** operation code (op) + query_id + data

**Standard Message Format:**
```func
int op = in_msg_body~load_uint(32);      ;; Operation code
int query_id = in_msg_body~load_uint(64); ;; Query ID (for tracking)
;; ... remaining data
```

### Message Modes

```func
;; Common send modes
const int SEND_MODE_REGULAR = 0;              ;; Pay fees separately
const int SEND_MODE_PAY_FEES_SEPARATELY = 1;  ;; Pay transfer fees separately
const int SEND_MODE_IGNORE_ERRORS = 2;        ;; Ignore send errors
const int SEND_MODE_CARRY_REMAINING_BALANCE = 64;  ;; Send all remaining balance
const int SEND_MODE_CARRY_ALL_BALANCE = 128;  ;; Send all balance and destroy

;; [OK] GOOD: Pay fees separately, ignore errors
send_raw_message(msg, 1 + 2);

;; [OK] GOOD: Return all remaining value to sender
send_raw_message(msg, 64);
```

**Best Practice:** Use mode `64` (carry remaining balance) for responses to avoid dust accumulation.

### Bounce Handling

Bounced messages occur when:
- Recipient doesn't exist
- Recipient contract throws error
- Insufficient gas for recipient

```func
() recv_internal(int balance, int msg_value, cell in_msg, slice in_msg_body) {
    slice cs = in_msg.begin_parse();
    int flags = cs~load_uint(4);

    ;; Check if bounced
    if (flags & 1) {
        ;; Handle bounced message
        ;; DO NOT throw here (creates bounce loop)
        return ();
    }

    ;; Normal message handling
    int op = in_msg_body~load_uint(32);
    ;; ...
}
```

**Best Practice:** Always check bounce flag first and handle gracefully (no throws).

### Get Methods vs Internal Messages

```func
;; BAD: Get method that modifies state
int get_and_increment() method_id {
    int counter = get_data().begin_parse().preload_uint(64);
    counter += 1;  // WRONG: Get methods can't modify state
    return counter;
}

;; [OK] GOOD: Get method is read-only
int get_counter() method_id {
    return get_data().begin_parse().preload_uint(64);
}

;; [OK] GOOD: State modification via internal message
() recv_internal(...) {
    if (op == op::increment()) {
        int counter = get_data().begin_parse().preload_uint(64);
        counter += 1;
        set_data(begin_cell().store_uint(counter, 64).end_cell());
    }
}
```

---

## Gas Optimization

### Gas Components

TON gas has two parts:
1. **Compute gas** - CPU operations
2. **Storage fees** - Data storage over time

**Storage Fees Formula:**
```
storage_fee = cells * cell_price + bits * bit_price
```

### Minimize Cell Count

```func
;; [FAIL] EXPENSIVE: Multiple cells
cell data = begin_cell()
    .store_ref(
        begin_cell()
            .store_uint(a, 32)
            .end_cell()
    )
    .store_ref(
        begin_cell()
            .store_uint(b, 32)
            .end_cell()
    )
    .end_cell();

;; [OK] OPTIMIZED: Single cell (if fits)
cell data = begin_cell()
    .store_uint(a, 32)
    .store_uint(b, 32)
    .end_cell();
```

**Best Practice:** Pack data into as few cells as possible (max 1023 bits per cell).

### Avoid Unnecessary Loads

```func
;; [FAIL] EXPENSIVE: Load data multiple times
() bad_example() {
    slice ds = get_data().begin_parse();
    int counter = ds~load_uint(64);
    ;; ... some logic ...
    ds = get_data().begin_parse();  // LOAD AGAIN
    int owner = ds~load_msg_addr();
}

;; [OK] OPTIMIZED: Load once
() good_example() {
    slice ds = get_data().begin_parse();
    int counter = ds~load_uint(64);
    slice owner = ds~load_msg_addr();
    ;; Use both values
}
```

### Use Inline Functions

```func
;; [FAIL] EXPENSIVE: Regular function call
int add(int a, int b) {
    return a + b;
}

;; [OK] OPTIMIZED: Inline (no call overhead)
int add(int a, int b) inline {
    return a + b;
}

;; [OK] OPTIMIZED: Inline_ref (balance between code size and speed)
int complex_calculation(int a, int b) inline_ref {
    ;; Complex logic here
    return result;
}
```

**When to use:**
- `inline` - Small functions (<10 ops)
- `inline_ref` - Medium functions (10-50 ops)
- Regular - Large functions or rarely called

---

## Jetton (Token) Standards

### TEP-74: Jetton Standard

**Jetton Minter (Master Contract):**
```func
;; Required get methods
(int, int, slice, cell, cell) get_jetton_data() method_id {
    return (
        total_supply,      ;; Total supply
        -1,                ;; Mintable flag (-1 = true, 0 = false)
        admin_address,     ;; Admin address
        content,           ;; Metadata cell
        jetton_wallet_code ;; Wallet code
    );
}

slice get_wallet_address(slice owner_address) method_id {
    return calculate_user_jetton_wallet_address(
        owner_address,
        my_address(),
        jetton_wallet_code
    );
}
```

**Jetton Wallet (User Wallet):**
```func
;; Required get methods
(int, slice, slice, cell) get_wallet_data() method_id {
    return (
        balance,           ;; Jetton balance
        owner,             ;; Owner address
        jetton_master,     ;; Minter address
        jetton_wallet_code ;; Wallet code
    );
}
```

### Off-Chain Metadata

**Metadata Format (TEP-64):**
```json
{
  "name": "My Token",
  "description": "Description of token",
  "symbol": "MTK",
  "decimals": "9",
  "image": "https://example.com/logo.png",
  "image_data": "<base64_encoded_image>"
}
```

**On-Chain Reference:**
```func
;; Store IPFS link
cell content = begin_cell()
    .store_uint(0x01, 8)  ;; Off-chain content tag
    .store_slice("https://ipfs.io/ipfs/Qm..."^^)
    .end_cell();
```

---

## NFT Standards

### TEP-62: NFT Standard

**NFT Collection:**
```func
;; Required get methods
(int, cell, slice) get_collection_data() method_id {
    return (
        next_item_index,   ;; Next NFT index
        collection_content,;; Collection metadata
        owner_address      ;; Owner
    );
}

slice get_nft_address_by_index(int index) method_id {
    return calculate_nft_item_address(index);
}
```

**NFT Item:**
```func
;; Required get methods
(int, int, slice, slice, cell) get_nft_data() method_id {
    return (
        init?,             ;; -1 if initialized, 0 otherwise
        index,             ;; NFT index
        collection_address,;; Collection address
        owner_address,     ;; Current owner
        individual_content ;; NFT-specific metadata
    );
}
```

### SBT (Soulbound Tokens)

**TEP-85: SBT Standard (Non-transferable NFTs):**
```func
;; Transfer blocked
() recv_internal(...) {
    if (op == op::transfer()) {
        throw(413);  ;; SBTs cannot be transferred
    }
    ;; ... other ops
}

;; Revoke method (only authority)
() recv_internal(...) {
    if (op == op::revoke()) {
        throw_unless(401, equal_slices(sender, authority));
        ;; Destroy SBT
        set_data(begin_cell().end_cell());
        return ();
    }
}
```

---

## TON Connect Integration

### DApp Authentication Flow

1. **Generate QR/Deep Link:**
```typescript
import TonConnect from '@tonconnect/sdk';

const connector = new TonConnect({
    manifestUrl: 'https://myapp.com/tonconnect-manifest.json'
});

const walletConnectionSource = {
    universalLink: 'https://app.tonkeeper.com/ton-connect',
    bridgeUrl: 'https://bridge.tonapi.io/bridge'
};

const link = connector.connect(walletConnectionSource);
console.log('Connection link:', link);
```

2. **Handle Connection:**
```typescript
connector.onStatusChange(wallet => {
    if (wallet) {
        console.log('Connected wallet:', wallet.account.address);
        console.log('Public key:', wallet.account.publicKey);
    }
});
```

3. **Send Transaction:**
```typescript
const transaction = {
    validUntil: Math.floor(Date.now() / 1000) + 60, // 60 sec
    messages: [
        {
            address: "EQ...",
            amount: "1000000000", // 1 TON in nanotons
            payload: "te6cckEBAQEA..." // base64 encoded cell
        }
    ]
};

const result = await connector.sendTransaction(transaction);
```

### Manifest File

**tonconnect-manifest.json:**
```json
{
  "url": "https://myapp.com",
  "name": "My DApp",
  "iconUrl": "https://myapp.com/icon.png",
  "termsOfUseUrl": "https://myapp.com/terms",
  "privacyPolicyUrl": "https://myapp.com/privacy"
}
```

---

## Security Patterns

### Access Control

```func
;; SECURE: Check sender is owner
() recv_internal(...) {
    slice sender_address = cs~load_msg_addr();

    if (op == op::admin_action()) {
        (slice owner) = load_data();
        throw_unless(401, equal_slices(sender_address, owner));
        ;; Perform admin action
    }
}
```

### Integer Overflow Protection

FunC has automatic overflow checks (throws on overflow):

```func
;; [OK] SAFE: Automatically checks overflow
int result = a + b;  ;; Throws if overflows

;; For explicit control:
int safe_add(int a, int b) {
    int result = a + b;
    ;; Overflow check is automatic
    return result;
}
```

### Message Value Validation

```func
;; SECURE: Ensure sufficient value sent
const int MIN_TON_FOR_STORAGE = 50000000;  ;; 0.05 TON

() recv_internal(int msg_value, ...) {
    throw_unless(
        402,
        msg_value >= MIN_TON_FOR_STORAGE
    );
    ;; Process message
}
```

### Prevent Duplicate Replay

```func
;; Use query_id to prevent replays
cell processed_queries;  ;; Store processed query_ids

() recv_internal(...) {
    int query_id = in_msg_body~load_uint(64);

    ;; Check if already processed
    throw_if(403, is_processed(query_id));

    ;; Mark as processed
    mark_processed(query_id);

    ;; Process message
}
```

---

## Testing Strategies

### Blueprint Tests (TypeScript)

```typescript
import { Blockchain } from '@ton/sandbox';

describe('Counter', () => {
    let blockchain: Blockchain;
    let counter: SandboxContract<Counter>;

    beforeEach(async () => {
        blockchain = await Blockchain.create();
        counter = blockchain.openContract(...);
    });

    it('should handle insufficient value', async () => {
        const result = await counter.sendIncrement({
            value: toNano('0.001'), // Too small
        });

        expect(result.transactions).toHaveTransaction({
            success: false,
            exitCode: 402, // Insufficient value
        });
    });

    it('should handle bounce', async () => {
        // Send to non-existent contract
        const result = await counter.sendTo({
            to: Address.parse('EQBadAddress...'),
            value: toNano('1'),
        });

        expect(result.transactions).toHaveTransaction({
            from: recipient,
            to: counter.address,
            bounced: true,
        });
    });
});
```

### Gas Profiling

```typescript
it('should measure gas consumption', async () => {
    const result = await counter.sendIncrement({
        value: toNano('0.1'),
    });

    const tx = result.transactions[1]; // Internal transaction
    console.log('Gas used:', tx.gasUsed);
    console.log('Storage fees:', tx.storageFees);
});
```

---

## Common Pitfalls

### 1. Forgetting Bounce Flag

```func
;; VULNERABLE: No bounce check
() recv_internal(...) {
    int op = in_msg_body~load_uint(32);
    ;; Process op without checking if bounced
}

;; SECURE: Always check bounce
() recv_internal(...) {
    int flags = cs~load_uint(4);
    if (flags & 1) {  ;; Bounced message
        return ();
    }
    int op = in_msg_body~load_uint(32);
}
```

### 2. Incorrect Address Comparison

```func
;; [FAIL] WRONG: Direct equality (doesn't work)
if (addr1 == addr2) { ... }

;; [OK] CORRECT: Use equal_slices
if (equal_slices(addr1, addr2)) { ... }
```

### 3. Not Handling Empty Messages

```func
;; VULNERABLE: Assumes body exists
() recv_internal(...) {
    int op = in_msg_body~load_uint(32);  ;; May fail if empty
}

;; SECURE: Check for empty
() recv_internal(...) {
    if (in_msg_body.slice_empty?()) {
        return ();  ;; Ignore empty messages
    }
    int op = in_msg_body~load_uint(32);
}
```

### 4. Incorrect Gas Calculations

```func
;; [FAIL] WRONG: Sending all value (leaves nothing for gas)
send_raw_message(msg, 128);  ;; Sends all, contract may freeze

;; [OK] CORRECT: Leave balance for storage fees
send_raw_message(msg, 64);   ;; Send remaining, keep initial balance
```

### 5. Large Data in Single Cell

```func
;; [FAIL] WRONG: Too much data (>1023 bits)
cell data = begin_cell()
    .store_uint(value1, 256)
    .store_uint(value2, 256)
    .store_uint(value3, 256)
    .store_uint(value4, 256)  ;; 1024 bits - FAILS
    .end_cell();

;; [OK] CORRECT: Use references
cell data = begin_cell()
    .store_uint(value1, 256)
    .store_uint(value2, 256)
    .store_ref(
        begin_cell()
            .store_uint(value3, 256)
            .store_uint(value4, 256)
            .end_cell()
    )
    .end_cell();
```

---

## Production Checklist

Before deploying to mainnet:

**Security:**
- [ ] Bounce handling implemented
- [ ] Access control on privileged operations
- [ ] Integer overflow handling (automatic in FunC)
- [ ] Message value validation
- [ ] Query ID tracking for replay prevention
- [ ] Professional security audit completed

**Gas Optimization:**
- [ ] Data packed into minimal cells
- [ ] Inline functions used for helpers
- [ ] Unnecessary loads eliminated
- [ ] Storage fees calculated for contract lifetime

**Standards Compliance:**
- [ ] Jetton/NFT standards followed (if applicable)
- [ ] Metadata format correct (TEP-64)
- [ ] Required get methods implemented
- [ ] Wallet address calculation matches standard

**Testing:**
- [ ] Unit tests for all operations
- [ ] Bounce scenarios tested
- [ ] Insufficient value scenarios tested
- [ ] Gas consumption measured
- [ ] Testnet deployment verified

**TON Connect:**
- [ ] Manifest file hosted and accessible
- [ ] Transaction building tested
- [ ] Wallet compatibility verified
- [ ] Error handling implemented

---

## Resources

- [TON Documentation](https://docs.ton.org/)
- [FunC Documentation](https://docs.ton.org/develop/func/overview)
- [Tact Documentation](https://docs.tact-lang.org/)
- [TEPs (TON Enhancement Proposals)](https://github.com/ton-blockchain/TEPs)
- [TON Connect](https://docs.ton.org/develop/dapps/ton-connect/overview)
- [Blueprint Framework](https://github.com/ton-org/blueprint)
- [TON Cookbook](https://docs.ton.org/develop/smart-contracts/)
- [TON Community](https://t.me/tondev_eng)
