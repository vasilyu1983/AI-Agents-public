# TON Smart Contract Development — Tact + Blueprint Template

Production-grade TON smart contract development using Tact language (high-level, TypeScript-like) and Blueprint framework.

---

## Project Overview

This template provides a complete development environment for building TON smart contracts using:

- **Tact** - High-level smart contract language for TON (similar to TypeScript)
- **Blueprint** - Modern development framework
- **TypeScript** - Testing and deployment
- **TON SDK** - JavaScript library for TON
- **Sandbox** - Local blockchain testing

**Advantages of Tact over FunC:**
- TypeScript-like syntax (easier to learn)
- Built-in safety features (overflow protection, automatic serialization)
- Strong typing system
- Less boilerplate code
- Still compiles to efficient FunC code

**Use cases:** Jettons, NFTs, DeFi, wallets, DAOs, games

---

## Project Structure

```
tact-contract/
├── contracts/
│   ├── counter.tact         # Main contract
│   ├── jetton.tact          # Token contract
│   └── nft.tact             # NFT contract
├── wrappers/
│   ├── Counter.ts           # TypeScript wrapper
│   └── JettonMinter.ts      # Token wrapper
├── tests/
│   ├── Counter.spec.ts      # Tests
│   └── JettonMinter.spec.ts
├── scripts/
│   ├── deploy.ts            # Deployment
│   └── interact.ts          # Interaction
├── build/
│   └── counter.pkg          # Compiled package
├── tact.config.json
├── blueprint.config.ts
└── package.json
```

---

## Environment Setup

### 1. Install Prerequisites

```bash
# Install Node.js (v18+)

# Create new Blueprint + Tact project
npm create ton@latest

# Select "Tact" when prompted

# Or install Tact manually:
npm install --save-dev @tact-lang/compiler
npm install --save-dev @ton/blueprint @ton/core @ton/sandbox
```

### 2. Configure Tact

**tact.config.json:**
```json
{
    "projects": [
        {
            "name": "counter",
            "path": "./contracts/counter.tact",
            "output": "./build"
        },
        {
            "name": "jetton",
            "path": "./contracts/jetton.tact",
            "output": "./build"
        }
    ]
}
```

---

## Basic Counter Contract (Tact)

### Contract Code (contracts/counter.tact)

```tact
import "@stdlib/deploy";

message Increment {
    queryId: Int as uint64;
}

message Reset {
    queryId: Int as uint64;
    newCounter: Int as uint64;
}

message GetCounter {
    queryId: Int as uint64;
}

message CounterResponse {
    queryId: Int as uint64;
    counter: Int as uint64;
}

contract Counter with Deployable {
    counter: Int as uint64;
    owner: Address;

    init(owner: Address) {
        self.counter = 0;
        self.owner = owner;
    }

    // Increment counter
    receive(msg: Increment) {
        self.counter = self.counter + 1;
        self.reply(CounterResponse{
            queryId: msg.queryId,
            counter: self.counter
        }.toCell());
    }

    // Reset counter (owner only)
    receive(msg: Reset) {
        require(sender() == self.owner, "Only owner can reset");
        self.counter = msg.newCounter;
        self.reply(CounterResponse{
            queryId: msg.queryId,
            counter: self.counter
        }.toCell());
    }

    // Query counter
    receive(msg: GetCounter) {
        self.reply(CounterResponse{
            queryId: msg.queryId,
            counter: self.counter
        }.toCell());
    }

    // Get methods
    get fun counter(): Int {
        return self.counter;
    }

    get fun owner(): Address {
        return self.owner;
    }
}
```

---

## Jetton (Token) Contract Example

### Jetton Minter (contracts/jetton.tact)

