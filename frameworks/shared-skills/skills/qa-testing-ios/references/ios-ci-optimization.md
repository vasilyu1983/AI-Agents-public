# iOS CI Optimization

This reference was split for clarity to keep CI guidance smaller and less brittle.

Use:

- [ios-ci-general.md](ios-ci-general.md) for provider-neutral iOS CI patterns
- [ios-ci-github-actions.md](ios-ci-github-actions.md) for GitHub Actions specifics

Why this changed:

- hosted macOS labels, Xcode versions, and simulator runtimes drift quickly
- provider-specific pinning ages faster than the core iOS testing workflow
- the main skill should stay portable across GitHub Actions, Xcode Cloud, and self-hosted macOS

Before copying any CI example, verify:

- current Xcode version and release notes
- current runner image labels and installed software
- current simulator runtimes available in that CI environment
