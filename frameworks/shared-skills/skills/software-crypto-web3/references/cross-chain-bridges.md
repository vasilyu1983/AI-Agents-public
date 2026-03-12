# Cross-Chain Bridge Architecture and Security

Patterns for building and integrating cross-chain bridges, including architecture models, trust assumptions, protocol-specific patterns (LayerZero, Wormhole, IBC), security analysis of major bridge exploits, and a risk assessment framework for bridge selection.

---

## Table of Contents

1. [Bridge Architectures](#bridge-architectures)
2. [Trust Models](#trust-models)
3. [LayerZero Patterns](#layerzero-patterns)
4. [Wormhole Patterns](#wormhole-patterns)
5. [IBC (Cosmos)](#ibc-cosmos)
6. [Bridge Security: Major Exploits](#bridge-security-major-exploits)
7. [Risk Assessment Framework](#risk-assessment-framework)
8. [Testing Cross-Chain Transactions](#testing-cross-chain-transactions)
9. [Anti-Patterns](#anti-patterns)

---

## Bridge Architectures

### Core Models

| Architecture | How It Works | Examples |
|-------------|-------------|---------|
| Lock-and-Mint | Lock tokens on source, mint wrapped on destination | WBTC, many generic bridges |
| Burn-and-Mint | Burn native tokens on source, mint native on destination | LayerZero OFT, Circle CCTP |
| Liquidity Pool | Swap against pools on each chain (no wrapping) | Stargate, Across |
| Atomic Swap | Hash time-locked contracts (HTLC) | THORChain, older DEXes |

### Lock-and-Mint Flow

```text
Source Chain                    Bridge                    Destination Chain
+-----------+                +---------+                +---------------+
| User locks|  lock event   | Relayer |  mint message  | Mint wrapped  |
| 100 ETH   | ----------->  | detects | ------------> | 100 wETH to   |
| in bridge |                | event   |                | user          |
+-----------+                +---------+                +---------------+

Return flow:
| User burns|  burn event   | Relayer |  unlock msg    | Unlock 100    |
| 100 wETH  | ----------->  | detects | ------------> | native ETH    |
|           |                |         |                | to user       |
+-----------+                +---------+                +---------------+
```

**Risk**: Wrapped tokens are only as secure as the bridge. If the bridge is compromised, wrapped tokens become unbacked.

### Burn-and-Mint Flow (Native Bridging)

```text
Source Chain                    Bridge                    Destination Chain
+-----------+                +---------+                +---------------+
| Burn 100  |  burn proof    | Verify  |  mint native   | Mint 100      |
| USDC      | ----------->  | proof   | ------------> | USDC          |
|           |                |         |                | (native)      |
+-----------+                +---------+                +---------------+

Advantage: No wrapped tokens. Same canonical token on both chains.
Examples: Circle CCTP (USDC), LayerZero OFT
```

### Liquidity Pool Model

```text
Source Chain                                              Destination Chain
+-----------+                                            +---------------+
| User swaps|  message + proof                           | Pool releases |
| 100 USDC  | ----------------------------------------> | 99.97 USDC   |
| into pool |                                            | from pool     |
+-----------+                                            +---------------+

Advantage: Instant finality (no minting delay)
Disadvantage: Requires liquidity on both sides, rebalancing needed
```

---

## Trust Models

### Trust Model Comparison

| Model | Validators | Security Assumption | Speed | Examples |
|-------|-----------|---------------------|-------|---------|
| Trusted (Multisig) | Fixed set of signers (e.g., 5/8) | Majority honest | Fast (minutes) | Many early bridges |
| Optimistic | Anyone can relay; watchers can challenge | At least 1 honest watcher | Slow (challenge period) | Across, Connext |
| Light Client | On-chain verification of source chain headers | Cryptographic proof | Medium | IBC, bridge using ZK proofs |
| ZK-Proof | Zero-knowledge proof of source chain state | Math (cryptographic) | Medium-slow (proof generation) | Succinct, zkBridge |
| Economic | Staked validators with slashing | Rational actors | Fast | Axelar, Chainlink CCIP |

### Security Spectrum

```text
Least Secure                                              Most Secure
<------------------------------------------------------------------>
Multisig        Optimistic      Economic       Light Client    ZK-Proof
(trust N/M)     (1 watcher)     (staking)      (crypto)        (math)

Trade-off: More secure = slower and/or more expensive
```

### Choosing a Trust Model

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| High-value DeFi transfers | Light client or ZK | Cannot afford compromise |
| Fast user transfers | Optimistic + insurance | Speed matters, risk managed |
| Governance messages | Light client | Integrity critical, latency acceptable |
| Gaming assets | Economic or optimistic | Lower value, speed preferred |
| Stablecoin bridging | Native burn-and-mint | Canonical token (Circle CCTP) |

---

## LayerZero Patterns

### Architecture

```text
LayerZero V2 Architecture:
  Source Chain         LayerZero          Destination Chain
  +-----------+      +-----------+      +---------------+
  | OApp      | ---> | DVN       | ---> | OApp          |
  | (sends)   |      | (verify)  |      | (receives)    |
  +-----------+      +-----------+      +---------------+
                     | Executor  |
                     | (deliver) |
                     +-----------+

  DVN: Decentralized Verifier Network (configurable security)
  Executor: Delivers message to destination (configurable)
```

### OApp (Omnichain Application)

```solidity
// LayerZero V2 OApp pattern
import { OApp, Origin, MessagingFee } from "@layerzerolabs/oapp-evm";

contract MyOApp is OApp {
    constructor(
        address endpoint,
        address delegate
    ) OApp(endpoint, delegate) {}

    // Send cross-chain message
    function sendMessage(
        uint32 dstEid,        // Destination endpoint ID
        bytes calldata payload,
        bytes calldata options // Gas settings, executor options
    ) external payable {
        _lzSend(
            dstEid,
            payload,
            options,
            MessagingFee(msg.value, 0),  // Native fee
            payable(msg.sender)           // Refund address
        );
    }

    // Receive cross-chain message
    function _lzReceive(
        Origin calldata origin,   // Source chain info
        bytes32 guid,             // Unique message ID
        bytes calldata payload,
        address executor,
        bytes calldata extraData
    ) internal override {
        // Process the cross-chain message
        // origin.srcEid = source endpoint ID
        // origin.sender = sender address (bytes32)
        _processMessage(origin.srcEid, payload);
    }
}
```

### OFT (Omnichain Fungible Token)

```solidity
// LayerZero OFT: burn-and-mint cross-chain token
import { OFT } from "@layerzerolabs/oft-evm";

contract MyOFT is OFT {
    constructor(
        string memory name,
        string memory symbol,
        address lzEndpoint,
        address delegate
    ) OFT(name, symbol, lzEndpoint, delegate) {}

    // Usage: token.send(dstEid, to, amount, options)
    // Automatically burns on source, mints on destination
}

// OFTAdapter: wrap existing ERC-20 for cross-chain
import { OFTAdapter } from "@layerzerolabs/oft-evm";

contract MyOFTAdapter is OFTAdapter {
    constructor(
        address token,          // Existing ERC-20
        address lzEndpoint,
        address delegate
    ) OFTAdapter(token, lzEndpoint, delegate) {}
    // Locks on source chain, mints OFT on destination
}
```

### LayerZero Security Configuration

```solidity
// Configure DVN (Decentralized Verifier Network) per pathway
// Example: require both Google Cloud DVN + Polyhedra DVN
SetConfigParam[] memory params = new SetConfigParam[](1);
params[0] = SetConfigParam({
    eid: destinationEid,
    configType: CONFIG_TYPE_ULN,
    config: abi.encode(UlnConfig({
        confirmations: 15,
        requiredDVNCount: 2,
        optionalDVNCount: 0,
        optionalDVNThreshold: 0,
        requiredDVNs: [googleCloudDVN, polyhedraDVN],
        optionalDVNs: []
    }))
});
```

---

## Wormhole Patterns

### Guardian Network

```text
Wormhole Architecture:
  Source Chain          Guardians (19)         Destination Chain
  +-----------+      +----------------+      +---------------+
  | Core       | --> | 13/19 sign     | --> | Core           |
  | Contract   |     | the VAA        |     | Contract       |
  | (publish)  |     | (Verified      |     | (verify +      |
  |            |     |  Action         |     |  execute)      |
  +-----------+      |  Approval)     |      +---------------+
                     +----------------+

  VAA: Verified Action Approval
    - Contains: emitter chain, emitter address, sequence, payload
    - Signed by 13/19 Guardians (supermajority)
    - Verifiable on any supported chain
```

### Sending Messages

```solidity
// Wormhole message publishing
interface IWormhole {
    function publishMessage(
        uint32 nonce,
        bytes memory payload,
        uint8 consistencyLevel  // Finality level
    ) external payable returns (uint64 sequence);
}

contract WormholeSender {
    IWormhole public wormhole;

    function sendCrossChain(bytes memory data) external payable {
        uint64 sequence = wormhole.publishMessage{value: msg.value}(
            0,      // nonce
            data,   // payload
            1       // consistency: finalized
        );
        // sequence is used to track the message
    }
}
```

### Receiving and Verifying VAAs

```solidity
contract WormholeReceiver {
    IWormhole public wormhole;
    mapping(bytes32 => bool) public processedMessages;

    function receiveMessage(bytes memory vaa) external {
        // Parse and verify the VAA
        (IWormhole.VM memory vm, bool valid, string memory reason) =
            wormhole.parseAndVerifyVM(vaa);
        require(valid, reason);

        // Prevent replay
        require(!processedMessages[vm.hash], "Already processed");
        processedMessages[vm.hash] = true;

        // Verify source (emitter chain + address)
        require(vm.emitterChainId == EXPECTED_CHAIN, "Wrong chain");
        require(vm.emitterAddress == EXPECTED_EMITTER, "Wrong emitter");

        // Process the payload
        _processPayload(vm.payload);
    }
}
```

### Wormhole Relayer (Automatic Delivery)

```solidity
// Automatic relayer: no manual VAA submission needed
import "wormhole-solidity-sdk/WormholeRelayerSDK.sol";

contract AutomaticRelay is TokenSender, TokenReceiver {
    function sendCrossChainWithTokens(
        uint16 targetChain,
        address targetAddress,
        bytes memory payload,
        uint256 amount,
        address token
    ) external payable {
        sendTokenWithPayloadToEvm(
            targetChain,
            targetAddress,
            payload,
            0, // receiverValue
            GAS_LIMIT,
            token,
            amount
        );
    }
}
```

---

## IBC (Cosmos)

### Channel Lifecycle

```text
IBC Channel Handshake (4-step):
  Chain A                          Chain B
  1. ChanOpenInit    ----------->
  2.                 <-----------  ChanOpenTry
  3. ChanOpenAck     ----------->
  4.                 <-----------  ChanOpenConfirm

  After handshake: bidirectional packet relay
```

### Packet Relay

```text
IBC Packet Flow:
  Chain A                  Relayer               Chain B
  +---------+            +---------+            +---------+
  | SendPkt | ---------> | Relay   | ---------> | RecvPkt |
  |         |            | (proof) |            |         |
  |         | <--------- |         | <--------- | WriteAck|
  | AckPkt  |            |         |            |         |
  +---------+            +---------+            +---------+

  Relayer: permissionless, anyone can run
  Security: Light client verification (no trusted third party)
```

### CosmWasm IBC Contract

```rust
// IBC-enabled CosmWasm contract
#[cfg_attr(not(feature = "library"), entry_point)]
pub fn ibc_channel_open(
    deps: DepsMut,
    env: Env,
    msg: IbcChannelOpenMsg,
) -> Result<IbcChannelOpenResponse, ContractError> {
    // Validate channel parameters (version, ordering)
    let channel = msg.channel();
    if channel.version != IBC_VERSION {
        return Err(ContractError::InvalidVersion {});
    }
    Ok(None)
}

#[cfg_attr(not(feature = "library"), entry_point)]
pub fn ibc_packet_receive(
    deps: DepsMut,
    env: Env,
    msg: IbcPacketReceiveMsg,
) -> Result<IbcReceiveResponse, ContractError> {
    let packet_data: MyPacketData = from_json(&msg.packet.data)?;
    // Process cross-chain message
    let response = IbcReceiveResponse::new()
        .set_ack(ack_success())
        .add_attribute("action", "receive");
    Ok(response)
}
```

### IBC Security Properties

| Property | Implementation |
|----------|----------------|
| Trustless | Light client verification on both chains |
| Permissionless relay | Anyone can run a relayer |
| Ordered delivery | Ordered channels guarantee sequence |
| Timeout | Packets expire if not delivered |
| Replay protection | Sequence numbers prevent replay |

---

## Bridge Security: Major Exploits

### Historical Exploits

| Bridge | Date | Loss | Root Cause | Lesson |
|--------|------|------|------------|--------|
| Ronin (Axie) | Mar 2022 | $624M | 5/9 validator keys compromised | Insufficient validator decentralization |
| Wormhole | Feb 2022 | $326M | Signature verification bypass | Incomplete input validation |
| Nomad | Aug 2022 | $190M | Fraudulent root accepted as valid | Initialization bug in upgrade |
| Harmony Horizon | Jun 2022 | $100M | 2/5 multisig compromised | Too few signers, single point of failure |
| Multichain | Jul 2023 | $126M | CEO arrested, keys compromised | Centralized key management |

### Common Bridge Vulnerability Classes

| Vulnerability | Description | Prevention |
|---------------|------------|------------|
| Insufficient validation | Message or proof not properly verified | Validate all fields: chain, sender, nonce, payload |
| Key compromise | Validator/signer keys stolen | HSM/MPC, separation of duties, key rotation |
| Replay attacks | Same message processed twice | Nonce tracking, message hash deduplication |
| Upgrade bugs | Proxy upgrade introduces vulnerability | Timelocks, multi-sig upgrades, formal verification |
| Relayer manipulation | Relayer submits invalid proofs | On-chain proof verification, multiple relayers |
| Destination chain spoofing | Message claims to be from wrong source | Verify emitter chain ID + address |

### Security Checklist for Bridge Integration

- [ ] Verify message source chain and sender address
- [ ] Deduplicate messages (prevent replay)
- [ ] Validate payload format and bounds
- [ ] Set appropriate gas limits for cross-chain execution
- [ ] Implement timeout handling for failed deliveries
- [ ] Rate-limit high-value transfers
- [ ] Monitor for anomalous bridge activity
- [ ] Test with adversarial scenarios (partial delivery, out-of-order)

---

## Risk Assessment Framework

### Bridge Evaluation Criteria

| Criterion | Weight | Questions to Ask |
|-----------|--------|-----------------|
| Trust model | 30% | How many validators? What happens if compromised? |
| Track record | 20% | Any past exploits? How were they handled? |
| Audit history | 15% | Number of audits? By whom? Findings resolved? |
| TVL and usage | 10% | How much value secured? How long in production? |
| Code quality | 10% | Open source? Test coverage? Formal verification? |
| Team and funding | 10% | Who maintains it? Funded for long-term? |
| Monitoring and response | 5% | Incident response plan? Real-time monitoring? |

### Risk Scoring Matrix

```text
Risk Score = sum of (criterion_score * weight)

Criterion scores (1-5):
  1: Critical risk (no audit, centralized, past exploit)
  2: High risk (single audit, small validator set)
  3: Medium risk (multiple audits, medium validator set)
  4: Low risk (well-audited, large validator set, no exploits)
  5: Minimal risk (formal verification, decentralized, long track record)

Decision thresholds:
  4.0+: Suitable for high-value transfers
  3.0-3.9: Suitable for medium-value with monitoring
  2.0-2.9: Use with caution, implement rate limits
  < 2.0: Do not use for production
```

### Bridge Comparison (Assessment Template)

| Criterion | LayerZero V2 | Wormhole | IBC | Chainlink CCIP |
|-----------|-------------|----------|-----|----------------|
| Trust model | Configurable DVN | 13/19 Guardians | Light client | Oracle network |
| Validator count | User-chosen | 19 Guardians | Per-chain | Chainlink nodes |
| Past exploits | None (V2) | $326M (V1, 2022) | None major | None |
| Audit count | Multiple | Multiple | Multiple | Multiple |
| Chains supported | 70+ | 30+ | Cosmos ecosystem | 12+ |
| Message type | Arbitrary | Arbitrary + tokens | Arbitrary + tokens | Arbitrary + tokens |

---

## Testing Cross-Chain Transactions

### Local Testing with Forks

```typescript
// Hardhat fork testing for cross-chain
import { ethers } from 'hardhat';

describe('Cross-chain bridge', () => {
  it('should lock tokens on source chain', async () => {
    // Fork Ethereum mainnet
    await network.provider.request({
      method: 'hardhat_reset',
      params: [{
        forking: {
          jsonRpcUrl: process.env.ETH_RPC_URL,
          blockNumber: 19000000,
        },
      }],
    });

    // Test lock transaction on source chain
    const bridge = await ethers.getContractAt('Bridge', BRIDGE_ADDRESS);
    await bridge.lock(TOKEN, AMOUNT, DST_CHAIN_ID);
    // Verify tokens are locked
  });
});
```

### Testnet Integration Testing

```text
Cross-chain test workflow:
  1. Deploy contracts on source testnet (e.g., Sepolia)
  2. Deploy contracts on destination testnet (e.g., Mumbai)
  3. Configure bridge endpoints and trust settings
  4. Execute cross-chain transaction
  5. Wait for message delivery (minutes to hours on testnet)
  6. Verify state on destination chain
  7. Test failure scenarios (timeout, invalid proof)
```

### LayerZero Testing

```bash
# LayerZero testnet configuration
npx hardhat lz:test:run  # Run cross-chain tests

# LayerZero simulation (local, no testnet needed)
# Uses @layerzerolabs/test-devtools-evm-hardhat
npx hardhat test --network hardhat  # Simulated endpoints
```

### Testing Checklist

- [ ] Happy path: message sent and received correctly
- [ ] Replay protection: same message cannot be processed twice
- [ ] Invalid source: message from unauthorized sender rejected
- [ ] Timeout handling: expired messages handled gracefully
- [ ] Gas estimation: sufficient gas for destination execution
- [ ] Partial failure: source succeeds but destination fails
- [ ] Rate limiting: high-value transfers throttled correctly
- [ ] Upgrade: bridge contracts upgradeable without breaking messages in flight

---

## Anti-Patterns

### 1. Trusting a Single Bridge

**Problem**: All cross-chain traffic goes through one bridge. If it is compromised, everything is lost.

**Fix**: Use multiple bridges for redundancy. Consider bridge aggregators.

### 2. No Rate Limiting on Bridge Transfers

**Problem**: An exploit can drain the entire bridge TVL in a single transaction.

**Fix**: Implement per-transaction limits, daily limits, and circuit breakers that pause on anomalous activity.

### 3. Ignoring Message Ordering

**Problem**: Assuming messages arrive in order. Out-of-order delivery causes state inconsistency.

**Fix**: Use sequence numbers or idempotent message handling.

### 4. Hardcoding Bridge Addresses

**Problem**: Cannot upgrade or switch bridges if the address is hardcoded.

**Fix**: Use a registry pattern or upgradeable configuration for bridge addresses.

### 5. No Timeout Handling

**Problem**: Cross-chain message fails silently. User's tokens are locked on source but never minted on destination.

**Fix**: Implement timeout mechanisms with refund paths. All bridge messages must have an expiry.

---

## Cross-References

- [blockchain-best-practices.md](blockchain-best-practices.md) -- Universal blockchain security patterns
- [solidity-best-practices.md](solidity-best-practices.md) -- Solidity/EVM patterns for bridge contracts
- [cosmwasm-best-practices.md](cosmwasm-best-practices.md) -- CosmWasm IBC patterns
- [defi-protocol-patterns.md](defi-protocol-patterns.md) -- DeFi composability across chains
- [nft-token-standards.md](nft-token-standards.md) -- Cross-chain token standards (OFT, ONFT)
