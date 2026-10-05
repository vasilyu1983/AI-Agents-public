# iOS Runtime Debug Request

- Goal:
  prove whether the current iOS build really installs and launches on the intended simulator or device
- Project facts:
  workspace or project path, scheme, configuration, destination, bundle ID if known
- Current symptom:
  stale UI, install failure, missing executable, simulator drift, wrong screen, auth mismatch after sign-in
- Proof required:
  build success, built `.app` path, fresh uninstall/install/launch result, screenshot or launch logs
- Constraints:
  XcodeBuildMCP available or unavailable, XcodeGen in use, simulator already booted or not