```tact
import "@stdlib/deploy";
import "@stdlib/ownable";

// Messages for Jetton operations
message Mint {
    queryId: Int as uint64;
    to: Address;
    amount: Int as coins;
}

message Burn {
    queryId: Int as uint64;
    amount: Int as coins;
}

message Transfer {
    queryId: Int as uint64;
    to: Address;
    amount: Int as coins;
    responseAddress: Address?;
    customPayload: Cell?;
    forwardTonAmount: Int as coins;
    forwardPayload: Cell?;
}

message InternalTransfer {
    queryId: Int as uint64;
    amount: Int as coins;
    from: Address;
    responseAddress: Address?;
    forwardTonAmount: Int as coins;
    forwardPayload: Cell?;
}

message BurnNotification {
    queryId: Int as uint64;
    amount: Int as coins;
    owner: Address;
}

// Jetton Minter Contract
contract JettonMinter with Deployable, Ownable {
    totalSupply: Int as coins;
    owner: Address;
    content: Cell;
    mintable: Bool;

    init(owner: Address, content: Cell) {
        self.owner = owner;
        self.totalSupply = 0;
        self.content = content;
        self.mintable = true;
    }

    // Mint new tokens
    receive(msg: Mint) {
        self.requireOwner();
        require(self.mintable, "Not mintable");

        self.totalSupply = self.totalSupply + msg.amount;

        // Send internal transfer to wallet
        let walletInit: StateInit = self.getJettonWalletInit(msg.to);
        send(SendParameters{
            to: contractAddress(walletInit),
            value: ton("0.05"),
            mode: SendIgnoreErrors,
            bounce: false,
            body: InternalTransfer{
                queryId: msg.queryId,
                amount: msg.amount,
                from: myAddress(),
                responseAddress: self.owner,
                forwardTonAmount: 0,
                forwardPayload: emptyCell()
            }.toCell(),
            code: walletInit.code,
            data: walletInit.data
        });
    }

    // Burn notification from wallet
    receive(msg: BurnNotification) {
        let walletInit: StateInit = self.getJettonWalletInit(msg.owner);
        require(sender() == contractAddress(walletInit), "Invalid sender");

        self.totalSupply = self.totalSupply - msg.amount;
    }

    // Calculate wallet address
    fun getJettonWalletInit(owner: Address): StateInit {
        return initOf JettonWallet(myAddress(), owner);
    }

    // Get methods
    get fun totalSupply(): Int {
        return self.totalSupply;
    }

    get fun mintable(): Bool {
        return self.mintable;
    }

    get fun walletAddress(owner: Address): Address {
        let walletInit: StateInit = self.getJettonWalletInit(owner);
        return contractAddress(walletInit);
    }

    get fun jettonData(): JettonData {
        return JettonData{
            totalSupply: self.totalSupply,
            mintable: self.mintable,
            owner: self.owner,
            content: self.content,
            walletCode: self.getJettonWalletInit(myAddress()).code
        };
    }
}

// Jetton Wallet Contract
contract JettonWallet {
    master: Address;
    owner: Address;
    balance: Int as coins;

    init(master: Address, owner: Address) {
        self.master = master;
        self.owner = owner;
        self.balance = 0;
    }

    // Receive tokens from minter
    receive(msg: InternalTransfer) {
        require(sender() == self.master, "Only master can mint");
        self.balance = self.balance + msg.amount;

        // Notify recipient if needed
        if (msg.forwardTonAmount > 0 && msg.responseAddress != null) {
            send(SendParameters{
                to: msg.responseAddress!!,
                value: msg.forwardTonAmount,
                mode: SendIgnoreErrors,
                body: msg.forwardPayload
            });
        }
    }

    // Transfer tokens
    receive(msg: Transfer) {
        require(sender() == self.owner, "Only owner can transfer");
        require(self.balance >= msg.amount, "Insufficient balance");

        self.balance = self.balance - msg.amount;

        // Send to recipient wallet
        let recipientInit: StateInit = initOf JettonWallet(self.master, msg.to);
        send(SendParameters{
            to: contractAddress(recipientInit),
            value: ton("0.05"),
            mode: SendIgnoreErrors,
            bounce: true,
            body: InternalTransfer{
                queryId: msg.queryId,
                amount: msg.amount,
                from: self.owner,
                responseAddress: msg.responseAddress,
                forwardTonAmount: msg.forwardTonAmount,
                forwardPayload: msg.forwardPayload
            }.toCell(),
            code: recipientInit.code,
            data: recipientInit.data
        });
    }

    // Burn tokens
    receive(msg: Burn) {
        require(sender() == self.owner, "Only owner can burn");
        require(self.balance >= msg.amount, "Insufficient balance");

        self.balance = self.balance - msg.amount;

        // Notify minter
        send(SendParameters{
            to: self.master,
            value: 0,
            mode: SendRemainingValue,
            body: BurnNotification{
                queryId: msg.queryId,
                amount: msg.amount,
                owner: self.owner
            }.toCell()
        });
    }

    get fun balance(): Int {
        return self.balance;
    }

    get fun owner(): Address {
        return self.owner;
    }
}

// Data structures
struct JettonData {
    totalSupply: Int as coins;
    mintable: Bool;
    owner: Address;
    content: Cell;
    walletCode: Cell;
}
```

