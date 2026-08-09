# software-ios-runtime-debugging — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-05-31] App Attest never runs under a Debug build: an `#if DEBUG` guard selects the dev-token provider, so a plain Xcode Run silently exercises the wrong auth path — verify attestation via a Release build configuration or an archive, not Cmd-R.
## Domain Knowledge

- [2026-05-31] App Attest stamps dev-provisioned builds with the `appattestdevelop` AAGUID and production with the zero-padded `appattest` AAGUID; a server pinning only prod rejects every Xcode-run device with bad_aaguid, so accept both on staging.
- [2026-07-11] The skill's original scope (stale-build/install/launch proof) never covered classic runtime-performance triage (hangs, crashes, jank, Jetsam, launch-time). Added `references/runtime-performance-triage.md`: Apple's own hang-reporting default is ~250ms (Instruments/MetricKit), which is a different, smaller number than third-party SDKs' own configurable "app hang" thresholds (e.g., Sentry's ~2s default) — don't compare hang rates across tools without confirming they use the same threshold. Jetsam per-device memory limits are not Apple-published; any specific MB figure in the wild is community-derived and should be labeled empirical. Processor Trace requires M4+ Apple silicon or A18-class iPhones (16 and later) — verify the chip cutoff at use-time since Apple has extended hardware-gated Instruments features to new generations before.
## Open Questions

## Consolidated Principles

