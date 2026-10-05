---
paths:
  - "**/*.kt"
description: Coroutine cancellation rule for Kotlin code.
owner: skills/universal/software-android-native/SKILL.md
---
Extends common/errors.md.
- Never swallow `CancellationException`; catch and rethrow it before any broad `catch (e: Throwable)` or `catch (e: Exception)`.
- Enforce this in the project's CI with a static analyser, such as detekt.
Why and procedure: skills/universal/software-android-native/references/coroutine-and-compose-recipes.md#retry-with-backoff
