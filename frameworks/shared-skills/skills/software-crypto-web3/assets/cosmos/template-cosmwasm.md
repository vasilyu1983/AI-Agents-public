# CosmWasm Smart Contract Development Template

Production-grade smart contract development for the Cosmos ecosystem using CosmWasm and Rust.

---

## Project Overview

This template provides a complete development environment for building, testing, and deploying CosmWasm smart contracts using:

- **CosmWasm** - Smart contract platform for Cosmos
- **Rust** - Systems programming language
- **cargo-generate** - Project scaffolding
- **cw-multi-test** - Multi-contract testing
- **CosmJS** - JavaScript library for Cosmos

**Use cases:** DeFi protocols, DAOs, NFT marketplaces, governance systems, IBC-enabled contracts

---

## Project Structure

```
cosmwasm-contract/
├── src/
│   ├── contract.rs          # Entry points (instantiate, execute, query, migrate)
│   ├── state.rs             # State definitions and storage
│   ├── msg.rs               # Message types (Instantiate, Execute, Query)
│   ├── error.rs             # Custom error types
│   ├── helpers.rs           # Utility functions
│   └── lib.rs               # Library exports
├── examples/
│   └── schema.rs            # JSON schema generator
├── tests/
│   ├── integration.rs       # Integration tests with cw-multi-test
│   └── helpers/
│       └── mock.rs          # Mock contracts and helpers
├── schema/                  # Generated JSON schemas
│   ├── instantiate_msg.json
│   ├── execute_msg.json
│   ├── query_msg.json
│   └── state.json
├── Cargo.toml
├── .cargo/
│   └── config             # Cargo configuration
└── README.md
```

---

## Environment Setup

### 1. Install Prerequisites

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
rustup target add wasm32-unknown-unknown

# Install cargo-generate (for project templates)
cargo install cargo-generate --features vendored-openssl

# Install cargo-run-script (for custom scripts)
cargo install cargo-run-script
```

### 2. Create New Project

```bash
# Using CosmWasm template
cargo generate --git https://github.com/CosmWasm/cw-template.git --name my-contract
cd my-contract

# Or manually create project
cargo new --lib my-contract
cd my-contract
```

### 3. Configure Cargo.toml

**Cargo.toml:**
```toml
[package]
name = "my-contract"
version = "0.1.0"
authors = ["Your Name <your.email@example.com>"]
edition = "2021"

[lib]
crate-type = ["cdylib", "rlib"]

[profile.release]
opt-level = 3
debug = false
rpath = false
lto = true
debug-assertions = false
codegen-units = 1
panic = 'abort'
incremental = false
overflow-checks = true

[features]
# Use library feature to disable all instantiate/execute/query exports
library = []

[dependencies]
cosmwasm-std = "1.5"
cosmwasm-storage = "1.5"
cw-storage-plus = "1.2"
cw2 = "1.1"
schemars = "0.8"
serde = { version = "1.0", default-features = false, features = ["derive"] }
thiserror = "1.0"

[dev-dependencies]
cw-multi-test = "0.20"
cosmwasm-schema = "1.5"
```

---

## Basic Contract Implementation

### Entry Points (contract.rs)

```rust
use cosmwasm_std::{
    entry_point, to_binary, Binary, Deps, DepsMut, Env, MessageInfo,
    Response, StdResult,
};

use crate::error::ContractError;
use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg, CountResponse};
use crate::state::{State, CONFIG};

// Version info for migration
const CONTRACT_NAME: &str = "crates.io:my-contract";
const CONTRACT_VERSION: &str = env!("CARGO_PKG_VERSION");

#[entry_point]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: InstantiateMsg,
) -> Result<Response, ContractError> {
    // Set contract version for migration
    cw2::set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;

    let state = State {
        count: msg.count,
        owner: info.sender.clone(),
    };

    CONFIG.save(deps.storage, &state)?;

    Ok(Response::new()
        .add_attribute("method", "instantiate")
        .add_attribute("owner", info.sender)
        .add_attribute("count", msg.count.to_string()))
}

#[entry_point]
pub fn execute(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: ExecuteMsg,
) -> Result<Response, ContractError> {
    match msg {
        ExecuteMsg::Increment {} => execute_increment(deps),
        ExecuteMsg::Reset { count } => execute_reset(deps, info, count),
        ExecuteMsg::Transfer { recipient, amount } => {
            execute_transfer(deps, info, recipient, amount)
        }
    }
}

#[entry_point]
pub fn query(deps: Deps, _env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::GetCount {} => to_binary(&query_count(deps)?),
        QueryMsg::GetOwner {} => to_binary(&query_owner(deps)?),
    }
}

