// ESLint Configuration for Code Quality & Refactoring
// Copy this to your project as .eslintrc.js

module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended', // If using TypeScript
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  plugins: [
    '@typescript-eslint',
  ],
  rules: {
    // ============================================
    // CODE QUALITY RULES
    // ============================================

    // Complexity Rules (prevent code smells)
    'complexity': ['error', 10], // Max cyclomatic complexity
    'max-depth': ['error', 3], // Max nesting depth
    'max-lines': ['error', {
      max: 300, // Max lines per file
      skipBlankLines: true,
      skipComments: true,
    }],
    'max-lines-per-function': ['error', {
      max: 50, // Max lines per function
      skipBlankLines: true,
      skipComments: true,
    }],
    'max-nested-callbacks': ['error', 3], // Max callback nesting
    'max-params': ['error', 4], // Max function parameters
    'max-statements': ['error', 15], // Max statements per function

    // Naming Conventions
    'camelcase': ['error', {
      properties: 'never',
      ignoreDestructuring: true,
    }],
    'id-length': ['error', {
      min: 2, // Min variable name length
      exceptions: ['i', 'j', 'k', 'x', 'y', 'z', '_'], // Loop counters allowed
    }],
    'new-cap': ['error', { // Constructor names must start with capital
      newIsCap: true,
      capIsNew: false,
    }],

    // Code Smell Prevention
    'no-duplicate-imports': 'error',
    'no-else-return': ['error', {
      allowElseIf: false, // Enforce guard clauses
    }],
    'no-lonely-if': 'error', // Merge nested if statements
    'no-magic-numbers': ['warn', {
      ignore: [-1, 0, 1, 2], // Common numbers allowed
      ignoreArrayIndexes: true,
      enforceConst: true,
    }],
    'no-negated-condition': 'warn', // Avoid negated conditions
    'no-nested-ternary': 'error', // No nested ternaries
    'no-param-reassign': 'error', // Don't modify parameters
    'no-return-assign': 'error', // No assignment in return
    'no-unneeded-ternary': 'error', // Use boolean instead
    'no-unused-expressions': 'error',
    'no-unused-vars': ['error', {
      argsIgnorePattern: '^_', // Allow unused args starting with _
      varsIgnorePattern': '^_',
    }],
    'no-useless-return': 'error',
    'no-var': 'error', // Use const/let instead
    'prefer-const': 'error', // Use const when possible
    'prefer-template': 'error', // Use template literals

    // Function Quality
    'consistent-return': 'error', // All paths must return same type
    'default-case': 'warn', // Switch statements need default
    'default-param-last': 'error', // Default params at end
    'func-style': ['error', 'declaration', { // Use function declarations
      allowArrowFunctions: true,
    }],
    'no-console': 'warn', // No console.log in production
    'no-debugger': 'error', // No debugger statements
    'no-empty-function': 'error',
    'no-loop-func': 'error', // No functions in loops
    'no-shadow': 'error', // No variable shadowing
    'require-await': 'error', // Async functions must have await

    // Best Practices
    'curly': ['error', 'all'], // Always use braces
    'dot-notation': 'error', // Use dot notation when possible
    'eqeqeq': ['error', 'always'], // Use === instead of ==
    'guard-for-in': 'error', // Check hasOwnProperty in for-in
    'no-alert': 'error', // No alert() calls
    'no-eval': 'error', // No eval()
    'no-implied-eval': 'error', // No setTimeout with string
    'no-multi-assign': 'error', // No a = b = c
    'no-new': 'error', // No new for side effects
    'no-throw-literal': 'error', // Throw Error objects
    'prefer-arrow-callback': 'error', // Use arrow functions for callbacks
    'prefer-promise-reject-errors': 'error', // Reject with Error objects
    'radix': 'error', // parseInt with radix
    'yoda': 'error', // No yoda conditions

    // Error Handling
    'no-catch-shadow': 'off', // Deprecated in ESLint 8
    'no-empty': ['error', {
      allowEmptyCatch: false, // No empty catch blocks
    }],
    'no-ex-assign': 'error', // No reassigning exception
    'no-throw-literal': 'error', // Throw Error objects only

    // ============================================
    // TYPESCRIPT-SPECIFIC RULES
    // ============================================

    '@typescript-eslint/no-explicit-any': 'warn', // Avoid any
    '@typescript-eslint/explicit-function-return-type': ['warn', {
      allowExpressions: true,
      allowTypedFunctionExpressions: true,
    }],
    '@typescript-eslint/no-unused-vars': ['error', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    '@typescript-eslint/prefer-nullish-coalescing': 'error',
    '@typescript-eslint/prefer-optional-chain': 'error',
    '@typescript-eslint/no-floating-promises': 'error', // Handle promises

    // ============================================
    // CODE STYLE (optional - use Prettier instead)
    // ============================================

    'indent': ['error', 2], // 2-space indentation
    'linebreak-style': ['error', 'unix'], // Unix line endings
    'quotes': ['error', 'single', {
      avoidEscape: true,
      allowTemplateLiterals: true,
    }],
    'semi': ['error', 'always'], // Always use semicolons
    'comma-dangle': ['error', 'always-multiline'], // Trailing commas
    'max-len': ['error', {
      code: 120, // Max line length
      ignoreUrls: true,
      ignoreStrings: true,
      ignoreTemplateLiterals: true,
    }],
  },

  // ============================================
  // OVERRIDES FOR SPECIFIC FILES
  // ============================================

  overrides: [
    {
      // Test files can be longer and more complex
      files: ['**/*.test.js', '**/*.test.ts', '**/*.spec.js', '**/*.spec.ts'],
      rules: {
        'max-lines': 'off',
        'max-lines-per-function': 'off',
        'max-statements': 'off',
        'no-magic-numbers': 'off',
      },
    },
    {
      // Configuration files can use require
      files: ['.eslintrc.js', '*.config.js'],
      rules: {
        '@typescript-eslint/no-var-requires': 'off',
      },
    },
  ],
};

