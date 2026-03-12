# Characterization Testing

Golden master and approval testing techniques for preserving behavior during refactoring. Based on Michael Feathers' *Working Effectively with Legacy Code*.

## Contents

- [Characterization Test Theory](#characterization-test-theory)
- [Golden Master Pattern](#golden-master-pattern)
- [Approval Testing Libraries](#approval-testing-libraries)
- [When to Use Characterization Tests](#when-to-use-characterization-tests)
- [Generating Tests from Logs](#generating-tests-from-logs)
- [Maintaining Golden Masters](#maintaining-golden-masters)
- [Transitioning to Unit Tests](#transitioning-to-unit-tests)
- [Workflow Integration](#workflow-integration)
- [Related Resources](#related-resources)

---

## Characterization Test Theory

A characterization test documents what code actually does, not what it should do. The goal is to capture current behavior so you can refactor with confidence, even when you do not fully understand the code.

### Key Principles (Feathers)

1. **The code is the specification** -- existing behavior IS the requirement until proven otherwise
2. **Test what IS, not what SHOULD BE** -- do not fix bugs while characterizing
3. **Cover the boundary you will change** -- test the API surface, module boundary, or function you plan to refactor
4. **Use the tests as a safety net** -- if a characterization test fails after refactoring, you changed behavior

### When Characterization Tests Are Necessary

```
Is the code under test well-understood?
├── Yes → Does it have adequate unit tests?
│   ├── Yes → Refactor directly, existing tests protect you
│   └── No → Write unit tests first if feasible
└── No → Is it risky to change without tests?
    ├── Yes → Write characterization tests
    └── No → Consider the risk tolerance
        ├── High risk (money, auth, data) → Write characterization tests
        └── Low risk → Acceptable to refactor with integration tests only
```

### The Characterization Test Workflow

```
1. Pick the boundary you'll refactor
2. Write tests that call the code and record actual outputs
3. Assert that outputs match the recorded values
4. Run the full characterization suite → all green (by definition)
5. Refactor the internals
6. Run the suite again → if anything fails, you changed behavior
7. Investigate: was the behavior change intentional?
   - Yes → Update the golden master
   - No → Revert the refactoring step
```

---

## Golden Master Pattern

The golden master pattern captures a snapshot of current output and compares future runs against it.

### Basic Golden Master Implementation

```python
"""
Golden master testing: capture output, store as reference,
compare future runs against the reference.
"""
import json
import hashlib
from pathlib import Path
from typing import Any

GOLDEN_DIR = Path("tests/golden_masters")

def capture_golden_master(test_name: str, output: Any) -> Path:
    """Capture current output as the golden master."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    path = GOLDEN_DIR / f"{test_name}.golden.json"

    with open(path, "w") as f:
        json.dump(output, f, indent=2, sort_keys=True, default=str)

    print(f"Golden master captured: {path}")
    return path

def assert_matches_golden_master(test_name: str, actual: Any):
    """Compare current output against the golden master."""
    path = GOLDEN_DIR / f"{test_name}.golden.json"

    if not path.exists():
        # First run: capture the golden master
        capture_golden_master(test_name, actual)
        return

    with open(path) as f:
        expected = json.load(f)

    actual_normalized = json.loads(json.dumps(actual, sort_keys=True, default=str))

    assert actual_normalized == expected, (
        f"Output does not match golden master for {test_name}.\n"
        f"To update the golden master, delete {path} and re-run.\n"
        f"Diff:\n{_diff(expected, actual_normalized)}"
    )

def _diff(expected: Any, actual: Any, path: str = "$") -> str:
    """Generate a human-readable diff."""
    diffs = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        all_keys = set(expected.keys()) | set(actual.keys())
        for key in sorted(all_keys):
            if key not in expected:
                diffs.append(f"  ADDED {path}.{key}: {actual[key]}")
            elif key not in actual:
                diffs.append(f"  REMOVED {path}.{key}: {expected[key]}")
            elif expected[key] != actual[key]:
                diffs.append(f"  CHANGED {path}.{key}: {expected[key]} → {actual[key]}")
    elif expected != actual:
        diffs.append(f"  CHANGED {path}: {expected} → {actual}")
    return "\n".join(diffs) if diffs else "  (no differences)"

# Usage in tests
import pytest

def test_order_total_calculation():
    """Characterization test for the legacy order calculator."""
    from legacy_app.orders import calculate_order_total

    order = {
        "items": [
            {"sku": "WIDGET-A", "qty": 3, "unit_price": 9.99},
            {"sku": "GADGET-B", "qty": 1, "unit_price": 24.50},
        ],
        "coupon": "SAVE10",
        "shipping": "standard",
    }

    result = calculate_order_total(order)
    assert_matches_golden_master("order_total_basic", result)

def test_order_total_edge_cases():
    """Characterization: empty cart, zero quantities, negative discounts."""
    from legacy_app.orders import calculate_order_total

    edge_cases = [
        {"items": [], "coupon": None, "shipping": "standard"},
        {"items": [{"sku": "X", "qty": 0, "unit_price": 10.0}], "coupon": None, "shipping": "express"},
        {"items": [{"sku": "X", "qty": 1, "unit_price": 0.0}], "coupon": "SAVE10", "shipping": "standard"},
    ]

    results = [calculate_order_total(case) for case in edge_cases]
    assert_matches_golden_master("order_total_edge_cases", results)
```

### Golden Master for Data Transformations

```python
"""
Characterize a data transformation pipeline.
Useful for ETL code, report generators, CSV processors.
"""
import csv
import io

def test_csv_export_golden_master():
    """Capture the exact CSV output of the legacy export."""
    from legacy_app.reports import generate_monthly_report

    report = generate_monthly_report(month=1, year=2026)

    # Capture the full output including headers, formatting, precision
    output = io.StringIO()
    writer = csv.writer(output)
    for row in report:
        writer.writerow(row)

    assert_matches_golden_master(
        "monthly_report_jan_2026",
        output.getvalue()
    )
```

---

## Approval Testing Libraries

Approval testing automates the golden master workflow with built-in diff tools and approval commands.

### Python: approvaltests

```python
"""
Using the approvaltests library for Python.
pip install approvaltests
"""
from approvaltests import verify, verify_all
from approvaltests.reporters import GenericDiffReporterFactory

def test_pricing_engine():
    """Approval test: captures output, shows diff on failure."""
    from legacy_app.pricing import calculate_price

    scenarios = [
        ("Basic item", calculate_price(item="widget", qty=1)),
        ("Bulk discount", calculate_price(item="widget", qty=100)),
        ("Premium item", calculate_price(item="premium-widget", qty=1)),
        ("Zero quantity", calculate_price(item="widget", qty=0)),
    ]

    # verify_all generates a formatted string and compares to approved file
    verify_all(
        "Pricing Scenarios",
        scenarios,
        lambda s: f"{s[0]}: ${s[1]:.2f}"
    )

# First run:
#   Creates test_pricing_engine.received.txt
#   Fails (no approved file yet)
#   Review the .received.txt file
#   Rename to test_pricing_engine.approved.txt to approve

# Subsequent runs:
#   Compares output against .approved.txt
#   If different: shows diff and fails
#   If same: passes silently
```

### Java: ApprovalTests.Java

```java
import org.approvaltests.Approvals;
import org.approvaltests.combinations.CombinationApprovals;
import org.junit.jupiter.api.Test;

class PricingEngineTest {

    @Test
    void testPricingCombinations() {
        // Test all combinations of inputs
        CombinationApprovals.verifyAllCombinations(
            this::calculatePrice,
            new String[]{"widget", "premium-widget", "service"},  // items
            new Integer[]{0, 1, 10, 100}                          // quantities
        );
    }

    private String calculatePrice(String item, Integer qty) {
        double price = LegacyPricingEngine.calculate(item, qty);
        return String.format("$%.2f", price);
    }
}
```

### JavaScript: Jest Snapshots

```javascript
// Jest has built-in snapshot testing (approval-style)

const { processOrder } = require("../legacy/orderProcessor");

describe("Order Processor (characterization)", () => {
  test("standard order output", () => {
    const order = {
      items: [
        { sku: "WIDGET-A", qty: 3, price: 9.99 },
        { sku: "GADGET-B", qty: 1, price: 24.50 },
      ],
      coupon: "SAVE10",
    };

    const result = processOrder(order);

    // First run: creates __snapshots__/orderProcessor.test.js.snap
    // Subsequent runs: compares against snapshot
    expect(result).toMatchSnapshot();
  });

  test("edge cases", () => {
    const cases = [
      { items: [], coupon: null },
      { items: [{ sku: "X", qty: 0, price: 10 }], coupon: null },
      { items: [{ sku: "X", qty: -1, price: 10 }], coupon: "INVALID" },
    ];

    cases.forEach((testCase, index) => {
      expect(processOrder(testCase)).toMatchSnapshot(`edge-case-${index}`);
    });
  });
});

// Update snapshots: npx jest --updateSnapshot
```

### Library Comparison

| Library | Language | Diff Tool | CI Support | Combination Testing |
|---------|----------|-----------|------------|-------------------|
| **approvaltests** | Python | System diff, custom | Yes | verify_all |
| **ApprovalTests.Java** | Java | IntelliJ, custom | Yes | CombinationApprovals |
| **Jest snapshots** | JavaScript | Built-in | Yes | Manual loops |
| **verify** (Rust) | Rust | insta crate | Yes | Manual |
| **ApprovalTests.Net** | C# | VS, Beyond Compare | Yes | CombinationApprovals |
| **SnapshotTesting** | Swift | Xcode | Yes | Manual |

---

## When to Use Characterization Tests

### Good Fit

| Scenario | Why Characterization Tests Work |
|----------|-------------------------------|
| **Untested legacy code** | No existing safety net; characterization creates one fast |
| **Complex algorithms** | Behavior is hard to specify; easier to capture than describe |
| **Data transformations** | Output format is the contract; golden master verifies it |
| **Before strangler migration** | Prove the new system matches the old one |
| **Regulatory/compliance code** | Must prove behavior did not change |
| **Third-party integration wrappers** | Capture expected responses for offline testing |

### Poor Fit

| Scenario | Better Alternative |
|----------|-------------------|
| **Nondeterministic output** (timestamps, random IDs) | Mock or normalize before comparing |
| **UI rendering** | Visual regression testing (Chromatic, Percy) |
| **Performance characteristics** | Benchmark tests |
| **Well-understood code with clear specs** | Write proper unit tests instead |
| **Code that is known to be buggy** | Fix bugs first, then characterize |

### Handling Nondeterminism

```python
"""
Normalize nondeterministic values before golden master comparison.
"""
import re
from datetime import datetime

def normalize_for_golden_master(output: dict) -> dict:
    """Remove or normalize nondeterministic fields."""
    normalized = json.loads(json.dumps(output))

    # Replace timestamps with placeholder
    if "created_at" in normalized:
        normalized["created_at"] = "<TIMESTAMP>"

    # Replace UUIDs with placeholder
    if "id" in normalized:
        normalized["id"] = "<UUID>"

    # Normalize floating point precision
    if "total" in normalized:
        normalized["total"] = round(normalized["total"], 2)

    return normalized

def normalize_string_output(text: str) -> str:
    """Normalize nondeterministic values in string output."""
    # Replace UUIDs
    text = re.sub(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        '<UUID>', text
    )
    # Replace ISO timestamps
    text = re.sub(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?',
        '<TIMESTAMP>', text
    )
    return text
```

---

## Generating Tests from Logs

Use production or staging logs to generate realistic characterization test cases.

### Log-to-Test Generator

```python
"""
Generate characterization tests from request/response logs.
Input: structured logs with request + response pairs.
Output: pytest test file with golden master assertions.
"""
import json
from pathlib import Path

def generate_tests_from_logs(log_file: str, output_dir: str, max_tests: int = 50):
    """Parse request/response logs into test cases."""
    test_cases = []

    with open(log_file) as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("type") != "http_request":
                continue

            test_cases.append({
                "method": entry["http"]["method"],
                "path": entry["http"]["path"],
                "request_body": entry.get("request_body"),
                "response_status": entry["http"]["status_code"],
                "response_body": entry.get("response_body"),
            })

            if len(test_cases) >= max_tests:
                break

    # Generate test file
    output = Path(output_dir) / "test_characterization_generated.py"
    with open(output, "w") as f:
        f.write('"""Auto-generated characterization tests from production logs."""\n')
        f.write("import pytest\n")
        f.write("import requests\n\n")
        f.write('BASE_URL = "http://localhost:8000"\n\n')

        for i, tc in enumerate(test_cases):
            f.write(f"def test_case_{i:04d}_{tc['method'].lower()}_{tc['path'].replace('/', '_').strip('_')}():\n")
            f.write(f'    """Characterized from production log entry."""\n')
            f.write(f'    response = requests.{tc["method"].lower()}(\n')
            f.write(f'        f"{{BASE_URL}}{tc["path"]}",\n')
            if tc["request_body"]:
                f.write(f"        json={json.dumps(tc['request_body'])},\n")
            f.write(f"    )\n")
            f.write(f"    assert response.status_code == {tc['response_status']}\n")
            if tc["response_body"]:
                f.write(f"    assert response.json() == {json.dumps(tc['response_body'])}\n")
            f.write("\n\n")

    print(f"Generated {len(test_cases)} test cases in {output}")

# Usage
generate_tests_from_logs(
    "logs/api-access-2026-01.jsonl",
    "tests/characterization/",
    max_tests=100
)
```

### Sampling Strategy for Log-Based Test Generation

- [ ] Include at least one example per endpoint
- [ ] Include examples for each HTTP status code returned
- [ ] Prioritize endpoints that will be refactored
- [ ] Include edge cases (empty bodies, large payloads, special characters)
- [ ] Normalize nondeterministic fields (timestamps, IDs) before storing as golden masters
- [ ] Limit to 50-200 tests to keep the suite fast

---

## Maintaining Golden Masters

### Golden Master Lifecycle

| Phase | Action | Who |
|-------|--------|-----|
| **Capture** | Run test for the first time, review and approve output | Developer starting refactoring |
| **Protect** | Golden masters committed to Git, fail CI on mismatch | CI/CD pipeline |
| **Update** | Intentional behavior change requires re-approval | Developer + reviewer |
| **Retire** | Replace with unit tests after refactoring complete | Developer |

### Update Workflow

```bash
#!/bin/bash
# update-golden-masters.sh
# Use when behavior change is intentional

echo "WARNING: This will overwrite golden masters with current output."
echo "Only run this after confirming the behavior change is intentional."
read -p "Continue? (y/N) " confirm

if [ "$confirm" != "y" ]; then
    echo "Aborted."
    exit 0
fi

# For pytest + custom golden master
find tests/golden_masters -name "*.golden.json" -delete
pytest tests/characterization/ -x

# For Jest snapshots
# npx jest --updateSnapshot

# For approvaltests
# mv tests/*.received.txt tests/*.approved.txt

echo "Golden masters updated. Review changes with: git diff tests/"
```

### CI Protection

```yaml
# .github/workflows/characterization-tests.yaml
name: Characterization Tests

on:
  pull_request:
    paths:
      - "src/**"
      - "tests/characterization/**"
      - "tests/golden_masters/**"

jobs:
  characterization:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run characterization tests
        run: pytest tests/characterization/ -v

      - name: Check for unapproved golden master changes
        run: |
          if git diff --name-only | grep -q "golden_masters"; then
            echo "::error::Golden master files were modified during test run."
            echo "::error::This means behavior changed. Review carefully."
            git diff tests/golden_masters/
            exit 1
          fi
```

---

## Transitioning to Unit Tests

Characterization tests are temporary scaffolding. Replace them with proper unit tests as you understand the code better.

### Transition Process

```
Phase 1: Characterize
  - Write golden master tests around the boundary
  - Cover happy paths and edge cases
  - All tests pass (they capture current behavior)

Phase 2: Refactor
  - Extract methods, introduce seams, simplify
  - Characterization tests catch any behavior changes
  - Keep refactoring steps small

Phase 3: Understand
  - As you refactor, you learn what the code actually does
  - Document discovered behavior as comments or specs
  - Identify bugs vs features in the current behavior

Phase 4: Replace
  - Write unit tests for the refactored code
  - Each unit test replaces part of the characterization test
  - Unit tests test intent; characterization tests test behavior
  - Delete characterization tests when fully covered

Phase 5: Clean up
  - Remove golden master files
  - Remove characterization test infrastructure
  - Update CI to run only unit/integration tests
```

### Replacement Checklist

- [ ] Every characterization test has a corresponding unit test
- [ ] Unit tests cover the same edge cases
- [ ] Unit tests are faster than characterization tests
- [ ] Golden master files deleted from repository
- [ ] CI updated to exclude characterization test directory
- [ ] Documentation updated with discovered behavior notes

---

## Workflow Integration

### Refactoring with Characterization Tests: Step by Step

```bash
# 1. Create the characterization test branch
git checkout -b refactor/order-calculator

# 2. Write characterization tests
pytest tests/characterization/test_order_calculator.py -v
# All pass (capturing current behavior)

# 3. Commit the golden masters
git add tests/characterization/ tests/golden_masters/
git commit -m "Add characterization tests for order calculator"

# 4. Refactor in small steps
# ... make changes ...
pytest tests/characterization/test_order_calculator.py -v
# If any fail: you changed behavior. Investigate.

# 5. After refactoring is complete, write unit tests
pytest tests/unit/test_order_calculator.py -v

# 6. Verify unit tests cover characterization tests
pytest tests/ --cov=src/orders/calculator.py
# Coverage should be equal or better

# 7. Remove characterization tests
git rm tests/characterization/test_order_calculator.py
git rm tests/golden_masters/order_calculator_*.golden.json
git commit -m "Replace characterization tests with unit tests for order calculator"
```

---

## Related Resources

- [Legacy Code Strategies](./legacy-code-strategies.md) - Broader strategies for working with legacy code
- [Code Smells Guide](./code-smells-guide.md) - Identifying what to refactor
- [Refactoring Catalog](./refactoring-catalog.md) - Specific refactoring techniques
- [Strangler Fig Migration](./strangler-fig-migration.md) - Incremental migration using characterization tests
- [Automated Refactoring Tools](./automated-refactoring-tools.md) - Tool-assisted refactoring
- [Tech Debt Management](./tech-debt-management.md) - Prioritizing refactoring work
- [SKILL.md](../SKILL.md) - Parent skill overview
