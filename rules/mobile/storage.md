---
paths:
  - "**/*.swift"
  - "**/*.kt"
description: Token and credential storage rules for iOS and Android code.
owner: skills/universal/software-security-appsec/SKILL.md
---
Extends common/security.md.
- On iOS, store tokens and credentials only in the Keychain, and set `kSecAttrAccessible` explicitly on each item.
- Never store tokens or credentials in `UserDefaults`, plist files, or an unencrypted database.
- On Android, encrypt them with a non-exportable Android Keystore key, and persist only the ciphertext and IV.
- Check the status of each Keychain write; a silent failure leaves an old token in place.
Why and procedure: skills/universal/software-security-appsec/assets/mobile/template-mobile-security.md#secure-data-storage-swift