---

## TypeScript Wrapper

### Counter Wrapper (wrappers/Counter.ts)

```typescript
import { Address, beginCell, Cell, Contract, contractAddress, ContractProvider, Sender, SendMode } from '@ton/core';

export class Counter implements Contract {
    constructor(
        readonly address: Address,
        readonly init?: { code: Cell; data: Cell }
    ) {}

    static createFromConfig(owner: Address, code: Cell, workchain = 0) {
        const data = beginCell()
            .storeAddress(owner)
            .endCell();
        const init = { code, data };
        return new Counter(contractAddress(workchain, init), init);
    }

    async sendIncrement(
        provider: ContractProvider,
        via: Sender,
        value: bigint,
        queryId: bigint = 0n
    ) {
        await provider.internal(via, {
            value,
            sendMode: SendMode.PAY_GAS_SEPARATELY,
            body: beginCell()
                .storeUint(0x7e8764ef, 32) // Increment op code (generated by Tact)
                .storeUint(queryId, 64)
                .endCell(),
        });
    }

    async sendReset(
        provider: ContractProvider,
        via: Sender,
        value: bigint,
        newCounter: bigint,
        queryId: bigint = 0n
    ) {
        await provider.internal(via, {
            value,
            sendMode: SendMode.PAY_GAS_SEPARATELY,
            body: beginCell()
                .storeUint(0x9b1d1eb9, 32) // Reset op code
                .storeUint(queryId, 64)
                .storeUint(newCounter, 64)
                .endCell(),
        });
    }

    async getCounter(provider: ContractProvider): Promise<bigint> {
        const result = await provider.get('counter', []);
        return result.stack.readBigNumber();
    }

    async getOwner(provider: ContractProvider): Promise<Address> {
        const result = await provider.get('owner', []);
        return result.stack.readAddress();
    }
}
```

---

## Testing

### Test File (tests/Counter.spec.ts)

```typescript
import { Blockchain, SandboxContract, TreasuryContract } from '@ton/sandbox';
import { toNano } from '@ton/core';
import { Counter } from '../wrappers/Counter';
import '@ton/test-utils';

describe('Counter', () => {
    let blockchain: Blockchain;
    let deployer: SandboxContract<TreasuryContract>;
    let counter: SandboxContract<Counter>;

    beforeEach(async () => {
        blockchain = await Blockchain.create();
        deployer = await blockchain.treasury('deployer');

        // Compile Tact contract
        const { code, abi } = await import('../build/counter.compiled.json');

        counter = blockchain.openContract(
            Counter.createFromConfig(deployer.address, Cell.fromBase64(code))
        );

        await counter.sendDeploy(deployer.getSender(), toNano('0.05'));
    });

    it('should deploy and have zero counter', async () => {
        const counterValue = await counter.getCounter();
        expect(counterValue).toBe(0n);

        const owner = await counter.getOwner();
        expect(owner.equals(deployer.address)).toBe(true);
    });

    it('should increment counter', async () => {
        await counter.sendIncrement(deployer.getSender(), toNano('0.05'));

        const counterValue = await counter.getCounter();
        expect(counterValue).toBe(1n);
    });

    it('should increment multiple times', async () => {
        for (let i = 0; i < 5; i++) {
            await counter.sendIncrement(deployer.getSender(), toNano('0.05'));
        }

        const counterValue = await counter.getCounter();
        expect(counterValue).toBe(5n);
    });

    it('should reset counter (owner)', async () => {
        await counter.sendIncrement(deployer.getSender(), toNano('0.05'));
        await counter.sendIncrement(deployer.getSender(), toNano('0.05'));

        await counter.sendReset(deployer.getSender(), toNano('0.05'), 10n);

        const counterValue = await counter.getCounter();
        expect(counterValue).toBe(10n);
    });

    it('should reject reset from non-owner', async () => {
        const notOwner = await blockchain.treasury('notOwner');

        const result = await counter.sendReset(notOwner.getSender(), toNano('0.05'), 100n);

        expect(result.transactions).toHaveTransaction({
            from: notOwner.address,
            to: counter.address,
            success: false,
        });
    });
});
```

