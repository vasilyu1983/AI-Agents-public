# Bitcoin Development — Bitcoin Core & Lightning Network Template

Production-grade Bitcoin development with Bitcoin Core, Lightning Network, and scripting.

---

## Project Overview

This template provides guidance for Bitcoin development using:

- **Bitcoin Core** - Reference implementation of Bitcoin
- **Bitcoin Script** - Stack-based scripting language
- **Lightning Network** - Layer 2 payment channels
- **BDK (Bitcoin Dev Kit)** - Rust library for wallet development
- **Electrum/Electrs** - Server for SPV wallets
- **BTCPay Server** - Self-hosted payment processor

**Use cases:** Wallets, payment processors, Lightning apps, multisig, timelock contracts, DLCs

---

## Project Structure

```
bitcoin-project/
├── bitcoin-core/
│   ├── bitcoin.conf         # Node configuration
│   └── scripts/
│       ├── multisig.sh      # Multisig wallet scripts
│       └── timelock.sh      # Timelock scripts
├── wallet/
│   ├── src/
│   │   ├── main.rs          # BDK wallet implementation
│   │   ├── descriptors.rs   # Output descriptors
│   │   └── psbt.rs          # PSBT handling
│   └── Cargo.toml
├── lightning/
│   ├── lnd.conf             # LND configuration
│   └── node/
│       ├── channels.ts      # Channel management
│       └── invoices.ts      # Invoice handling
└── scripts/
    ├── deploy-node.sh       # Node deployment
    └── backup.sh            # Backup scripts
```

---

## Environment Setup

### 1. Install Bitcoin Core

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install bitcoind bitcoin-cli

# macOS (Homebrew)
brew install bitcoin

