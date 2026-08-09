# Runtime Proof Loop

Use this exact order when runtime truth is unclear:

1. Discover the entrypoint:
   workspace or project, scheme, configuration, destination, bundle ID.
2. Build the app.
3. Inspect the built `.app` bundle:
   confirm `Info.plist` and executable presence.
4. Uninstall any stale installed copy from the target simulator or device.
5. Install the fresh build artifact.
6. Launch the fresh install.
7. Capture one proof artifact:
   screenshot, UI hierarchy, or launch logs.
8. Only then interpret UI, auth, API, or visual issues.

Do not skip the uninstall step when the symptom is “the app still shows the old screen.”
