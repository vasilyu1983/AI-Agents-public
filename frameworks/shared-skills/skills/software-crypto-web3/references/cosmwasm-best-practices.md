# CosmWasm Best Practices - Cosmos Ecosystem Smart Contracts

Production-grade patterns for secure, efficient smart contract development in the Cosmos ecosystem using CosmWasm.

---

## Table of Contents

1. [CosmWasm Architecture](#cosmwasm-architecture)
2. [Contract Structure](#contract-structure)
3. [Message Handling](#message-handling)
4. [State Management](#state-management)
5. [Query Patterns](#query-patterns)
6. [IBC Integration](#ibc-integration)
7. [Error Handling](#error-handling)
8. [Testing Strategies](#testing-strategies)
9. [Gas Optimization](#gas-optimization)
10. [Common Pitfalls](#common-pitfalls)

---

## CosmWasm Architecture

### Actor Model

CosmWasm follows an **actor model** where contracts:
- Receive messages (inputs)
- Update internal state
- Send messages to other contracts
- Return responses

**Key difference from Ethereum:** No reentrancy (messages processed sequentially).

### Contract Lifecycle

```
┌─────────────┐
│  Instantiate│ ──> Initial state setup
└─────────────┘
       │
       ▼
┌─────────────┐
│   Execute   │ ──> State mutations
└─────────────┘
       │
       ▼
┌─────────────┐
│    Query    │ ──> Read-only state access
└─────────────┘
       │
       ▼
┌─────────────┐
│   Migrate   │ ──> Upgrade contract logic
└─────────────┘
```

---

## Contract Structure

### Standard Project Layout

```
cosmwasm-contract/
├── src/
│   ├── contract.rs      # Entry points (instantiate, execute, query)
│   ├── state.rs         # State definitions
│   ├── msg.rs           # Message types
│   ├── error.rs         # Custom errors
│   ├── helpers.rs       # Utility functions
│   └── lib.rs           # Library exports
├── examples/
│   └── schema.rs        # JSON schema generator
├── tests/
│   └── integration.rs   # Integration tests
├── Cargo.toml
└── schema/              # Generated JSON schemas
```

### Entry Points (contract.rs)

```rust
use cosmwasm_std::{
    entry_point, Binary, Deps, DepsMut, Env, MessageInfo, Response, StdResult,
};

use crate::error::ContractError;
use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg};
use crate::state::{State, STATE};

#[entry_point]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: InstantiateMsg,
) -> Result<Response, ContractError> {
    let state = State {
        owner: info.sender.clone(),
        count: msg.count,
    };
    STATE.save(deps.storage, &state)?;

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
        ExecuteMsg::Increment {} => execute_increment(deps, info),
        ExecuteMsg::Reset { count } => execute_reset(deps, info, count),
    }
}

#[entry_point]
pub fn query(deps: Deps, _env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::GetCount {} => to_binary(&query_count(deps)?),
    }
}

#[entry_point]
pub fn migrate(
    _deps: DepsMut,
    _env: Env,
    _msg: MigrateMsg,
) -> Result<Response, ContractError> {
    Ok(Response::default())
}
```

---

## Message Handling

### Message Types (msg.rs)

```rust
use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::Addr;

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
    #[returns(GetCountResponse)]
    GetCount {},
    #[returns(GetBalanceResponse)]
    GetBalance { address: String },
}

#[cw_serde]
pub struct GetCountResponse {
    pub count: i32,
}

#[cw_serde]
pub struct GetBalanceResponse {
    pub balance: Uint128,
}

#[cw_serde]
pub struct MigrateMsg {}
```

### Execute Handlers

```rust
pub fn execute_increment(
    deps: DepsMut,
    _info: MessageInfo,
) -> Result<Response, ContractError> {
    STATE.update(deps.storage, |mut state| -> Result<_, ContractError> {
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
    STATE.update(deps.storage, |mut state| -> Result<_, ContractError> {
        // Access control
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
```

---

## State Management

### State Definition (state.rs)

```rust
use cosmwasm_schema::cw_serde;
use cosmwasm_std::Addr;
use cw_storage_plus::{Item, Map};

#[cw_serde]
pub struct State {
    pub owner: Addr,
    pub count: i32,
}

// Singleton state
pub const STATE: Item<State> = Item::new("state");

// Map: address -> balance
pub const BALANCES: Map<&Addr, Uint128> = Map::new("balances");

// Multi-index map example
use cw_storage_plus::IndexedMap;

pub struct TokenIndexes<'a> {
    pub owner: MultiIndex<'a, Addr, Token, String>,
}

impl<'a> IndexList<Token> for TokenIndexes<'a> {
    fn get_indexes(&'_ self) -> Box<dyn Iterator<Item = &'_ dyn Index<Token>> + '_> {
        let v: Vec<&dyn Index<Token>> = vec![&self.owner];
        Box::new(v.into_iter())
    }
}

pub fn tokens<'a>() -> IndexedMap<'a, &'a str, Token, TokenIndexes<'a>> {
    let indexes = TokenIndexes {
        owner: MultiIndex::new(|d| d.owner.clone(), "tokens", "tokens__owner"),
    };
    IndexedMap::new("tokens", indexes)
}
```

### State Updates

```rust
use cosmwasm_std::{DepsMut, MessageInfo, Response, Uint128};

// GOOD: SECURE: Update with closure
pub fn increase_balance(
    deps: DepsMut,
    info: MessageInfo,
    amount: Uint128,
) -> Result<Response, ContractError> {
    BALANCES.update(
        deps.storage,
        &info.sender,
        |balance: Option<Uint128>| -> StdResult<_> {
            Ok(balance.unwrap_or_default() + amount)
        },
    )?;

    Ok(Response::new())
}

// GOOD: SECURE: Load, modify, save pattern
pub fn decrease_balance(
    deps: DepsMut,
    info: MessageInfo,
    amount: Uint128,
) -> Result<Response, ContractError> {
    let mut balance = BALANCES
        .may_load(deps.storage, &info.sender)?
        .unwrap_or_default();

    if balance < amount {
        return Err(ContractError::InsufficientFunds {});
    }

    balance -= amount;
    BALANCES.save(deps.storage, &info.sender, &balance)?;

    Ok(Response::new())
}
```

---

## Query Patterns

### Simple Query

```rust
use cosmwasm_std::{to_binary, Binary, Deps, StdResult};

pub fn query_count(deps: Deps) -> StdResult<GetCountResponse> {
    let state = STATE.load(deps.storage)?;
    Ok(GetCountResponse { count: state.count })
}

pub fn query_balance(deps: Deps, address: String) -> StdResult<GetBalanceResponse> {
    let addr = deps.api.addr_validate(&address)?;
    let balance = BALANCES
        .may_load(deps.storage, &addr)?
        .unwrap_or_default();
    Ok(GetBalanceResponse { balance })
}
```

### Paginated Query

```rust
use cosmwasm_std::{Deps, Order, StdResult};
use cw_storage_plus::Bound;

const DEFAULT_LIMIT: u32 = 10;
const MAX_LIMIT: u32 = 30;

pub fn query_all_balances(
    deps: Deps,
    start_after: Option<String>,
    limit: Option<u32>,
) -> StdResult<AllBalancesResponse> {
    let limit = limit.unwrap_or(DEFAULT_LIMIT).min(MAX_LIMIT) as usize;
    let start = start_after.map(|s| Bound::exclusive(s.as_str()));

    let balances: StdResult<Vec<_>> = BALANCES
        .range(deps.storage, start, None, Order::Ascending)
        .take(limit)
        .map(|item| {
            let (addr, balance) = item?;
            Ok(BalanceResponse {
                address: addr.to_string(),
                balance,
            })
        })
        .collect();

    Ok(AllBalancesResponse {
        balances: balances?,
    })
}
```

---

## IBC Integration

### IBC Packet Handling

```rust
use cosmwasm_std::{
    entry_point, DepsMut, Env, IbcBasicResponse, IbcChannelCloseMsg,
    IbcChannelConnectMsg, IbcChannelOpenMsg, IbcPacketAckMsg, IbcPacketReceiveMsg,
    IbcPacketTimeoutMsg, IbcReceiveResponse, Never,
};

#[entry_point]
pub fn ibc_channel_open(
    _deps: DepsMut,
    _env: Env,
    msg: IbcChannelOpenMsg,
) -> Result<(), ContractError> {
    // Validate channel parameters
    if msg.channel().version != "ics20-1" {
        return Err(ContractError::InvalidIbcVersion {
            version: msg.channel().version.clone(),
        });
    }
    Ok(())
}

#[entry_point]
pub fn ibc_channel_connect(
    _deps: DepsMut,
    _env: Env,
    _msg: IbcChannelConnectMsg,
) -> Result<IbcBasicResponse, ContractError> {
    Ok(IbcBasicResponse::default())
}

#[entry_point]
pub fn ibc_packet_receive(
    deps: DepsMut,
    _env: Env,
    msg: IbcPacketReceiveMsg,
) -> Result<IbcReceiveResponse, Never> {
    // Parse packet data
    let packet: TransferPacket = from_slice(&msg.packet.data)?;

    // Validate packet
    if packet.amount.is_zero() {
        return Ok(IbcReceiveResponse::new()
            .set_ack(ack_fail("Amount cannot be zero")));
    }

    // Process transfer
    let recipient = deps.api.addr_validate(&packet.recipient)?;
    BALANCES.update(deps.storage, &recipient, |balance| -> StdResult<_> {
        Ok(balance.unwrap_or_default() + packet.amount)
    })?;

    Ok(IbcReceiveResponse::new()
        .set_ack(ack_success())
        .add_attribute("action", "ibc_transfer")
        .add_attribute("recipient", packet.recipient))
}

#[entry_point]
pub fn ibc_packet_ack(
    _deps: DepsMut,
    _env: Env,
    msg: IbcPacketAckMsg,
) -> Result<IbcBasicResponse, ContractError> {
    // Handle acknowledgment
    let ack: Acknowledgement = from_slice(&msg.acknowledgement.data)?;

    if ack.is_error() {
        // Revert local state changes
    }

    Ok(IbcBasicResponse::new())
}
```

---

## Error Handling

### Custom Errors (error.rs)

```rust
use cosmwasm_std::StdError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ContractError {
    #[error("{0}")]
    Std(#[from] StdError),

    #[error("Unauthorized")]
    Unauthorized {},

    #[error("Insufficient funds")]
    InsufficientFunds {},

    #[error("Amount cannot be zero")]
    ZeroAmount {},

    #[error("Invalid IBC version: {version}")]
    InvalidIbcVersion { version: String },

    #[error("Custom Error val: {val:?}")]
    CustomError { val: String },
}
```

### Usage in Handlers

```rust
pub fn execute_transfer(
    deps: DepsMut,
    info: MessageInfo,
    recipient: String,
    amount: Uint128,
) -> Result<Response, ContractError> {
    // Validation
    if amount.is_zero() {
        return Err(ContractError::ZeroAmount {});
    }

    let recipient_addr = deps.api.addr_validate(&recipient)?;

    // Load sender balance
    let sender_balance = BALANCES
        .may_load(deps.storage, &info.sender)?
        .unwrap_or_default();

    // Check sufficient funds
    if sender_balance < amount {
        return Err(ContractError::InsufficientFunds {});
    }

    // Update balances
    BALANCES.save(deps.storage, &info.sender, &(sender_balance - amount))?;
    BALANCES.update(deps.storage, &recipient_addr, |balance| -> StdResult<_> {
        Ok(balance.unwrap_or_default() + amount)
    })?;

    Ok(Response::new()
        .add_attribute("action", "transfer")
        .add_attribute("from", info.sender)
        .add_attribute("to", recipient)
        .add_attribute("amount", amount))
}
```

---

## Testing Strategies

### Unit Tests

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
        let value: GetCountResponse = from_binary(&res).unwrap();
        assert_eq!(17, value.count);
    }

    #[test]
    fn increment() {
        let mut deps = mock_dependencies();

        let msg = InstantiateMsg { count: 17 };
        let info = mock_info("creator", &coins(2, "token"));
        instantiate(deps.as_mut(), mock_env(), info, msg).unwrap();

        // Execute increment
        let info = mock_info("anyone", &coins(2, "token"));
        let msg = ExecuteMsg::Increment {};
        let _res = execute(deps.as_mut(), mock_env(), info, msg).unwrap();

        // Verify
        let res = query(deps.as_ref(), mock_env(), QueryMsg::GetCount {}).unwrap();
        let value: GetCountResponse = from_binary(&res).unwrap();
        assert_eq!(18, value.count);
    }

    #[test]
    fn reset_unauthorized() {
        let mut deps = mock_dependencies();

        let msg = InstantiateMsg { count: 17 };
        let info = mock_info("creator", &coins(2, "token"));
        instantiate(deps.as_mut(), mock_env(), info, msg).unwrap();

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

### Integration Tests (Multi-Contract)

```rust
use cw_multi_test::{App, ContractWrapper, Executor};

#[test]
fn test_multi_contract_interaction() {
    let mut app = App::default();

    // Store contract code
    let code = ContractWrapper::new(execute, instantiate, query);
    let code_id = app.store_code(Box::new(code));

    // Instantiate contract
    let addr = app
        .instantiate_contract(
            code_id,
            Addr::unchecked("owner"),
            &InstantiateMsg { count: 0 },
            &[],
            "counter",
            None,
        )
        .unwrap();

    // Execute
    app.execute_contract(
        Addr::unchecked("user"),
        addr.clone(),
        &ExecuteMsg::Increment {},
        &[],
    )
    .unwrap();

    // Query
    let count: GetCountResponse = app
        .wrap()
        .query_wasm_smart(addr, &QueryMsg::GetCount {})
        .unwrap();

    assert_eq!(count.count, 1);
}
```

---

## Gas Optimization

### Storage Efficiency

```rust
// BAD: WASTEFUL: Storing full struct when only one field changes
#[cw_serde]
pub struct UserData {
    pub name: String,
    pub balance: Uint128,
    pub last_active: u64,
}

pub const USER_DATA: Map<&Addr, UserData> = Map::new("user_data");

// Update only balance (but stores entire struct)
pub fn bad_update(deps: DepsMut, user: &Addr, amount: Uint128) -> StdResult<()> {
    USER_DATA.update(deps.storage, user, |data| -> StdResult<_> {
        let mut data = data.unwrap();
        data.balance += amount;
        Ok(data)
    })?;
    Ok(())
}

// GOOD: OPTIMIZED: Separate frequently-updated data
pub const BALANCES: Map<&Addr, Uint128> = Map::new("balances");
pub const USER_INFO: Map<&Addr, UserInfo> = Map::new("user_info");

#[cw_serde]
pub struct UserInfo {
    pub name: String,
    pub last_active: u64,
}

pub fn good_update(deps: DepsMut, user: &Addr, amount: Uint128) -> StdResult<()> {
    BALANCES.update(deps.storage, user, |balance| -> StdResult<_> {
        Ok(balance.unwrap_or_default() + amount)
    })?;
    Ok(())
}
```

### Minimize Storage Operations

```rust
// BAD: EXPENSIVE: Multiple storage reads/writes
pub fn bad_batch_update(deps: DepsMut, users: Vec<Addr>) -> StdResult<()> {
    for user in users {
        let balance = BALANCES.load(deps.storage, &user)?;
        BALANCES.save(deps.storage, &user, &(balance + Uint128::new(100)))?;
    }
    Ok(())
}

// GOOD: OPTIMIZED: Batch operations
pub fn good_batch_update(deps: DepsMut, users: Vec<Addr>) -> StdResult<()> {
    for user in users {
        BALANCES.update(deps.storage, &user, |balance| -> StdResult<_> {
            Ok(balance.unwrap_or_default() + Uint128::new(100))
        })?;
    }
    Ok(())
}
```

---

## Common Pitfalls

### Address Validation

```rust
// BAD: VULNERABLE: No address validation
pub fn bad_transfer(
    deps: DepsMut,
    recipient: String,
    amount: Uint128,
) -> Result<Response, ContractError> {
    let recipient = Addr::unchecked(recipient);  // UNSAFE
    BALANCES.save(deps.storage, &recipient, &amount)?;
    Ok(Response::new())
}

// GOOD: SECURE: Validate address
pub fn good_transfer(
    deps: DepsMut,
    recipient: String,
    amount: Uint128,
) -> Result<Response, ContractError> {
    let recipient = deps.api.addr_validate(&recipient)?;  // SAFE
    BALANCES.save(deps.storage, &recipient, &amount)?;
    Ok(Response::new())
}
```

### Integer Overflow

```rust
use cosmwasm_std::Uint128;

// GOOD: SECURE: Use Uint128 (checked arithmetic)
pub fn safe_add(
    deps: DepsMut,
    user: &Addr,
    amount: Uint128,
) -> Result<Response, ContractError> {
    BALANCES.update(deps.storage, user, |balance| -> StdResult<_> {
        Ok(balance.unwrap_or_default() + amount)  // Panics on overflow
    })?;
    Ok(Response::new())
}

// For explicit error handling:
pub fn safe_add_with_check(
    deps: DepsMut,
    user: &Addr,
    amount: Uint128,
) -> Result<Response, ContractError> {
    BALANCES.update(deps.storage, user, |balance| -> Result<_, ContractError> {
        let balance = balance.unwrap_or_default();
        balance
            .checked_add(amount)
            .ok_or(ContractError::Overflow {})
    })?;
    Ok(Response::new())
}
```

### Query Side Effects

```rust
// BAD: VULNERABLE: Query modifies state
pub fn bad_query(deps: DepsMut) -> StdResult<GetCountResponse> {
    STATE.update(deps.storage, |mut state| -> StdResult<_> {
        state.count += 1;  // WRONG: Queries should not modify state
        Ok(state)
    })?;
    let state = STATE.load(deps.storage)?;
    Ok(GetCountResponse { count: state.count })
}

// GOOD: SECURE: Query is read-only
pub fn good_query(deps: Deps) -> StdResult<GetCountResponse> {
    let state = STATE.load(deps.storage)?;
    Ok(GetCountResponse { count: state.count })
}
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
- [ ] IBC packet validation
- [ ] Professional security audit completed

**Testing:**
- [ ] 100% unit test coverage
- [ ] Integration tests with cw-multi-test
- [ ] Negative test cases
- [ ] Gas benchmarks documented

**Deployment:**
- [ ] Contract verified on chain explorer
- [ ] Admin/migration authority secured
- [ ] Monitoring and alerting configured
- [ ] Emergency pause mechanism

**Documentation:**
- [ ] JSON schemas generated
- [ ] README with usage instructions
- [ ] API documentation
- [ ] Known limitations documented

---

## Resources

- [CosmWasm Documentation](https://docs.cosmwasm.com/)
- [CosmWasm Book](https://book.cosmwasm.com/)
- [CosmWasm Plus](https://github.com/CosmWasm/cw-plus)
- [CosmWasm Template](https://github.com/CosmWasm/cw-template)
- [Cosmos SDK Documentation](https://docs.cosmos.network/)
- [IBC Protocol](https://ibc.cosmos.network/)