# Or download from bitcoin.org
wget https://bitcoincore.org/bin/bitcoin-core-25.0/bitcoin-25.0-x86_64-linux-gnu.tar.gz
tar -xzf bitcoin-25.0-x86_64-linux-gnu.tar.gz
sudo install -m 0755 -o root -g root -t /usr/local/bin bitcoin-25.0/bin/*
```

### 2. Configure Bitcoin Core

**~/.bitcoin/bitcoin.conf:**
```conf
# Network
testnet=1              # Use testnet (remove for mainnet)
# signet=1             # Or use signet for testing

# RPC
server=1
rpcuser=your_username
rpcpassword=your_secure_password
rpcallowip=127.0.0.1
rpcport=18332          # 8332 for mainnet

# Indexing (optional, needed for some features)
txindex=1              # Index all transactions
addressindex=1         # Index addresses
timestampindex=1       # Index timestamps
spentindex=1           # Index spent outputs

# Mempool
maxmempool=300         # MB
mempoolexpiry=72       # hours

# Pruning (for space-constrained nodes)
# prune=550            # Keep only 550MB of blocks
```

### 3. Start Bitcoin Node

```bash
# Start daemon
bitcoind -daemon

# Check status
bitcoin-cli getblockchaininfo

# Stop daemon
bitcoin-cli stop
```

---

## Bitcoin Scripting

### Basic Scripts

**Pay to Public Key Hash (P2PKH):**
```
OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

**Pay to Script Hash (P2SH):**
```
OP_HASH160 <scriptHash> OP_EQUAL
```

**Pay to Witness Public Key Hash (P2WPKH - SegWit):**
```
OP_0 <pubKeyHash>
```

**Pay to Taproot (P2TR):**
```
OP_1 <taproot_output_key>
```

### Multisig Script (2-of-3)

```bash
#!/bin/bash
# Create 2-of-3 multisig address

# Generate 3 addresses
ADDR1=$(bitcoin-cli getnewaddress)
ADDR2=$(bitcoin-cli getnewaddress)
ADDR3=$(bitcoin-cli getnewaddress)

# Get public keys
PUBKEY1=$(bitcoin-cli getaddressinfo $ADDR1 | jq -r '.pubkey')
PUBKEY2=$(bitcoin-cli getaddressinfo $ADDR2 | jq -r '.pubkey')
PUBKEY3=$(bitcoin-cli getaddressinfo $ADDR3 | jq -r '.pubkey')

# Create multisig address
bitcoin-cli createmultisig 2 "[\"$PUBKEY1\",\"$PUBKEY2\",\"$PUBKEY3\"]"
```

**Output:**
```json
{
  "address": "2N...",
  "redeemScript": "5221...53ae",
  "descriptor": "wsh(multi(2,[...],...))#..."
}
```

### Timelock Script (CSV - CheckSequenceVerify)

```
# Script: Coins can be spent after 144 blocks (~24 hours)
<144> OP_CHECKSEQUENCEVERIFY OP_DROP
<pubKey> OP_CHECKSIG
```

**Creating timelock transaction:**
```bash
# Create raw transaction with sequence number
bitcoin-cli createrawtransaction \
  '[{"txid":"<txid>","vout":0,"sequence":144}]' \
  '{"<recipient_address>":0.01}'

# Sign and broadcast
bitcoin-cli signrawtransactionwithwallet <raw_tx>
bitcoin-cli sendrawtransaction <signed_tx>
```

---

## Wallet Development with BDK

### Rust Wallet Implementation

**Cargo.toml:**
```toml
[dependencies]
bdk = { version = "0.29", features = ["electrum"] }
bitcoin = "0.30"
```

**src/main.rs:**
```rust
use bdk::{
    bitcoin::{Address, Network},
    blockchain::ElectrumBlockchain,
    database::MemoryDatabase,
    electrum_client::Client,
    wallet::AddressIndex,
    KeychainKind, SyncOptions, Wallet,
};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create wallet with descriptor
    let external_descriptor = "wpkh([c258d2e4/84h/1h/0h]tpubD...)";
    let internal_descriptor = "wpkh([c258d2e4/84h/1h/0h]tpubD...)";

    let wallet = Wallet::new(
        external_descriptor,
        Some(internal_descriptor),
        Network::Testnet,
        MemoryDatabase::default(),
    )?;

    // Connect to Electrum server
    let client = Client::new("ssl://electrum.blockstream.info:60002")?;
    let blockchain = ElectrumBlockchain::from(client);

    // Sync wallet
    wallet.sync(&blockchain, SyncOptions::default())?;

    // Get balance
    let balance = wallet.get_balance()?;
    println!("Balance: {} sats", balance);

    // Get new address
    let address = wallet.get_address(AddressIndex::New)?;
    println!("New address: {}", address);

    // Create transaction
    let mut tx_builder = wallet.build_tx();
    tx_builder
        .add_recipient(Address::from_str("tb1...")?.script_pubkey(), 50_000)
        .fee_rate(bdk::FeeRate::from_sat_per_vb(1.0));

    let (mut psbt, _) = tx_builder.finish()?;

    // Sign transaction
    let finalized = wallet.sign(&mut psbt, Default::default())?;
    println!("Transaction signed: {}", finalized);

    // Extract and broadcast
    if finalized {
        let tx = psbt.extract_tx();
        blockchain.broadcast(&tx)?;
        println!("Transaction broadcast: {}", tx.txid());
    }

    Ok(())
}
```

---

## Lightning Network Integration

### LND Setup

**Install LND:**
```bash
# Download LND
wget https://github.com/lightningnetwork/lnd/releases/download/v0.17.0/lnd-linux-amd64-v0.17.0.tar.gz
tar -xzf lnd-linux-amd64-v0.17.0.tar.gz
sudo install -m 0755 -o root -g root -t /usr/local/bin lnd-linux-amd64-v0.17.0/*
```

**lnd.conf:**
```conf
[Application Options]
debuglevel=info
alias=MyLightningNode
color=#3399FF

[Bitcoin]
bitcoin.active=1
bitcoin.testnet=1
bitcoin.node=bitcoind

[Bitcoind]
bitcoind.rpcuser=your_username
bitcoind.rpcpass=your_password
bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333
```

**Start LND:**
```bash
lnd
```

### Channel Management

```bash
# Create wallet
lncli create

# Get node info
lncli getinfo

# Connect to peer
lncli connect 03..@host:port

# Open channel (1,000,000 sats)
lncli openchannel --node_key=03... --local_amt=1000000

# List channels
lncli listchannels

# Close channel
lncli closechannel <funding_txid> <output_index>
```

### Invoice and Payment

```bash
# Create invoice (10,000 sats)
lncli addinvoice --amt=10000 --memo="Coffee"

# Decode invoice
lncli decodepayreq <payment_request>

# Pay invoice
lncli payinvoice <payment_request>

# List invoices
lncli listinvoices

# List payments
lncli listpayments
```

### LND gRPC Client (TypeScript)

```typescript
import * as fs from 'fs';
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';

const lndCert = fs.readFileSync('/path/to/tls.cert');
const macaroon = fs.readFileSync('/path/to/admin.macaroon').toString('hex');

const packageDefinition = protoLoader.loadSync('lightning.proto');
const lnrpc = grpc.loadPackageDefinition(packageDefinition).lnrpc;

const credentials = grpc.credentials.createSsl(lndCert);
const macaroonCreds = grpc.credentials.createFromMetadataGenerator((args, callback) => {
    const metadata = new grpc.Metadata();
    metadata.add('macaroon', macaroon);
    callback(null, metadata);
});

const combinedCreds = grpc.credentials.combineChannelCredentials(
    credentials,
    macaroonCreds
);

const lightning = new lnrpc.Lightning('localhost:10009', combinedCreds);

// Get node info
lightning.getInfo({}, (err, response) => {
    if (err) console.error(err);
    else console.log('Node info:', response);
});

// Create invoice
lightning.addInvoice({ value: 10000, memo: 'Coffee' }, (err, response) => {
    if (err) console.error(err);
    else console.log('Invoice:', response.payment_request);
});

// Pay invoice
lightning.sendPaymentSync({
    payment_request: 'lnbc...'
}, (err, response) => {
    if (err) console.error(err);
    else console.log('Payment sent:', response);
});
```

---

## PSBT (Partially Signed Bitcoin Transactions)

### Creating and Signing PSBT

```bash
# Create PSBT
bitcoin-cli walletcreatefundedpsbt \
  '[]' \
  '[{"<address>":0.01}]' \
  | jq -r '.psbt' > unsigned.psbt

# Sign PSBT (wallet 1)
bitcoin-cli -rpcwallet=wallet1 walletprocesspsbt $(cat unsigned.psbt) \
  | jq -r '.psbt' > partially_signed.psbt

# Sign PSBT (wallet 2)
bitcoin-cli -rpcwallet=wallet2 walletprocesspsbt $(cat partially_signed.psbt) \
  | jq -r '.psbt' > fully_signed.psbt

# Finalize and broadcast
bitcoin-cli finalizepsbt $(cat fully_signed.psbt) \
  | jq -r '.hex' | xargs bitcoin-cli sendrawtransaction
```

---

## Output Descriptors

### Descriptor Types

```
# Single key P2WPKH
wpkh(xpub.../0/*)

# Multisig P2WSH (2-of-3)
wsh(multi(2,xpub1.../0/*,xpub2.../0/*,xpub3.../0/*))

# Nested SegWit (P2SH-P2WPKH)
sh(wpkh(xpub.../0/*))

# Taproot
tr(xpub.../0/*)

# With checksum
wpkh([fingerprint/derivation]xpub...)#checksum
```

### Import Descriptor

```bash
# Import watch-only descriptor
bitcoin-cli importdescriptors '[{
  "desc": "wpkh([c258d2e4/84h/1h/0h]tpubD...)#checksum",
  "timestamp": "now",
  "range": [0, 1000],
  "watchonly": true
}]'
```

---

## Useful Commands

### Node Operations

```bash
# Get blockchain info
bitcoin-cli getblockchaininfo

# Get mempool info
bitcoin-cli getmempoolinfo

# Get network info
bitcoin-cli getnetworkinfo

# Get peer info
bitcoin-cli getpeerinfo

# Add node
bitcoin-cli addnode "<ip>:port" "add"

# Generate blocks (regtest only)
bitcoin-cli -regtest generatetoaddress 101 <address>
```

### Wallet Operations

```bash
# Create wallet
bitcoin-cli createwallet "my_wallet"

# Load wallet
bitcoin-cli loadwallet "my_wallet"

# Get new address
bitcoin-cli getnewaddress "" "bech32"

# Get balance
bitcoin-cli getbalance

# Send transaction
bitcoin-cli sendtoaddress <address> 0.01

# List transactions
bitcoin-cli listtransactions

# List unspent outputs
bitcoin-cli listunspent

# Dump private key
bitcoin-cli dumpprivkey <address>

# Import private key
bitcoin-cli importprivkey <privkey>
```

### Transaction Operations

```bash
# Get raw transaction
bitcoin-cli getrawtransaction <txid> true

# Decode raw transaction
bitcoin-cli decoderawtransaction <hex>

# Test mempool accept
bitcoin-cli testmempoolaccept '["<hex>"]'

# Get transaction out
bitcoin-cli gettxout <txid> <vout>
```

---

## Testing with Regtest

```bash
# Start regtest node
bitcoind -regtest -daemon

# Create wallet
bitcoin-cli -regtest createwallet "test"

# Get new address
ADDR=$(bitcoin-cli -regtest getnewaddress)

# Mine 101 blocks (coinbase maturity)
bitcoin-cli -regtest generatetoaddress 101 $ADDR

# Check balance
bitcoin-cli -regtest getbalance

# Send transaction
bitcoin-cli -regtest sendtoaddress <recipient> 1.0

# Mine block to confirm
bitcoin-cli -regtest generatetoaddress 1 $ADDR
```

---

## Production Checklist

Before running in production:

**Security:**
- [ ] Use strong RPC password
- [ ] Firewall configured (only allow localhost for RPC)
- [ ] Regular backups of wallet.dat
- [ ] Encrypted wallet (`bitcoin-cli encryptwallet`)
- [ ] Monitor for security updates

**Performance:**
- [ ] Sufficient disk space (500GB+ for full node)
- [ ] 8GB+ RAM recommended
- [ ] SSD preferred for chainstate
- [ ] Monitor sync status

**Reliability:**
- [ ] Automated backups
- [ ] Monitoring and alerting
- [ ] Redundant peers configured
- [ ] Regular software updates

**Lightning (if applicable):**
- [ ] Channel backups automated
- [ ] Watchtower configured
- [ ] Sufficient inbound liquidity
- [ ] Fee policies set appropriately

---

## Resources

- [Bitcoin Core Documentation](https://bitcoin.org/en/bitcoin-core/)
- [Bitcoin Developer Guide](https://developer.bitcoin.org/)
- [BDK Documentation](https://bitcoindevkit.org/)
- [Lightning Network Specification](https://github.com/lightning/bolts)
- [LND Documentation](https://docs.lightning.engineering/)
- [Mastering Bitcoin](https://github.com/bitcoinbook/bitcoinbook)
- [Bitcoin Script](https://en.bitcoin.it/wiki/Script)
- [BIPs (Bitcoin Improvement Proposals)](https://github.com/bitcoin/bips)
