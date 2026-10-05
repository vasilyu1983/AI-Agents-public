---
paths:
  - "**/Info.plist"
  - "**/AndroidManifest.xml"
  - "**/network_security_config.xml"
description: Cleartext-traffic and trust-anchor rules for iOS and Android app config.
owner: skills/universal/software-security-appsec/SKILL.md
---
Extends common/security.md.
- Never set `NSAllowsArbitraryLoads` to true; scope any ATS exception to a named domain under `NSExceptionDomains`, and record the reason.
- Set `cleartextTrafficPermitted="false"` in the base config; never ship `android:usesCleartextTraffic="true"` in a release manifest.
- Trust user-installed CAs only inside `<debug-overrides>`, never in `<base-config>`.
Why and procedure: skills/universal/software-security-appsec/assets/mobile/template-mobile-security.md#network-security
