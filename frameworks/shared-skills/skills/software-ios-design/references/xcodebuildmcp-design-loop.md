# XcodeBuildMCP Design Loop

Use this reference when the user wants design fixes proved in Simulator instead of explained abstractly.

## What to Prefer

- Prefer repo-local `.xcodebuildmcp/config.yaml` for deterministic project, scheme, simulator, and bundle defaults. If the git root differs from the Xcode project root, pass `--project-path` explicitly to `bootstrap-xcodebuildmcp.sh`.
- Prefer `simulator build-and-run` for the main edit-review loop.
- Prefer screenshots, UI snapshots, and logs over speculative layout advice.
- Prefer standard controls and current iOS navigation chrome before custom glass or custom containers.

## Recommended Loop

1. Verify XcodeBuildMCP is available.
2. Check or scaffold `.xcodebuildmcp/config.yaml`.
3. Build and run on the intended simulator.
4. Navigate to the target screen.
5. Capture a screenshot and inspect the visible hierarchy.
6. Review spacing, typography, contrast, hierarchy, and navigation against Apple guidance.
7. Apply the smallest SwiftUI fix that addresses the issue.
8. Rebuild, re-run, and compare screenshots.

## Suggested CLI Flow

```bash
./scripts/bootstrap-xcodebuildmcp.sh --scheme MyApp --simulator-name "iPhone 17 Pro"
./scripts/run-ios.sh --scheme MyApp
./scripts/capture-screenshot.sh screenshots/before.png
```

Then review the screenshot, adjust the SwiftUI view, and re-run:

```bash
./scripts/run-ios.sh --scheme MyApp
./scripts/capture-screenshot.sh screenshots/after.png
```

## What to Inspect

- Is the screen using native structure for the task?
- Does the most important content win first attention?
- Are title, body, and metadata clearly separated by text style and spacing?
- Do materials improve hierarchy without hurting legibility?
- Does light and dark appearance preserve contrast?
- Are toolbar, sheet, and tab surfaces behaving like standard iOS chrome?

## Common Fix Patterns

- Replace fixed `font(.system(size: ...))` usage with text styles.
- Replace hardcoded black or white surfaces with semantic backgrounds or materials.
- Reduce dashboard clutter by promoting one hero area and demoting secondary cards.
- Move actions into native toolbar, swipe actions, or context menus when the screen feels crowded.
- Convert custom segmented navigation into tab views or standard navigation when the structure is really app-level.

## Proof Expectations

Prefer artifacts over summary:

- build/run output
- screenshot before
- screenshot after
- relevant log lines if layout or navigation warnings appear
- short explanation of what changed and why it is more native
