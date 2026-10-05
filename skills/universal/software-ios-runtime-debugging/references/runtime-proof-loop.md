# Runtime Proof Loop

Use this exact order when runtime truth is unclear:

1. Discover the entrypoint:
   workspace or project, scheme, configuration, destination, bundle ID.
2. Build the app.
3. Inspect the built `.app` bundle:
   confirm `Info.plist` and executable presence.
4. Preserve the reproduction: launch inputs, redacted logs, installed version/UUID, and relevant local-state evidence.
5. Replace/install the exact successful build artifact while retaining the data container where supported.
6. Launch the fresh install.
7. Capture one proof artifact:
   screenshot, UI hierarchy, or launch logs.
8. Only then interpret UI, auth, API, or visual issues.

If replacement fails, first distinguish packaging/signing errors from persisted-state or migration defects. Escalate to a scoped state reset or uninstall only after preserving needed evidence and local data; record which reset changes the symptom.
