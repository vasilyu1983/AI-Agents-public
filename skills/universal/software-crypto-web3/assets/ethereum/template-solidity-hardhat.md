# Ethereum Development — Hardhat 3 Template

Use the Ethers/Mocha toolbox when porting a TypeScript/Ethers workflow. Hardhat 3 uses ESM, explicit plugin registration, and a network connection that owns its Ethers instance. Preserve the initializer's package and TypeScript configuration.

## Setup

Check [supported Node releases](https://hardhat.org/docs/reference/nodejs-support) and [initialization](https://hardhat.org/docs/getting-started) before installing; pin the resolved toolchain and commit its lockfile.

```bash
mkdir my-hardhat-project
cd my-hardhat-project
npx hardhat --init
```

Select **A TypeScript Hardhat project using Mocha and Ethers.js**. Add `@openzeppelin/contracts` to implement standard tokens; review its matching major-version API before copying contract code. Keep `"type": "module"` in `package.json`.

## Configuration

Choose an exact compiler from [Solidity releases](https://github.com/ethereum/solidity/releases), check its [known bugs](https://docs.soliditylang.org/en/latest/bugs.html), and set `SOLC_VERSION` to that exact version. Match every pragma and the target chain's EVM support. `SOLC_VERSION` is required even for local builds; RPC and signer configuration variables are resolved when the selected network needs them.

**hardhat.config.ts:**
```typescript
import { configVariable, defineConfig } from "hardhat/config";
import hardhatToolboxMochaEthers from "@nomicfoundation/hardhat-toolbox-mocha-ethers";

const solcVersion = process.env.SOLC_VERSION;
if (!solcVersion || !/^\d+\.\d+\.\d+$/.test(solcVersion)) {
  throw new Error("SOLC_VERSION must name an exact reviewed compiler release");
}

export default defineConfig({
  plugins: [hardhatToolboxMochaEthers],
  solidity: {
    profiles: {
      default: { version: solcVersion },
      production: {
        version: solcVersion,
        settings: { optimizer: { enabled: true, runs: 200 } },
      },
    },
  },
  networks: {
    hardhatMainnet: { type: "edr-simulated", chainType: "l1" },
    sepolia: {
      type: "http",
      chainType: "l1",
      chainId: 11155111,
      url: configVariable("SEPOLIA_RPC_URL"),
      accounts: [configVariable("SEPOLIA_PRIVATE_KEY")],
    },
  },
  verify: { etherscan: { apiKey: configVariable("ETHERSCAN_API_KEY") } },
});
```

The optimizer count is an example setting, not a universal optimum. Keep mainnet configuration and signing authorization separate from testnet. Use the toolbox's keystore or a secrets provider; do not put production keys in source or shell history.

## Contract and Test

The pragma below is an example floor; the reviewed compiler pin must satisfy it. Add mint/transfer authorization and supply invariants when extending this fixed-supply example.

**contracts/Token.sol:**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    constructor() ERC20("MyToken", "MTK") {
        _mint(msg.sender, 1000 * 10**18);
    }
}
```

**test/Token.ts:**
```typescript
import { expect } from "chai";
import hre from "hardhat";

const { ethers } = await hre.network.create();

describe("MyToken", function () {
  it("mints once and preserves supply across a transfer", async function () {
    const [owner, recipient] = await ethers.getSigners();
    const token = await ethers.deployContract("MyToken");
    expect(await token.balanceOf(owner.address)).to.equal(ethers.parseEther("1000"));
    await token.transfer(recipient.address, ethers.parseEther("50"));
    expect(await token.balanceOf(recipient.address)).to.equal(ethers.parseEther("50"));
    expect(await token.totalSupply()).to.equal(ethers.parseEther("1000"));
  });
});
```

```bash
npx hardhat test
npx hardhat test --coverage
```

Use Hardhat 3's Solidity tests and built-in coverage; consult [gas statistics](https://hardhat.org/docs/guides/testing/gas-statistics) for the installed version's CLI. Do not install legacy gas-reporter/coverage plugins as a default. Coverage is evidence about exercised code, not a security guarantee.

## Deployment and Verification

**scripts/deploy.ts:**
```typescript
import hre from "hardhat";

const { ethers } = await hre.network.create();
const token = await ethers.deployContract("MyToken");
await token.waitForDeployment();
console.log("Token:", await token.getAddress());
```

Build, deploy, and verify with the same production profile so compiler settings match the deployed bytecode. Run deployments only after network, owner, upgrade authority, and simulation checks pass.

```bash
npx hardhat build --build-profile production
npx hardhat run --build-profile production scripts/deploy.ts --network sepolia
```

Install `@nomicfoundation/hardhat-verify` explicitly when importing its programmatic helper (the toolbox includes the plugin but does not re-export that helper).

**scripts/verify.ts:**
```typescript
import hre from "hardhat";
import { verifyContract } from "@nomicfoundation/hardhat-verify/verify";

async function main() {
  const address = process.env.TOKEN_ADDRESS;
  if (!address || !/^0x[0-9a-fA-F]{40}$/.test(address)) {
    throw new Error("TOKEN_ADDRESS must be a deployed contract address");
  }
  await verifyContract({ address, constructorArgs: [], provider: "etherscan" }, hre);
  console.log("Contract verified successfully");
}

main().catch((error) => {
  console.error("Verification failed:", error);
  process.exitCode = 1;
});
```

```bash
npx hardhat run --build-profile production scripts/verify.ts --network sepolia
```

Verification rejection, RPC failure, and malformed input must leave a nonzero exit status. Do not suppress an error by matching its message text. Preserve the deployed address, chain ID, build profile, compiler settings, and transaction receipt for review.

## Sources and Template Checks

- [Ethers/Mocha toolbox](https://hardhat.org/docs/plugins/hardhat-toolbox-mocha-ethers): initializer choice and plugin registration.
- [Configuration](https://hardhat.org/docs/reference/configuration): profiles, typed networks, configuration variables.
- [Ethers tests](https://hardhat.org/docs/guides/testing/using-ethers): network-owned Ethers instance.
- [Verification](https://hardhat.org/docs/plugins/hardhat-verify): helper and matching build profiles.
- Offline error-path regression: `python3 tests/test_template_guards.py` from this skill directory. It stubs the external verifier; it does not deploy contracts or establish plugin integration behavior.
