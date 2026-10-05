# CosmWasm Contract Template — 3.0 API Boundary

Use this baseline only after checking the target chain's supported CosmWasm VM and feature flags. A library update does not prove that a chain supports new host functions. For an existing contract, follow both the 1.5 → 2 and 2 → 3 steps in the [official migration guide](https://cosmwasm.github.io/core/migrating).

## Project and Dependencies

Start from [cw-template](https://github.com/CosmWasm/cw-template) to retain its build/schema layout, then review its dependency graph: the upstream template may target an older major. The manifest below selects the 3.0.x API family; resolve compatible patches, generate `Cargo.lock` with `cargo generate-lockfile`, commit it, and review that lockfile before release. These ranges express an API boundary, not a claim about the newest version.

```toml
[package]
name = "my-contract"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib", "rlib"]

[profile.release]
lto = true
codegen-units = 1
panic = "abort"
overflow-checks = true

[dependencies]
cosmwasm-std = "~3.0"
cosmwasm-schema = "~3.0"
cw-storage-plus = "~3.0"
serde = { version = "1", default-features = false, features = ["derive"] }

[dev-dependencies]
cw-multi-test = "~3.0"
```

Use `cw-storage-plus::Item`/`Map` for storage. If migration/version metadata is needed, add a compatible `cw2` release and validate the allowed source versions before changing state. Keep schema macros in normal dependencies when runtime message types use them.

CosmWasm 3 removes deprecated binary JSON helpers: use `to_json_binary` and `from_json`. `StdError` changed; use `StdResult`/`StdError::msg` for this small contract instead of copying an older `thiserror` conversion. Contracts disabling default features must explicitly enable `exports`.

## Minimal Counter (`src/lib.rs`)

This example implements initialization, public increment, owner-only reset, and query. It deliberately exposes no transfer or migration message without an implementation.

```rust
use cosmwasm_schema::cw_serde;
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env,
    MessageInfo, Response, StdError, StdResult,
};
use cw_storage_plus::Item;

#[cw_serde]
pub struct InstantiateMsg { pub count: i32 }
#[cw_serde]
pub enum ExecuteMsg { Increment {}, Reset { count: i32 } }
#[cw_serde]
pub enum QueryMsg { GetCount {} }
#[cw_serde]
pub struct CountResponse { pub count: i32 }
#[cw_serde]
pub struct State { pub count: i32, pub owner: Addr }
const CONFIG: Item<State> = Item::new("config");

#[entry_point]
pub fn instantiate(
    deps: DepsMut, _env: Env, info: MessageInfo, msg: InstantiateMsg,
) -> StdResult<Response> {
    CONFIG.save(deps.storage, &State { count: msg.count, owner: info.sender })?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(
    deps: DepsMut, _env: Env, info: MessageInfo, msg: ExecuteMsg,
) -> StdResult<Response> {
    CONFIG.update(deps.storage, |mut state| -> StdResult<State> {
        match msg {
            ExecuteMsg::Increment {} => {
                state.count = state.count.checked_add(1)
                    .ok_or_else(|| StdError::msg("count overflow"))?;
            }
            ExecuteMsg::Reset { count } => {
                if info.sender != state.owner {
                    return Err(StdError::msg("unauthorized reset"));
                }
                state.count = count;
            }
        }
        Ok(state)
    })?;
    Ok(Response::new().add_attribute("action", "update_count"))
}

#[entry_point]
pub fn query(deps: Deps, _env: Env, _msg: QueryMsg) -> StdResult<Binary> {
    to_json_binary(&CountResponse { count: CONFIG.load(deps.storage)?.count })
}
```

## Unit and Integration Tests

Generate valid Bech32 addresses with `MockApi::addr_make`; arbitrary strings passed to `Addr::unchecked` do not exercise address validation. Construct `MessageInfo` directly for these tests.

Append to `src/lib.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use cosmwasm_std::testing::{mock_dependencies, mock_env};
    use cosmwasm_std::from_json;

    #[test]
    fn increment_and_owner_reset() {
        let mut deps = mock_dependencies();
        let owner = deps.api.addr_make("owner");
        let other = deps.api.addr_make("other");
        let owner_info = MessageInfo { sender: owner, funds: vec![] };
        let other_info = MessageInfo { sender: other, funds: vec![] };
        instantiate(deps.as_mut(), mock_env(), owner_info.clone(),
            InstantiateMsg { count: 17 }).unwrap();
        execute(deps.as_mut(), mock_env(), other_info.clone(),
            ExecuteMsg::Increment {}).unwrap();
        let value: CountResponse = from_json(query(deps.as_ref(), mock_env(),
            QueryMsg::GetCount {}).unwrap()).unwrap();
        assert_eq!(value.count, 18);
        assert!(execute(deps.as_mut(), mock_env(), other_info,
            ExecuteMsg::Reset { count: 0 }).is_err());
        execute(deps.as_mut(), mock_env(), owner_info,
            ExecuteMsg::Reset { count: i32::MAX }).unwrap();
        let info = MessageInfo { sender: deps.api.addr_make("other"), funds: vec![] };
        assert!(execute(deps.as_mut(), mock_env(), info,
            ExecuteMsg::Increment {}).is_err());
        assert_eq!(CONFIG.load(deps.as_ref().storage).unwrap().count, i32::MAX);
    }
}
```

```bash
cargo test --locked
cargo clippy --locked -- -D warnings
cargo fmt --check
rustup target add wasm32-unknown-unknown
cargo build --locked --release --target wasm32-unknown-unknown
```

Add `cw-multi-test::ContractWrapper` integration tests for bank/CW20 transfers, replies, and cross-contract failures when those capabilities are introduced. Add migration tests with an allowed source version and rejected wrong-version/wrong-contract cases before making a contract upgradeable. Unit tests do not prove gas/VM behavior on the destination chain.

## Build and Deployment Gates

Read [optimizer releases and usage](https://github.com/CosmWasm/optimizer) to select a reviewed image digest compatible with the compiler and target chain. Do not copy a stale image tag from a tutorial. Record the optimized Wasm checksum, schema, exact Rust/dependency toolchain, and VM features.

Obtain the chain ID, live RPC, denomination, gas policy, CLI syntax, and signer requirements from the target chain's official docs. Abort when any are missing. Submit store/instantiate transactions on testnet, wait for successful inclusion, and extract code ID/contract address from that transaction's typed result or events; never guess from the last globally listed contract or event position. Reconcile the checksum and instantiated code ID before execution.

For CosmJS, load signer material from an authorized secrets provider and require explicit endpoint/gas configuration. Catching an upload/instantiate/execute exception must set a nonzero process exit status. Choose migration admin custody before instantiate; `--no-admin` makes a contract immutable and conflicts with a later migration plan.

## Sources

- [CosmWasm migration guide](https://cosmwasm.github.io/core/migrating): 3.0 API and error/serialization changes.
- [cw-multi-test manifest](https://github.com/CosmWasm/cw-multi-test/blob/main/Cargo.toml): compatible CosmWasm/storage families; re-check before resolving patches.
- [CosmWasm mock API source](https://github.com/CosmWasm/cosmwasm/blob/v3.0.2/packages/std/src/testing/mock.rs): valid address generation, read at the named historical tag.
- [cw2](https://docs.rs/cw2/): version metadata and migration helpers.
- [CosmJS](https://cosmos.github.io/cosmjs/): upload, instantiate, query, and execute APIs.