#[entry_point]
pub fn migrate(deps: DepsMut, _env: Env, _msg: MigrateMsg) -> Result<Response, ContractError> {
    // Perform migration logic here
    let version = cw2::get_contract_version(deps.storage)?;
    if version.contract != CONTRACT_NAME {
        return Err(ContractError::InvalidContractName {
            name: version.contract,
        });
    }

    cw2::set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;

    Ok(Response::new()
        .add_attribute("method", "migrate")
        .add_attribute("new_version", CONTRACT_VERSION))
}

// Execute handlers
pub fn execute_increment(deps: DepsMut) -> Result<Response, ContractError> {
    CONFIG.update(deps.storage, |mut state| -> Result<_, ContractError> {
        state.count += 1;
        Ok(state)
    })?;

    Ok(Response::new().add_attribute("action", "increment"))
}

pub fn execute_reset(
    deps: DepsMut,
    info: MessageInfo,
    count: i32,
) -> Result<Response, ContractError> {
    CONFIG.update(deps.storage, |mut state| -> Result<_, ContractError> {
        if info.sender != state.owner {
            return Err(ContractError::Unauthorized {});
        }
        state.count = count;
        Ok(state)
    })?;

    Ok(Response::new()
        .add_attribute("action", "reset")
        .add_attribute("count", count.to_string()))
}

// Query handlers
fn query_count(deps: Deps) -> StdResult<CountResponse> {
    let state = CONFIG.load(deps.storage)?;
    Ok(CountResponse { count: state.count })
}

fn query_owner(deps: Deps) -> StdResult<OwnerResponse> {
    let state = CONFIG.load(deps.storage)?;
    Ok(OwnerResponse {
        owner: state.owner.to_string(),
    })
}
```

### Message Types (msg.rs)

```rust
use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::Uint128;

#[cw_serde]
pub struct InstantiateMsg {
    pub count: i32,
}

#[cw_serde]
pub enum ExecuteMsg {
    Increment {},
    Reset { count: i32 },
    Transfer { recipient: String, amount: Uint128 },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(CountResponse)]
    GetCount {},
    #[returns(OwnerResponse)]
    GetOwner {},
}

#[cw_serde]
pub struct CountResponse {
    pub count: i32,
}

#[cw_serde]
pub struct OwnerResponse {
    pub owner: String,
}

#[cw_serde]
pub struct MigrateMsg {}
```

### State Management (state.rs)

```rust
use cosmwasm_schema::cw_serde;
use cosmwasm_std::Addr;
use cw_storage_plus::Item;

#[cw_serde]
pub struct State {
    pub count: i32,
    pub owner: Addr,
}

