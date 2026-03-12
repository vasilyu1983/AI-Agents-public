# Automated Refactoring Tools

Codemods, AST transforms, and IDE refactoring automation for safe, large-scale code changes. Move beyond manual find-and-replace.

## Contents

- [Codemod Frameworks](#codemod-frameworks)
- [AST Manipulation Basics](#ast-manipulation-basics)
- [Writing Custom Codemods](#writing-custom-codemods)
- [IDE Refactoring Features](#ide-refactoring-features)
- [Large-Scale Refactoring](#large-scale-refactoring)
- [Safety Verification](#safety-verification)
- [Codemod Testing Strategies](#codemod-testing-strategies)
- [Migration Codemods for Framework Upgrades](#migration-codemods-for-framework-upgrades)
- [Codemod Composition Patterns](#codemod-composition-patterns)
- [Related Resources](#related-resources)

---

## Codemod Frameworks

### Framework Overview

| Framework | Language | AST Library | Maintained By | Best For |
|-----------|---------|-------------|---------------|----------|
| **jscodeshift** | JavaScript/TypeScript | recast + ast-types | Meta | React/JS migrations |
| **ts-morph** | TypeScript | TypeScript compiler | Community | TS-specific transforms |
| **libCST** | Python | libCST (concrete syntax tree) | Meta/Instagram | Python code transforms |
| **Scalafix** | Scala | Scalameta | Community | Scala migrations |
| **Rector** | PHP | php-parser | Community | PHP framework upgrades |
| **Grit** | Multi-language | Tree-sitter | Grit.io | Pattern-based, polyglot |
| **Semgrep** | Multi-language | Tree-sitter | Semgrep Inc | Pattern matching + autofix |
| **OpenRewrite** | Java/Kotlin | Custom | Moderne | Java framework migrations |

### Installation

```bash
# jscodeshift (JavaScript/TypeScript)
npm install -g jscodeshift

# ts-morph (TypeScript)
npm install ts-morph

# libCST (Python)
pip install libcst

# Rector (PHP)
composer require rector/rector --dev

# OpenRewrite (Java - via Maven)
# Add to pom.xml as plugin

# Grit
npm install -g @getgrit/cli

# Semgrep
pip install semgrep
```

---

## AST Manipulation Basics

Understanding ASTs (Abstract Syntax Trees) is the foundation for writing codemods.

### What Is an AST?

```javascript
// Source code:
const total = price * quantity;

// AST (simplified):
{
  "type": "VariableDeclaration",
  "kind": "const",
  "declarations": [{
    "type": "VariableDeclarator",
    "id": { "type": "Identifier", "name": "total" },
    "init": {
      "type": "BinaryExpression",
      "operator": "*",
      "left": { "type": "Identifier", "name": "price" },
      "right": { "type": "Identifier", "name": "quantity" }
    }
  }]
}
```

### AST Explorer

Use [astexplorer.net](https://astexplorer.net) to visualize ASTs interactively. Select the parser that matches your codemod framework:

| Codemod Tool | AST Explorer Parser |
|-------------|-------------------|
| jscodeshift | recast |
| ts-morph | TypeScript |
| libCST | Python (CST) |
| Babel | @babel/parser |

### CST vs AST

| Property | AST (Abstract Syntax Tree) | CST (Concrete Syntax Tree) |
|----------|---------------------------|---------------------------|
| Whitespace | Discarded | Preserved |
| Comments | Usually discarded | Preserved |
| Formatting | Lost | Preserved |
| Best for | Analysis, linting | Refactoring (preserves style) |
| Libraries | babel, typescript, tree-sitter | recast, libCST, ts-morph |

For refactoring, prefer CST-based tools (recast, libCST) to preserve formatting and comments.

---

## Writing Custom Codemods

### jscodeshift: Rename a Function

```javascript
// codemod: rename-function.js
// Renames all calls from `oldFunctionName` to `newFunctionName`

module.exports = function (fileInfo, api) {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  // Find all function calls to `oldFunctionName`
  root
    .find(j.CallExpression, {
      callee: { type: "Identifier", name: "oldFunctionName" },
    })
    .forEach((path) => {
      path.node.callee.name = "newFunctionName";
    });

  // Also rename the import if it exists
  root
    .find(j.ImportSpecifier, {
      imported: { name: "oldFunctionName" },
    })
    .forEach((path) => {
      path.node.imported.name = "newFunctionName";
      // Update local binding too
      if (path.node.local && path.node.local.name === "oldFunctionName") {
        path.node.local.name = "newFunctionName";
      }
    });

  return root.toSource({ quote: "single" });
};

// Run:
// jscodeshift -t rename-function.js src/**/*.js
```

### jscodeshift: Migrate API Pattern

```javascript
// codemod: migrate-fetch-to-axios.js
// Transform: fetch(url, { method: 'POST', body: JSON.stringify(data) })
// Into:     axios.post(url, data)

module.exports = function (fileInfo, api) {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);
  let needsAxiosImport = false;

  root
    .find(j.CallExpression, { callee: { name: "fetch" } })
    .forEach((path) => {
      const args = path.node.arguments;
      if (args.length < 2) return;

      const url = args[0];
      const options = args[1];

      if (options.type !== "ObjectExpression") return;

      const methodProp = options.properties.find(
        (p) => p.key.name === "method" || p.key.value === "method"
      );
      const bodyProp = options.properties.find(
        (p) => p.key.name === "body" || p.key.value === "body"
      );

      if (!methodProp) return;

      const method = methodProp.value.value?.toLowerCase();
      if (!method) return;

      needsAxiosImport = true;

      // Build axios call
      let axiosArgs = [url];

      if (bodyProp && bodyProp.value.type === "CallExpression") {
        // Extract data from JSON.stringify(data)
        if (
          bodyProp.value.callee.object?.name === "JSON" &&
          bodyProp.value.callee.property?.name === "stringify"
        ) {
          axiosArgs.push(bodyProp.value.arguments[0]);
        }
      }

      // Replace fetch() with axios.method()
      j(path).replaceWith(
        j.callExpression(
          j.memberExpression(j.identifier("axios"), j.identifier(method)),
          axiosArgs
        )
      );
    });

  // Add axios import if needed
  if (needsAxiosImport) {
    const axiosImport = j.importDeclaration(
      [j.importDefaultSpecifier(j.identifier("axios"))],
      j.literal("axios")
    );

    const body = root.find(j.Program).get("body");
    body.unshift(axiosImport);
  }

  return root.toSource();
};
```

### libCST: Python Codemod

```python
"""
Codemod: Migrate from unittest assertions to pytest assertions.
Transform: self.assertEqual(a, b) → assert a == b
"""
import libcst as cst
import libcst.matchers as m

class UnittestToPytestTransformer(cst.CSTTransformer):
    """Transform unittest-style assertions to pytest-style."""

    ASSERTION_MAP = {
        "assertEqual": "==",
        "assertNotEqual": "!=",
        "assertTrue": None,  # Special handling
        "assertFalse": None,
        "assertIs": "is",
        "assertIsNot": "is not",
        "assertIn": "in",
        "assertNotIn": "not in",
        "assertIsNone": None,
        "assertIsNotNone": None,
        "assertGreater": ">",
        "assertGreaterEqual": ">=",
        "assertLess": "<",
        "assertLessEqual": "<=",
    }

    def leave_Expr(
        self, original_node: cst.Expr, updated_node: cst.Expr
    ) -> cst.BaseStatement:
        # Match self.assertXxx(...) calls
        if not m.matches(
            updated_node.value,
            m.Call(func=m.Attribute(value=m.Name("self"))),
        ):
            return updated_node

        call = updated_node.value
        method_name = call.func.attr.value

        if method_name not in self.ASSERTION_MAP:
            return updated_node

        args = [arg.value for arg in call.args]
        operator = self.ASSERTION_MAP[method_name]

        # Binary comparison: assertEqual(a, b) → assert a == b
        if operator and len(args) >= 2:
            comparison = cst.Comparison(
                left=args[0],
                comparisons=[
                    cst.ComparisonTarget(
                        operator=self._get_cst_operator(operator),
                        comparator=args[1],
                    )
                ],
            )
            return updated_node.with_changes(
                value=cst.Assert(test=comparison)
            )

        # assertTrue(x) → assert x
        if method_name == "assertTrue" and len(args) >= 1:
            return updated_node.with_changes(
                value=cst.Assert(test=args[0])
            )

        # assertFalse(x) → assert not x
        if method_name == "assertFalse" and len(args) >= 1:
            return updated_node.with_changes(
                value=cst.Assert(test=cst.UnaryOperation(
                    operator=cst.Not(),
                    expression=args[0],
                ))
            )

        return updated_node

    def _get_cst_operator(self, op_str: str):
        ops = {
            "==": cst.Equal(),
            "!=": cst.NotEqual(),
            ">": cst.GreaterThan(),
            ">=": cst.GreaterThanEqual(),
            "<": cst.LessThan(),
            "<=": cst.LessThanEqual(),
            "in": cst.In(),
            "not in": cst.NotIn(),
            "is": cst.Is(),
            "is not": cst.IsNot(),
        }
        return ops[op_str]

# Run the codemod
def run_codemod(file_path: str):
    with open(file_path) as f:
        source = f.read()

    tree = cst.parse_module(source)
    modified = tree.visit(UnittestToPytestTransformer())

    with open(file_path, "w") as f:
        f.write(modified.code)
```

---

## IDE Refactoring Features

### VS Code Refactoring

| Refactoring | Keyboard Shortcut | Scope |
|------------|-------------------|-------|
| Rename symbol | F2 | Project-wide |
| Extract function | Ctrl+Shift+R | Selection |
| Extract variable | Ctrl+Shift+R | Selection |
| Move to new file | Quick Fix menu | Single symbol |
| Inline variable | Quick Fix menu | Single variable |
| Convert to template literal | Quick Fix menu | String concatenation |

### IntelliJ IDEA Refactoring

| Refactoring | Keyboard Shortcut | Scope |
|------------|-------------------|-------|
| Rename | Shift+F6 | Project-wide with usages |
| Extract method | Ctrl+Alt+M | Selection |
| Extract variable | Ctrl+Alt+V | Expression |
| Extract interface | Refactor menu | Class |
| Inline | Ctrl+Alt+N | Variable, method, or class |
| Move | F6 | Class, file, or package |
| Change signature | Ctrl+F6 | Method parameters |
| Pull members up | Refactor menu | Inheritance |
| Push members down | Refactor menu | Inheritance |
| Safe delete | Alt+Delete | Verify no usages before deleting |

### When IDE Refactoring Is Sufficient

```
Number of files to change?
├── 1-5 files → IDE refactoring (rename, extract, inline)
├── 5-50 files → IDE refactoring OR simple codemod
├── 50-500 files → Codemod required
└── 500+ files → Codemod + staged rollout
```

---

## Large-Scale Refactoring

### Meta's Approach to Large-Scale Codemods

Meta (Facebook) runs codemods across millions of files. Their approach:

1. **Write the codemod** -- Transform the code pattern
2. **Test on a sample** -- Run on 100 files, review manually
3. **Dry-run at scale** -- Generate diffs for all files without writing
4. **Human review** -- Sample review of generated diffs
5. **Apply in batches** -- Commit in groups of 100-500 files
6. **CI validation** -- Full test suite runs on each batch

### Batch Execution Pattern

```bash
#!/bin/bash
# run-codemod-batched.sh
# Run a codemod in batches with CI validation

CODEMOD="$1"
BATCH_SIZE=100
FILES=$(find src -name "*.ts" -type f)
TOTAL=$(echo "$FILES" | wc -l)
BATCH=0

echo "Running codemod: $CODEMOD"
echo "Total files: $TOTAL"
echo "Batch size: $BATCH_SIZE"

echo "$FILES" | while mapfile -t -n $BATCH_SIZE batch && [ ${#batch[@]} -gt 0 ]; do
    BATCH=$((BATCH + 1))
    echo ""
    echo "=== Batch $BATCH (${#batch[@]} files) ==="

    # Apply codemod to this batch
    jscodeshift -t "$CODEMOD" "${batch[@]}"

    # Run tests
    echo "Running tests..."
    if ! npm test 2>/dev/null; then
        echo "TESTS FAILED in batch $BATCH. Reverting..."
        git checkout -- "${batch[@]}"
        echo "Reverted. Investigate and fix codemod."
        exit 1
    fi

    # Commit batch
    git add "${batch[@]}"
    git commit -m "codemod: $(basename "$CODEMOD" .js) (batch $BATCH)"

    echo "Batch $BATCH committed successfully."
done

echo ""
echo "All batches complete."
```

### Dry-Run and Diff Generation

```bash
# jscodeshift: dry-run mode (prints to stdout, doesn't modify files)
jscodeshift -t my-codemod.js --dry --print src/

# Generate diff without applying
jscodeshift -t my-codemod.js --dry src/ 2>&1 | tee codemod-preview.diff

# Count affected files
jscodeshift -t my-codemod.js --dry src/ 2>&1 | grep "^Modified" | wc -l

# Semgrep: autofix with diff preview
semgrep --config my-rules.yaml --autofix --dryrun src/
```

---

## Safety Verification

### Post-Codemod Verification Checklist

- [ ] **TypeScript compiles** -- `tsc --noEmit` passes
- [ ] **Linter passes** -- `eslint .` or equivalent
- [ ] **Unit tests pass** -- Full test suite green
- [ ] **Integration tests pass** -- API contract tests green
- [ ] **No behavior change** -- Characterization tests green
- [ ] **No import cycles** -- `madge --circular src/`
- [ ] **No dead code introduced** -- `ts-prune` or `vulture`
- [ ] **Bundle size stable** -- Size diff within 5%
- [ ] **Manual review of sample** -- Spot-check 10 transformed files

### Automated Verification Pipeline

```yaml
# .github/workflows/codemod-verify.yaml
name: Codemod Verification

on:
  pull_request:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npx eslint src/ --max-warnings=0

      - name: Unit tests
        run: npm test

      - name: Check for circular imports
        run: npx madge --circular src/

      - name: Bundle size check
        run: |
          npm run build
          CURRENT_SIZE=$(du -sb dist/ | cut -f1)
          echo "Bundle size: $CURRENT_SIZE bytes"
          # Compare against baseline
          BASELINE=$(cat .bundle-size-baseline 2>/dev/null || echo 0)
          DIFF=$((CURRENT_SIZE - BASELINE))
          if [ $DIFF -gt 50000 ]; then
            echo "::warning::Bundle size increased by $DIFF bytes"
          fi
```

---

## Codemod Testing Strategies

### Unit Testing Codemods

```javascript
// __tests__/rename-function-codemod.test.js
const { applyTransform } = require("jscodeshift/dist/testUtils");
const transform = require("../rename-function");

describe("rename-function codemod", () => {
  it("renames function calls", () => {
    const input = `
      import { oldFunctionName } from './utils';
      const result = oldFunctionName(arg1, arg2);
    `;

    const expected = `
      import { newFunctionName } from './utils';
      const result = newFunctionName(arg1, arg2);
    `;

    const output = applyTransform(transform, {}, { source: input });
    expect(output.trim()).toBe(expected.trim());
  });

  it("handles already-renamed code (idempotent)", () => {
    const input = `
      import { newFunctionName } from './utils';
      const result = newFunctionName(arg1);
    `;

    const output = applyTransform(transform, {}, { source: input });
    expect(output.trim()).toBe(input.trim());
  });

  it("does not rename unrelated functions", () => {
    const input = `
      const result = unrelatedFunction(arg);
    `;

    const output = applyTransform(transform, {}, { source: input });
    expect(output.trim()).toBe(input.trim());
  });

  it("handles no matches gracefully", () => {
    const input = `console.log("hello");`;
    const output = applyTransform(transform, {}, { source: input });
    expect(output.trim()).toBe(input.trim());
  });
});
```

### Testing Python Codemods

```python
"""
Test suite for Python codemods using libCST.
"""
import pytest
import libcst as cst
from codemods.unittest_to_pytest import UnittestToPytestTransformer

def apply_codemod(source: str) -> str:
    tree = cst.parse_module(source)
    modified = tree.visit(UnittestToPytestTransformer())
    return modified.code

def test_assertEqual_transforms():
    input_code = 'self.assertEqual(result, 42)'
    expected = 'assert result == 42'
    assert apply_codemod(input_code).strip() == expected

def test_assertTrue_transforms():
    input_code = 'self.assertTrue(is_valid)'
    expected = 'assert is_valid'
    assert apply_codemod(input_code).strip() == expected

def test_assertFalse_transforms():
    input_code = 'self.assertFalse(is_deleted)'
    expected = 'assert not is_deleted'
    assert apply_codemod(input_code).strip() == expected

def test_preserves_non_assertion_code():
    input_code = 'result = calculate(x, y)'
    assert apply_codemod(input_code).strip() == input_code

def test_idempotent_on_already_transformed():
    input_code = 'assert result == 42'
    assert apply_codemod(input_code).strip() == input_code

def test_preserves_comments():
    input_code = '# Check the result\nself.assertEqual(result, 42)'
    output = apply_codemod(input_code)
    assert '# Check the result' in output
    assert 'assert result == 42' in output
```

### Test Fixtures Pattern

```
codemods/
  __tests__/
    __fixtures__/
      rename-function/
        input.js       # Before codemod
        output.js      # Expected after codemod
      migrate-api/
        input.ts
        output.ts
    rename-function.test.js
    migrate-api.test.js
```

```javascript
// Generic fixture-based test runner
const fs = require("fs");
const path = require("path");
const { applyTransform } = require("jscodeshift/dist/testUtils");

function testFixture(codemodName, fixtureName) {
  const fixtureDir = path.join(__dirname, "__fixtures__", codemodName);
  const input = fs.readFileSync(path.join(fixtureDir, `${fixtureName}.input.js`), "utf8");
  const expected = fs.readFileSync(path.join(fixtureDir, `${fixtureName}.output.js`), "utf8");
  const transform = require(`../${codemodName}`);

  const output = applyTransform(transform, {}, { source: input });
  expect(output.trim()).toBe(expected.trim());
}
```

---

## Migration Codemods for Framework Upgrades

### React Class to Functional Components

```javascript
// codemod: class-to-functional.js (simplified)
module.exports = function (fileInfo, api) {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  root
    .find(j.ClassDeclaration, {
      superClass: { name: "Component" },
    })
    .forEach((path) => {
      const className = path.node.id.name;
      const renderMethod = path.node.body.body.find(
        (m) => m.type === "ClassMethod" && m.key.name === "render"
      );

      if (!renderMethod) return;

      // Create functional component
      const funcComponent = j.variableDeclaration("const", [
        j.variableDeclarator(
          j.identifier(className),
          j.arrowFunctionExpression(
            [j.identifier("props")],
            renderMethod.body
          )
        ),
      ]);

      j(path).replaceWith(funcComponent);
    });

  return root.toSource();
};
```

### Common Framework Migration Codemods

| Migration | Tool | Notes |
|-----------|------|-------|
| React class → functional | jscodeshift | Meta provides official codemods |
| Vue 2 → Vue 3 | @vue/compat + codemods | Vue CLI migration helper |
| Angular upgrade | ng update | Built-in schematics |
| Express 4 → 5 | Custom jscodeshift | Middleware signature changes |
| Jest 28 → 29 | jest-codemods | Official migration toolkit |
| Python 2 → 3 | 2to3, futurize | Built into Python stdlib |
| jQuery → vanilla JS | jscodeshift | Community codemods available |
| Moment.js → date-fns | Custom codemod | API surface changes |
| Enzyme → Testing Library | codemod-missing-await | Community codemod |

### Finding Existing Codemods

```bash
# Search npm for codemods
npm search codemod react
npm search jscodeshift migration

# Search GitHub for codemods
gh search repos "codemod jscodeshift" --sort stars

# React codemods (official)
npx @codemod-com/cli react/19/replace-string-ref

# Semgrep registry
semgrep --config "p/react-best-practices" src/
```

---

## Codemod Composition Patterns

### Sequential Composition

Run codemods in order, where each builds on the previous one.

```bash
#!/bin/bash
# run-migration.sh: Compose multiple codemods sequentially

echo "Step 1: Rename imports"
jscodeshift -t codemods/01-rename-imports.js src/

echo "Step 2: Update function signatures"
jscodeshift -t codemods/02-update-signatures.js src/

echo "Step 3: Migrate API calls"
jscodeshift -t codemods/03-migrate-api.js src/

echo "Step 4: Clean up unused imports"
jscodeshift -t codemods/04-remove-unused-imports.js src/

echo "Step 5: Run formatter"
npx prettier --write src/

echo "Step 6: Verify"
npx tsc --noEmit && npm test
```

### Pipeline Composition (libCST)

```python
"""
Compose multiple libCST transformers into a single pass.
More efficient than running each transformer separately.
"""
import libcst as cst
from typing import Sequence

def compose_transformers(
    source: str,
    transformers: Sequence[cst.CSTTransformer],
) -> str:
    """Apply multiple transformers in a single parse-transform-print cycle."""
    tree = cst.parse_module(source)

    for transformer in transformers:
        tree = tree.visit(transformer)

    return tree.code

# Usage
from codemods.rename_imports import RenameImportsTransformer
from codemods.update_signatures import UpdateSignaturesTransformer
from codemods.migrate_api import MigrateAPITransformer

result = compose_transformers(
    source=open("src/service.py").read(),
    transformers=[
        RenameImportsTransformer(),
        UpdateSignaturesTransformer(),
        MigrateAPITransformer(),
    ],
)
```

### Conditional Composition

```javascript
// codemod-runner.js: Apply codemods conditionally based on file analysis

module.exports = function (fileInfo, api) {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  // Only apply React migration if file uses React
  const hasReactImport = root.find(j.ImportDeclaration, {
    source: { value: "react" },
  }).length > 0;

  if (hasReactImport) {
    // Apply React-specific transforms
    applyReactMigration(root, j);
  }

  // Only apply API migration if file imports the old API client
  const hasOldClient = root.find(j.ImportDeclaration, {
    source: { value: "@company/old-api-client" },
  }).length > 0;

  if (hasOldClient) {
    applyAPIMigration(root, j);
  }

  return root.toSource();
};
```

---

## Related Resources

- [Characterization Testing](./characterization-testing.md) - Verify behavior after automated refactoring
- [Code Smells Guide](./code-smells-guide.md) - Identify patterns to target with codemods
- [Refactoring Catalog](./refactoring-catalog.md) - Manual refactoring techniques
- [Strangler Fig Migration](./strangler-fig-migration.md) - Incremental system replacement
- [Tech Debt Management](./tech-debt-management.md) - Prioritizing what to codemod
- [Operational Patterns](./operational-patterns.md) - CI/CD integration for refactoring
- [SKILL.md](../SKILL.md) - Parent skill overview
