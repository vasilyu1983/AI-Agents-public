# CI Troubleshooting Checklist

- Identify first failed NUKE target and stop at that boundary.
- Confirm prerequisite targets executed (`DependsOn`) and in correct order (`After`).
- Confirm runtime gates (`OnlyWhenDynamic`) did not skip required targets.
- Inspect test filters for category drift or typos (`ApiTest`, `DbTests`, `ComponentTests`).
- Verify Docker prerequisites (daemon availability, auth, registry connectivity).
- Verify digest extraction from push output is still valid.
- Verify `deploy.env` path differs correctly for local vs CI.
- Verify artifact directories are persisted before cleanup targets run.
- Re-run failing target with elevated verbosity to isolate root cause.