pub const CONFIG: Item<State> = Item::new("config");
```

### Error Handling (error.rs)

```rust
use cosmwasm_std::StdError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ContractError {
    #[error("{0}")]
    Std(#[from] StdError),

    #[error("Unauthorized")]
    Unauthorized {},

    #[error("Invalid contract name: {name}")]
    InvalidContractName { name: String },

    #[error("Semver parsing error: {0}")]
    SemVer(String),
}

impl From<semver::Error> for ContractError {
    fn from(err: semver::Error) -> Self {
        Self::SemVer(err.to_string())
    }
}
```

---

## Testing

### Unit Tests (contract.rs)

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use cosmwasm_std::testing::{mock_dependencies, mock_env, mock_info};
    use cosmwasm_std::{coins, from_binary};

    #[test]
    fn proper_initialization() {
        let mut deps = mock_dependencies();

        let msg = InstantiateMsg { count: 17 };
        let info = mock_info("creator", &coins(1000, "earth"));

        let res = instantiate(deps.as_mut(), mock_env(), info, msg).unwrap();
        assert_eq!(0, res.messages.len());

        // Query count
        let res = query(deps.as_ref(), mock_env(), QueryMsg::GetCount {}).unwrap();
        let value: CountResponse = from_binary(&res).unwrap();
        assert_eq!(17, value.count);
    }

    #[test]
    fn increment() {
        let mut deps = mock_dependencies();

        let msg = InstantiateMsg { count: 17 };
        let info = mock_info("creator", &coins(2, "token"));
        let _res = instantiate(deps.as_mut(), mock_env(), info, msg).unwrap();

        // Increment
        let info = mock_info("anyone", &coins(2, "token"));
        let msg = ExecuteMsg::Increment {};
        let _res = execute(deps.as_mut(), mock_env(), info, msg).unwrap();

        // Verify
        let res = query(deps.as_ref(), mock_env(), QueryMsg::GetCount {}).unwrap();
        let value: CountResponse = from_binary(&res).unwrap();
        assert_eq!(18, value.count);
    }

    #[test]
    fn reset() {
        let mut deps = mock_dependencies();

        let msg = InstantiateMsg { count: 17 };
        let info = mock_info("creator", &coins(2, "token"));
        let _res = instantiate(deps.as_mut(), mock_env(), info, msg).unwrap();

        // Reset as owner
        let info = mock_info("creator", &coins(2, "token"));
        let msg = ExecuteMsg::Reset { count: 5 };
        let _res = execute(deps.as_mut(), mock_env(), info, msg).unwrap();

        // Verify
        let res = query(deps.as_ref(), mock_env(), QueryMsg::GetCount {}).unwrap();
        let value: CountResponse = from_binary(&res).unwrap();
        assert_eq!(5, value.count);
    }

    #[test]
    fn unauthorized_reset() {
        let mut deps = mock_dependencies();

        let msg = InstantiateMsg { count: 17 };
        let info = mock_info("creator", &coins(2, "token"));
        let _res = instantiate(deps.as_mut(), mock_env(), info, msg).unwrap();

        // Unauthorized reset
        let info = mock_info("anyone", &coins(2, "token"));
        let msg = ExecuteMsg::Reset { count: 5 };
        let res = execute(deps.as_mut(), mock_env(), info, msg);

        match res {
            Err(ContractError::Unauthorized {}) => {}
            _ => panic!("Must return unauthorized error"),
        }
    }
}
```

### Integration Tests (tests/integration.rs)

```rust
use cosmwasm_std::{Addr, Coin, Empty, Uint128};
use cw_multi_test::{App, AppBuilder, Contract, ContractWrapper, Executor};

use my_contract::msg::{CountResponse, ExecuteMsg, InstantiateMsg, QueryMsg};

pub fn contract_template() -> Box<dyn Contract<Empty>> {
    let contract = ContractWrapper::new(
        my_contract::contract::execute,
        my_contract::contract::instantiate,
        my_contract::contract::query,
    )
    .with_migrate(my_contract::contract::migrate);
    Box::new(contract)
}

const USER: &str = "user";
const ADMIN: &str = "admin";
const NATIVE_DENOM: &str = "denom";

fn mock_app() -> App {
    AppBuilder::new().build(|router, _, storage| {
        router
            .bank
            .init_balance(
                storage,
                &Addr::unchecked(USER),
                vec![Coin {
                    denom: NATIVE_DENOM.to_string(),
                    amount: Uint128::new(1000),
                }],
            )
            .unwrap();
    })
}

fn proper_instantiate() -> (App, Addr) {
    let mut app = mock_app();
    let code_id = app.store_code(contract_template());

    let msg = InstantiateMsg { count: 1 };
    let contract_addr = app
        .instantiate_contract(
            code_id,
            Addr::unchecked(ADMIN),
            &msg,
            &[],
            "test",
            None,
        )
        .unwrap();

    (app, contract_addr)
}

#[test]
fn count() {
    let (mut app, contract_addr) = proper_instantiate();

    let msg = ExecuteMsg::Increment {};
    let cosmos_msg = my_contract::msg::ExecuteMsg::Increment {};
    app.execute_contract(Addr::unchecked(USER), contract_addr.clone(), &cosmos_msg, &[])
        .unwrap();

    let res: CountResponse = app
        .wrap()
        .query_wasm_smart(contract_addr, &QueryMsg::GetCount {})
        .unwrap();

    assert_eq!(res.count, 2);
}

#[test]
fn reset() {
    let (mut app, contract_addr) = proper_instantiate();

    let msg = ExecuteMsg::Reset { count: 5 };
    app.execute_contract(Addr::unchecked(ADMIN), contract_addr.clone(), &msg, &[])
        .unwrap();

    let res: CountResponse = app
        .wrap()
        .query_wasm_smart(contract_addr, &QueryMsg::GetCount {})
        .unwrap();

    assert_eq!(res.count, 5);
}
```

---

## Building and Deployment

### Build Contract

```bash
# Optimize for production
docker run --rm -v "$(pwd)":/code \
  --mount type=volume,source="$(basename "$(pwd)")_cache",target=/code/target \
  --mount type=volume,source=registry_cache,target=/usr/local/cargo/registry \
  cosmwasm/rust-optimizer:0.15.0

# This produces optimized wasm in ./artifacts/
```

### Deploy to Testnet

```bash
# Set up wasmd CLI
CHAIN_ID="uni-6"
TESTNET_NAME="uni-6"
RPC="https://rpc.uni.junomint.com:443"
TXFLAG="--chain-id ${CHAIN_ID} --gas-prices 0.025ujunox --gas auto --gas-adjustment 1.3"

# Store contract
RES=$(junod tx wasm store artifacts/my_contract.wasm --from wallet $TXFLAG -y --output json -b block)
CODE_ID=$(echo $RES | jq -r '.logs[0].events[-1].attributes[0].value')

echo "Code ID: $CODE_ID"

# Instantiate contract
INIT='{"count":100}'
junod tx wasm instantiate $CODE_ID "$INIT" \
    --from wallet --label "my contract" $TXFLAG -y --no-admin

# Get contract address
CONTRACT=$(junod query wasm list-contract-by-code $CODE_ID --output json | jq -r '.contracts[-1]')
echo "Contract address: $CONTRACT"

# Query contract
junod query wasm contract-state smart $CONTRACT '{"get_count":{}}'

# Execute contract
junod tx wasm execute $CONTRACT '{"increment":{}}' \
    --from wallet $TXFLAG -y
```

---

## CosmJS Client Integration

### TypeScript Client

```typescript
import { SigningCosmWasmClient } from "@cosmjs/cosmwasm-stargate";
import { DirectSecp256k1HdWallet } from "@cosmjs/proto-signing";
import { GasPrice } from "@cosmjs/stargate";
import fs from "fs";

const RPC_ENDPOINT = "https://rpc.uni.junomint.com:443";
const MNEMONIC = "your mnemonic here"; // NEVER commit this

async function main() {
  // Create wallet from mnemonic
  const wallet = await DirectSecp256k1HdWallet.fromMnemonic(MNEMONIC, {
    prefix: "juno",
  });

  const [account] = await wallet.getAccounts();
  console.log("Wallet address:", account.address);

  // Connect to chain
  const client = await SigningCosmWasmClient.connectWithSigner(
    RPC_ENDPOINT,
    wallet,
    {
      gasPrice: GasPrice.fromString("0.025ujunox"),
    }
  );

  // Upload contract
  const wasmCode = fs.readFileSync("./artifacts/my_contract.wasm");
  const uploadResult = await client.upload(
    account.address,
    wasmCode,
    "auto"
  );
  console.log("Code ID:", uploadResult.codeId);

  // Instantiate contract
  const instantiateMsg = { count: 100 };
  const instantiateResult = await client.instantiate(
    account.address,
    uploadResult.codeId,
    instantiateMsg,
    "My Contract",
    "auto"
  );
  console.log("Contract address:", instantiateResult.contractAddress);

  // Query contract
  const queryResult = await client.queryContractSmart(
    instantiateResult.contractAddress,
    { get_count: {} }
  );
  console.log("Count:", queryResult.count);

  // Execute contract
  const executeMsg = { increment: {} };
  const executeResult = await client.execute(
    account.address,
    instantiateResult.contractAddress,
    executeMsg,
    "auto"
  );
  console.log("Transaction hash:", executeResult.transactionHash);
}

main().catch(console.error);
```

---

## Useful Commands

### Development

```bash
# Build contract
cargo build

# Run tests
cargo test

# Run clippy
cargo clippy -- -D warnings

# Format code
cargo fmt

# Generate schema
cargo run --example schema

# Check wasm size
ls -lh target/wasm32-unknown-unknown/release/*.wasm
```

### Optimization

```bash
# Using rust-optimizer (recommended)
docker run --rm -v "$(pwd)":/code \
  --mount type=volume,source="$(basename "$(pwd)")_cache",target=/code/target \
  --mount type=volume,source=registry_cache,target=/usr/local/cargo/registry \
  cosmwasm/rust-optimizer:0.15.0

# Using workspace-optimizer (for workspaces)
docker run --rm -v "$(pwd)":/code \
  --mount type=volume,source="$(basename "$(pwd)")_cache",target=/code/target \
  --mount type=volume,source=registry_cache,target=/usr/local/cargo/registry \
  cosmwasm/workspace-optimizer:0.15.0
```

---

## Production Checklist

Before deploying to mainnet:

**Security:**
- [ ] All addresses validated with `addr_validate()`
- [ ] Checked arithmetic (Uint128/Decimal)
- [ ] Custom errors for all failure cases
- [ ] Access control on privileged functions
- [ ] No state changes in query functions
- [ ] Migration function secured
- [ ] Professional security audit completed

**Testing:**
- [ ] 100% unit test coverage
- [ ] Integration tests with cw-multi-test
- [ ] Negative test cases
- [ ] Migration tests
- [ ] Gas benchmarks documented

**Deployment:**
- [ ] Contract optimized with rust-optimizer
- [ ] Schema generated and documented
- [ ] Admin/migration authority secured
- [ ] Deployment tested on testnet
- [ ] Contract verified on chain explorer

**Documentation:**
- [ ] README with usage instructions
- [ ] API documentation
- [ ] Architecture diagram
- [ ] Known limitations documented

---

## Resources

- [CosmWasm Documentation](https://docs.cosmwasm.com/)
- [CosmWasm Book](https://book.cosmwasm.com/)
- [CosmWasm Plus](https://github.com/CosmWasm/cw-plus)
- [CosmWasm Template](https://github.com/CosmWasm/cw-template)
- [CosmJS Documentation](https://cosmos.github.io/cosmjs/)
- [Cosmos SDK](https://docs.cosmos.network/)
- [Juno Network](https://docs.junonetwork.io/)
