// ESLint flat-config starter for refactoring safety.
// Copy to your project root as eslint.config.js and tune thresholds per repo.

const js = require("@eslint/js");
const globals = require("globals");
const tsParser = require("@typescript-eslint/parser");
const tsPlugin = require("@typescript-eslint/eslint-plugin");

module.exports = [
  {
    ignores: [
      "**/dist/**",
      "**/build/**",
      "**/coverage/**",
      "**/node_modules/**",
    ],
  },
  js.configs.recommended,
  {
    files: ["**/*.{js,cjs,mjs,ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.node,
        ...globals.es2024,
      },
      parser: tsParser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
    },
    rules: {
      // Safety rules for behavior-preserving refactors.
      complexity: ["warn", 12],
      "max-depth": ["warn", 4],
      "max-lines-per-function": [
        "warn",
        {
          max: 80,
          skipBlankLines: true,
          skipComments: true,
        },
      ],
      "max-params": ["warn", 4],
      "no-duplicate-imports": "error",
      "no-else-return": ["warn", { allowElseIf: false }],
      "no-empty": ["error", { allowEmptyCatch: false }],
      "no-empty-function": "error",
      "no-implicit-coercion": "warn",
      "no-lonely-if": "warn",
      "no-magic-numbers": [
        "off",
        {
          ignore: [-1, 0, 1, 2],
          ignoreArrayIndexes: true,
          enforceConst: true,
        },
      ],
      "no-negated-condition": "off",
      "no-nested-ternary": "warn",
      "no-param-reassign": "error",
      "no-shadow": "off",
      "no-unused-vars": [
        "off",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
      "no-useless-return": "warn",
      "prefer-const": "error",
      "prefer-template": "warn",
      "require-await": "off",
      eqeqeq: ["error", "always"],

      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/no-shadow": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
      "@typescript-eslint/prefer-nullish-coalescing": "warn",
      "@typescript-eslint/prefer-optional-chain": "warn",
    },
  },
  {
    files: ["**/*.{test,spec}.{js,ts,tsx}"],
    rules: {
      complexity: "off",
      "max-lines-per-function": "off",
      "max-params": "off",
    },
  },
];

/*
Install:
  npm install --save-dev eslint @eslint/js globals @typescript-eslint/parser @typescript-eslint/eslint-plugin

Suggested package.json scripts:
  {
    "scripts": {
      "lint": "eslint .",
      "lint:fix": "eslint . --fix"
    }
  }

Notes:
  - Keep formatting in Prettier (or the formatter your repo already uses).
  - Treat thresholds as starting heuristics, not universal refactor laws.
  - Add type-aware rules only after wiring project-specific tsconfig settings.
*/