---

## Deployment

### Deploy Script (scripts/deploy.ts)

```typescript
import { toNano } from '@ton/core';
import { Counter } from '../wrappers/Counter';
import { NetworkProvider } from '@ton/blueprint';
import { compile } from '@tact-lang/compiler';

export async function run(provider: NetworkProvider) {
    // Compile Tact contract
    const result = await compile({
        project: {
            name: 'counter',
            path: './contracts/counter.tact',
            output: './build',
        },
    });

    const counter = provider.open(
        Counter.createFromConfig(
            provider.sender().address!,
            result.code
        )
    );

    await counter.sendDeploy(provider.sender(), toNano('0.05'));

    await provider.waitForDeploy(counter.address);

    console.log('Counter deployed at:', counter.address);
    console.log('Initial counter:', await counter.getCounter());
}
```

---

## Advanced Features

### Traits (Reusable Components)

```tact
trait Pausable {
    paused: Bool;

    receive("pause") {
        require(!self.paused, "Already paused");
        self.paused = true;
    }

    receive("unpause") {
        require(self.paused, "Not paused");
        self.paused = false;
    }

    fun requireNotPaused() {
        require(!self.paused, "Contract is paused");
    }
}

contract MyContract with Deployable, Pausable {
    paused: Bool;

    init() {
        self.paused = false;
    }

    receive("doSomething") {
        self.requireNotPaused();
        // Do something
    }
}
```

### Maps and Iteration

```tact
contract Storage {
    items: map<Int, Int>;
    count: Int as uint32;

    init() {
        self.count = 0;
    }

    receive("add") {
        self.items.set(self.count, now());
        self.count = self.count + 1;
    }

    get fun get(key: Int): Int? {
        return self.items.get(key);
    }

    get fun size(): Int {
        return self.count;
    }
}
```

---

## Useful Commands

### Development

```bash
# Build Tact contracts
npx @tact-lang/compiler

# Or with Blueprint:
npx blueprint build

# Run tests
npx blueprint test

# Watch mode
npx blueprint test --watch

# Deploy
npx blueprint run
```

### Tact CLI

```bash
# Compile specific contract
npx @tact-lang/compiler contracts/counter.tact

# Generate bindings
npx @tact-lang/compiler --bindings typescript contracts/counter.tact
```

---

## Tact Language Features

### Type System

```tact
// Primitive types
let x: Int = 42;
let y: Bool = true;
let addr: Address = address("...");
let c: Cell = emptyCell();
let s: Slice = emptySlice();

// Optional types
let maybe: Int? = null;
let value: Int = maybe ?: 0; // Default value

// Coins (special type for TON amounts)
let amount: Int as coins = ton("1.5");
```

### Structs and Messages

```tact
struct User {
    name: String;
    age: Int as uint8;
    balance: Int as coins;
}

message UpdateUser {
    queryId: Int as uint64;
    user: User;
}
```

### Safety Features

```tact
// Automatic overflow protection
let x: Int = 1000000000000000000;
let y: Int = x + 1; // Safe, won't overflow

// Require statements
require(sender() == self.owner, "Unauthorized");

// Safe math operations
let result: Int = a.checked_add(b); // Returns null on overflow
```

---

## Production Checklist

Before deploying to mainnet:

**Security:**
- [ ] All operations have authorization checks
- [ ] Overflow/underflow handled
- [ ] Gas consumption measured
- [ ] Professional audit completed

**Testing:**
- [ ] 100% test coverage
- [ ] Edge cases tested
- [ ] Gas benchmarks
- [ ] Testnet deployment verified

**Deployment:**
- [ ] Contracts compiled and optimized
- [ ] Initial state configured
- [ ] Owner/admin keys secured
- [ ] Monitoring setup

**Documentation:**
- [ ] README complete
- [ ] API documented
- [ ] Known limitations listed

---

## Resources

- [Tact Documentation](https://docs.tact-lang.org/)
- [Tact by Example](https://tact-by-example.org/)
- [TON Documentation](https://docs.ton.org/)
- [Blueprint](https://github.com/ton-org/blueprint)
- [TON Sandbox](https://github.com/ton-org/sandbox)
- [Jetton Standard](https://github.com/ton-blockchain/TEPs/blob/master/text/0074-jettons-standard.md)