// ============================================
// USAGE INSTRUCTIONS
// ============================================

/*
1. Install dependencies:
   npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin

2. Copy this file to your project root as .eslintrc.js

3. Add scripts to package.json:
   {
     "scripts": {
       "lint": "eslint . --ext .js,.ts",
       "lint:fix": "eslint . --ext .js,.ts --fix"
     }
   }

4. Run linter:
   npm run lint        # Check for issues
   npm run lint:fix    # Auto-fix issues

5. Integrate with VS Code:
   Install "ESLint" extension
   Add to settings.json:
   {
     "editor.codeActionsOnSave": {
       "source.fixAll.eslint": true
     }
   }

6. Add to CI/CD:
   - name: Lint
     run: npm run lint

7. Configure with Husky pre-commit hook:
   npx husky add .husky/pre-commit "npm run lint"
*/

// ============================================
// ALTERNATIVE: EXTEND POPULAR CONFIGS
// ============================================

/*
Instead of custom rules, you can extend popular configs:

module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'airbnb-base', // Airbnb style guide
    // or
    'standard', // JavaScript Standard Style
    // or
    'google', // Google style guide
  ],
  rules: {
    // Override specific rules if needed
    'max-len': ['error', { code: 120 }],
  },
};

Install:
npm install --save-dev eslint-config-airbnb-base
npm install --save-dev eslint-config-standard
npm install --save-dev eslint-config-google
*/

// ============================================
// INTEGRATION WITH PRETTIER
// ============================================

/*
Use ESLint for code quality, Prettier for formatting:

1. Install:
   npm install --save-dev prettier eslint-config-prettier

2. Update extends:
   extends: [
     'eslint:recommended',
     'plugin:@typescript-eslint/recommended',
     'prettier', // Must be last to override formatting rules
   ],

3. Create .prettierrc:
   {
     "semi": true,
     "singleQuote": true,
     "trailingComma": "es5",
     "printWidth": 120
   }

4. Update package.json:
   {
     "scripts": {
       "format": "prettier --write .",
       "format:check": "prettier --check ."
     }
   }
*/
