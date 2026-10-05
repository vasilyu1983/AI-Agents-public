---
paths:
  - "**/*.swift"
description: Price display and currency formatting rules for Swift code.
owner: skills/universal/software-ios-native/SKILL.md
---
Extends common/coding-behavior.md.
- Never hardcode a price; show StoreKit's `product.displayPrice`.
- Never format currency by hand, such as `String(format: "£%.2f", …)`; use a `NumberFormatter` with an explicit `currencyCode` and the current locale.
Why and procedure: skills/universal/software-ios-native/SKILL.md#quick-reference
