# DeFi Protocol Implementation Patterns

Production patterns for building decentralized finance protocols: AMM/DEX, lending, staking, yield farming, flash loans, and oracle integration. Covers both EVM (Solidity) and Solana implementations with security considerations.

---

## Table of Contents

1. [AMM and DEX Patterns](#amm-and-dex-patterns)
2. [Lending Protocol Patterns](#lending-protocol-patterns)
3. [Staking and Reward Distribution](#staking-and-reward-distribution)
4. [Yield Farming and Vault Patterns](#yield-farming-and-vault-patterns)
5. [Flash Loans](#flash-loans)
6. [Oracle Integration](#oracle-integration)
7. [Price Manipulation Prevention](#price-manipulation-prevention)
8. [DeFi Composability and Protocol Risk](#defi-composability-and-protocol-risk)
9. [Anti-Patterns](#anti-patterns)

---

## AMM and DEX Patterns

### Constant Product AMM (Uniswap V2 Model)

The simplest and most widely forked AMM model. The invariant `x * y = k` determines prices.

```solidity
// Core swap logic (simplified Uniswap V2 pattern)
contract ConstantProductAMM {
    IERC20 public tokenA;
    IERC20 public tokenB;
    uint256 public reserveA;
    uint256 public reserveB;

    uint256 private constant FEE_NUMERATOR = 997;    // 0.3% fee
    uint256 private constant FEE_DENOMINATOR = 1000;

    function swap(
        address tokenIn,
        uint256 amountIn
    ) external returns (uint256 amountOut) {
        require(amountIn > 0, "Zero amount");
        require(
            tokenIn == address(tokenA) || tokenIn == address(tokenB),
            "Invalid token"
        );

        bool isTokenA = tokenIn == address(tokenA);
        (uint256 resIn, uint256 resOut) = isTokenA
            ? (reserveA, reserveB)
            : (reserveB, reserveA);

        // Apply fee to input
        uint256 amountInWithFee = amountIn * FEE_NUMERATOR;

        // Constant product formula: amountOut = (resOut * amountInWithFee) /
        //   (resIn * FEE_DENOMINATOR + amountInWithFee)
        amountOut = (resOut * amountInWithFee) /
            (resIn * FEE_DENOMINATOR + amountInWithFee);

        // Update reserves
        if (isTokenA) {
            reserveA += amountIn;
            reserveB -= amountOut;
        } else {
            reserveB += amountIn;
            reserveA -= amountOut;
        }

        // Transfer tokens
        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        IERC20(isTokenA ? address(tokenB) : address(tokenA))
            .transfer(msg.sender, amountOut);
    }
}
```

**Key properties:**

- Price impact increases with trade size relative to pool depth
- Liquidity providers (LPs) earn fees proportional to their share
- Impermanent loss occurs when token prices diverge from deposit ratio
- No oracle dependency -- price is derived from reserves

### Concentrated Liquidity (Uniswap V3 Model)

LPs provide liquidity within specific price ranges (ticks), improving capital efficiency.

```text
Uniswap V3 Key Concepts:
  - Ticks: Discrete price points (each tick = 0.01% price change)
  - Positions: Liquidity deployed between two ticks [tickLower, tickUpper]
  - Active liquidity: Only liquidity in the current price range earns fees
  - Capital efficiency: 100-4000x better than V2 for tight ranges
```

```solidity
// Concentrated liquidity position (simplified)
struct Position {
    uint128 liquidity;
    int24 tickLower;
    int24 tickUpper;
    uint256 feeGrowthInside0Last;
    uint256 feeGrowthInside1Last;
    uint128 tokensOwed0;
    uint128 tokensOwed1;
}

// Price at a given tick
// price = 1.0001^tick
// sqrtPriceX96 = sqrt(1.0001^tick) * 2^96
```

**Design decisions:**

| Decision | V2 Approach | V3 Approach | Tradeoff |
|----------|------------|------------|----------|
| Liquidity range | Full range (0, infinity) | Custom range [a, b] | Higher returns but requires active management |
| LP token | Fungible ERC-20 | Non-fungible ERC-721 | More flexible but harder to compose |
| Fee tiers | Fixed 0.3% | 0.01%, 0.05%, 0.3%, 1% | Better for different pair volatilities |
| Oracle | Cumulative price | Geometric mean TWAP | More manipulation-resistant |

### DEX Router Pattern

```solidity
// Multi-hop swap router (simplified)
contract SwapRouter {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,  // [tokenA, tokenB, tokenC]
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts) {
        require(block.timestamp <= deadline, "Expired");

        // Calculate amounts for each hop
        amounts = getAmountsOut(amountIn, path);
        require(amounts[amounts.length - 1] >= amountOutMin, "Slippage");

        // Execute swaps along the path
        for (uint256 i = 0; i < path.length - 1; i++) {
            _swap(amounts[i], amounts[i + 1], path[i], path[i + 1]);
        }
    }
}
```

---

## Lending Protocol Patterns

### Compound/Aave Lending Model

Core components of a lending protocol:

```text
Lending Protocol Architecture:
  Supply side: Users deposit assets, receive interest-bearing tokens
  Borrow side: Users post collateral, borrow other assets
  Interest rates: Algorithmically determined by utilization
  Liquidation: Undercollateralized positions are liquidated
```

### Collateralization and Health Factor

```solidity
// Health factor calculation (Aave-style)
contract LendingPool {
    // Collateral factor: how much you can borrow against collateral
    // e.g., 0.75 means $100 of ETH collateral -> $75 max borrow
    mapping(address => uint256) public collateralFactor;

    // Liquidation threshold: when position becomes liquidatable
    // e.g., 0.80 means liquidation when borrow/collateral > 80%
    mapping(address => uint256) public liquidationThreshold;

    function healthFactor(address user) public view returns (uint256) {
        uint256 totalCollateralValue = getUserCollateralValue(user);
        uint256 totalBorrowValue = getUserBorrowValue(user);

        if (totalBorrowValue == 0) return type(uint256).max;

        // healthFactor = (collateral * liquidationThreshold) / borrows
        // healthFactor < 1.0 -> liquidatable
        return (totalCollateralValue * liquidationThreshold[user]) /
            totalBorrowValue;
    }
}
```

### Interest Rate Curves

```solidity
// Utilization-based interest rate model
contract InterestRateModel {
    uint256 public baseRate = 2e16;        // 2% base rate
    uint256 public slope1 = 4e16;          // 4% slope below kink
    uint256 public slope2 = 75e16;         // 75% slope above kink (steep)
    uint256 public optimalUtilization = 80e16; // 80% kink point

    function getBorrowRate(
        uint256 totalBorrows,
        uint256 totalSupply
    ) public view returns (uint256) {
        if (totalSupply == 0) return baseRate;

        uint256 utilization = (totalBorrows * 1e18) / totalSupply;

        if (utilization <= optimalUtilization) {
            // Below kink: gentle slope
            return baseRate +
                (utilization * slope1) / optimalUtilization;
        } else {
            // Above kink: steep slope (incentivizes repayment)
            uint256 excessUtilization =
                utilization - optimalUtilization;
            uint256 maxExcess = 1e18 - optimalUtilization;
            return baseRate + slope1 +
                (excessUtilization * slope2) / maxExcess;
        }
    }
}
```

### Liquidation Mechanics

```solidity
// Liquidation function (simplified)
function liquidate(
    address borrower,
    address collateralAsset,
    address debtAsset,
    uint256 debtToCover
) external {
    require(healthFactor(borrower) < 1e18, "Not liquidatable");

    // Liquidator repays debt
    uint256 maxLiquidation = getUserBorrow(borrower, debtAsset) / 2;
    // Close factor: max 50% of position per liquidation
    uint256 actualDebt = debtToCover > maxLiquidation
        ? maxLiquidation
        : debtToCover;

    // Calculate collateral to seize (with liquidation bonus)
    uint256 collateralToSeize = (actualDebt * getPrice(debtAsset) *
        liquidationBonus) / getPrice(collateralAsset);

    // Transfer collateral to liquidator, repay debt
    _repayBorrow(borrower, debtAsset, actualDebt, msg.sender);
    _seizeCollateral(borrower, msg.sender, collateralAsset, collateralToSeize);
}
```

---

## Staking and Reward Distribution

### Time-Weighted Reward Distribution

```solidity
// Synthetix-style staking rewards (industry standard)
contract StakingRewards {
    IERC20 public stakingToken;
    IERC20 public rewardToken;

    uint256 public rewardRate;           // Rewards per second
    uint256 public lastUpdateTime;
    uint256 public rewardPerTokenStored;
    uint256 public totalStaked;

    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;
    mapping(address => uint256) public balances;

    modifier updateReward(address account) {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = block.timestamp;
        if (account != address(0)) {
            rewards[account] = earned(account);
            userRewardPerTokenPaid[account] = rewardPerTokenStored;
        }
        _;
    }

    function rewardPerToken() public view returns (uint256) {
        if (totalStaked == 0) return rewardPerTokenStored;
        return rewardPerTokenStored +
            ((block.timestamp - lastUpdateTime) * rewardRate * 1e18) /
            totalStaked;
    }

    function earned(address account) public view returns (uint256) {
        return (balances[account] *
            (rewardPerToken() - userRewardPerTokenPaid[account])) /
            1e18 + rewards[account];
    }

    function stake(uint256 amount) external updateReward(msg.sender) {
        totalStaked += amount;
        balances[msg.sender] += amount;
        stakingToken.transferFrom(msg.sender, address(this), amount);
    }

    function withdraw(uint256 amount) external updateReward(msg.sender) {
        totalStaked -= amount;
        balances[msg.sender] -= amount;
        stakingToken.transfer(msg.sender, amount);
    }

    function getReward() external updateReward(msg.sender) {
        uint256 reward = rewards[msg.sender];
        rewards[msg.sender] = 0;
        rewardToken.transfer(msg.sender, reward);
    }
}
```

### Epoch-Based Distribution

```text
Epoch-based staking:
  - Rewards distributed per epoch (e.g., weekly)
  - Stake changes take effect next epoch
  - Prevents flash-stake attacks
  - More predictable for users

  Epoch 1: Stake recorded -> Epoch 2: Rewards accrue -> Epoch 3: Claim
```

### Proportional vs Time-Weighted

| Model | When to Use | Advantage | Disadvantage |
|-------|------------|-----------|--------------|
| Proportional (per-block) | Continuous rewards, liquid staking | Simple, fair | Flash-stake vulnerable |
| Epoch-based | Governance, limited reward pools | Flash-stake resistant | Less responsive |
| Time-weighted | Long-term alignment | Rewards loyalty | Complex, lock-up required |
| Vote-escrowed (ve) | Governance power + rewards | Strong alignment | Illiquid, complex |

---

## Yield Farming and Vault Patterns

### ERC-4626 Tokenized Vault

```solidity
// ERC-4626 vault (standard interface for yield-bearing tokens)
import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";

contract YieldVault is ERC4626 {
    constructor(IERC20 asset_)
        ERC4626(asset_)
        ERC20("Vault Shares", "vSHARE")
    {}

    // Total assets managed by the vault
    function totalAssets() public view override returns (uint256) {
        return asset.balanceOf(address(this)) + _getStrategyBalance();
    }

    // Deposit assets, receive shares
    // shares = (assets * totalSupply) / totalAssets
    // Withdraw shares, receive assets
    // assets = (shares * totalAssets) / totalSupply

    function _getStrategyBalance() internal view returns (uint256) {
        // Return balance deployed in yield strategy
        return strategy.balanceOf(address(this));
    }
}
```

### Auto-Compounding Vault Pattern

```text
Auto-compounding vault lifecycle:
  1. User deposits underlying asset
  2. Vault deploys to yield strategy (lending, LP, staking)
  3. Harvester calls harvest() periodically
  4. Harvest: claim rewards -> swap to underlying -> redeposit
  5. Share price increases (same shares, more underlying)
  6. User withdraws more than they deposited
```

### Vault Security Considerations

| Risk | Mitigation |
|------|------------|
| Deposit/withdraw sandwich | Use slippage protection, deadline |
| Share price manipulation | First depositor attack protection (virtual shares) |
| Strategy insolvency | Withdrawal queues, emergency withdrawal |
| Harvest front-running | Private mempool, commit-reveal |
| Reentrancy on deposit/withdraw | ReentrancyGuard, CEI pattern |

---

## Flash Loans

### Mechanics

```solidity
// Flash loan provider (simplified Aave pattern)
contract FlashLoanProvider {
    function flashLoan(
        address receiver,
        address token,
        uint256 amount,
        bytes calldata data
    ) external {
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));

        // Transfer tokens to borrower
        IERC20(token).transfer(receiver, amount);

        // Borrower executes arbitrary logic
        IFlashLoanReceiver(receiver).executeOperation(
            token, amount, _calculateFee(amount), data
        );

        // Verify repayment (amount + fee)
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        require(
            balanceAfter >= balanceBefore + _calculateFee(amount),
            "Flash loan not repaid"
        );
    }
}

// Flash loan receiver interface
interface IFlashLoanReceiver {
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata data
    ) external;
}
```

### Common Flash Loan Use Cases

| Use Case | Description |
|----------|------------|
| Arbitrage | Exploit price differences across DEXes |
| Liquidation | Borrow to liquidate undercollateralized positions |
| Collateral swap | Replace collateral without closing position |
| Self-liquidation | Repay debt to avoid liquidation penalty |
| Governance attacks | Borrow tokens for voting power (mitigate with snapshots) |

### Flash Loan Risk Mitigation

- Use time-weighted voting snapshots (not current balance) for governance
- Require multi-block oracles (TWAP) rather than spot prices
- Implement cooldown periods for large state changes
- Rate-limit liquidations per block

---

## Oracle Integration

### Chainlink Price Feeds

```solidity
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract ChainlinkConsumer {
    AggregatorV3Interface internal priceFeed;
    uint256 private constant STALE_THRESHOLD = 3600; // 1 hour

    constructor(address feedAddress) {
        priceFeed = AggregatorV3Interface(feedAddress);
    }

    function getPrice() public view returns (uint256) {
        (
            uint80 roundId,
            int256 price,
            ,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        // Validation checks (all required)
        require(price > 0, "Invalid price");
        require(updatedAt > 0, "Round not complete");
        require(answeredInRound >= roundId, "Stale round");
        require(
            block.timestamp - updatedAt < STALE_THRESHOLD,
            "Price too old"
        );

        return uint256(price);
    }
}
```

### Pyth Network (Low-Latency)

```solidity
import "@pythnetwork/pyth-sdk-solidity/IPyth.sol";

contract PythConsumer {
    IPyth public pyth;

    function getPrice(bytes32 priceId) public view returns (uint256) {
        PythStructs.Price memory price = pyth.getPriceNoOlderThan(
            priceId,
            60  // max age in seconds
        );

        require(price.price > 0, "Invalid price");

        // Convert from Pyth format (price * 10^expo)
        return uint256(int256(price.price)) *
            10 ** (18 - uint256(int256(-price.expo)));
    }
}
```

### TWAP (Time-Weighted Average Price)

```text
TWAP calculation:
  Accumulate price at each block:
    cumulative_price[t] = cumulative_price[t-1] + price[t]

  TWAP over period:
    twap = (cumulative_price[t2] - cumulative_price[t1]) / (t2 - t1)

  Manipulation resistance:
    - Longer TWAP window = more resistant but less responsive
    - 30-minute TWAP: good balance for most DeFi
    - Short TWAP: vulnerable to multi-block manipulation
```

### Oracle Selection Guide

| Oracle | Latency | Update Model | Best For |
|--------|---------|-------------|----------|
| Chainlink | Seconds-minutes | Push (heartbeat + deviation) | Lending, derivatives |
| Pyth | Sub-second | Pull (on-demand) | Trading, perps |
| Uniswap V3 TWAP | Block-time | On-chain accumulator | Backup oracle, governance |
| Redstone | Configurable | Push or pull | Flexible, multi-chain |

---

## Price Manipulation Prevention

### Common Attack Vectors

| Attack | Mechanism | Mitigation |
|--------|-----------|------------|
| Flash loan + AMM | Borrow large amount, move AMM price, exploit dependent protocol | TWAP oracles, multi-source pricing |
| Sandwich attack | Front-run + back-run a large swap | MEV protection, max slippage |
| Oracle manipulation | Influence oracle price source | Multiple oracles, circuit breakers |
| Donation attack | Donate tokens to inflate share price | Virtual shares, minimum deposit |

### Defense Patterns

```solidity
// Multi-oracle price validation
function getValidatedPrice(address token) internal view returns (uint256) {
    uint256 chainlinkPrice = getChainlinkPrice(token);
    uint256 twapPrice = getTWAPPrice(token);

    // Require oracles agree within 5%
    uint256 deviation = chainlinkPrice > twapPrice
        ? ((chainlinkPrice - twapPrice) * 1e18) / chainlinkPrice
        : ((twapPrice - chainlinkPrice) * 1e18) / twapPrice;

    require(deviation < 5e16, "Oracle price deviation too high");

    return chainlinkPrice; // Use primary oracle when validated
}

// Circuit breaker for extreme price movements
uint256 public lastPrice;
uint256 public constant MAX_PRICE_CHANGE = 20e16; // 20% max change

function checkPriceCircuitBreaker(uint256 newPrice) internal {
    if (lastPrice > 0) {
        uint256 change = newPrice > lastPrice
            ? ((newPrice - lastPrice) * 1e18) / lastPrice
            : ((lastPrice - newPrice) * 1e18) / lastPrice;
        require(change < MAX_PRICE_CHANGE, "Circuit breaker triggered");
    }
    lastPrice = newPrice;
}
```

---

## DeFi Composability and Protocol Risk

### Composability Patterns

```text
DeFi Lego Stack:
  Layer 1: Base assets (ETH, USDC, WBTC)
  Layer 2: Lending (aETH, cUSDC) -- deposit and receive yield tokens
  Layer 3: DEX LP (ETH/USDC LP token) -- provide liquidity
  Layer 4: Yield aggregator (vault share token) -- auto-compound
  Layer 5: Derivatives (leveraged positions, options)

  Each layer adds yield AND risk.
  Failure at any layer cascades upward.
```

### Protocol Risk Assessment

| Risk Type | Description | Mitigation |
|-----------|------------|------------|
| Smart contract risk | Bug in protocol code | Audits, bug bounties, formal verification |
| Oracle risk | Price feed failure or manipulation | Multi-oracle, circuit breakers |
| Governance risk | Malicious governance proposal | Timelocks, veto mechanisms |
| Liquidity risk | Insufficient liquidity for withdrawals | Reserve ratios, withdrawal queues |
| Composability risk | Cascading failures across protocols | Exposure limits, insurance |
| Regulatory risk | Legal action against protocol | Decentralization, legal review |

### Composability Security Checklist

- [ ] External calls to untrusted contracts use CEI pattern
- [ ] Token approvals are limited (not unlimited)
- [ ] Callback functions validate the caller
- [ ] Reentrancy guards on all state-changing functions
- [ ] Slippage protection on all swaps
- [ ] Deadline parameters on time-sensitive operations
- [ ] Price validation from multiple sources

---

## Anti-Patterns

### 1. Spot Price for Valuation

**Problem**: Using AMM spot price for collateral valuation. Easily manipulated with flash loans.

**Fix**: Use TWAP oracles or Chainlink price feeds. Never use `getReserves()` for pricing.

### 2. Unlimited Token Approvals

**Problem**: `approve(spender, type(uint256).max)` means if the spender is compromised, all tokens are at risk.

**Fix**: Approve exact amounts or use permit2 for single-use approvals.

### 3. Missing Slippage Protection

**Problem**: Swap with `amountOutMin = 0` means MEV bots extract maximum value.

**Fix**: Always calculate and enforce minimum output amounts.

### 4. Hardcoded Addresses

**Problem**: Hardcoding token or protocol addresses prevents deployment on other chains.

**Fix**: Use constructor parameters or configuration contracts.

### 5. No Emergency Pause

**Problem**: When a vulnerability is discovered, there is no way to stop the protocol.

**Fix**: Implement Pausable with guardian multisig for emergency stops.

---

## Cross-References

- [blockchain-best-practices.md](blockchain-best-practices.md) -- Universal blockchain security patterns
- [solidity-best-practices.md](solidity-best-practices.md) -- Solidity-specific gas and security patterns
- [../SKILL.md](../SKILL.md) -- DeFi scope, oracle integration, MEV protection
- [../../software-security-appsec/references/smart-contract-security-auditing.md](../../software-security-appsec/references/smart-contract-security-auditing.md) -- Audit workflows
