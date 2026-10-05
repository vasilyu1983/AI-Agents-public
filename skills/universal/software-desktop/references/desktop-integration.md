# Desktop Integration Concerns

Platform-convention guidance for file system access, tray and menus, native integrations, and offline-first data. Hostile-input and duplicate-launch traps for protocol handlers and file associations are in [../SKILL.md](../SKILL.md#known-traps).

**File system access**:
- Use save/open dialogs via framework APIs (never raw `fs` in renderer).
- Implement recent files list using platform conventions.
- Register file associations for custom file types in installer config.

**System tray and menu bar**:
- System tray for background-running apps; respect platform conventions (macOS uses menu bar, Windows uses system tray).
- Build native menus with keyboard shortcuts that match platform expectations (Cmd on macOS, Ctrl on Windows/Linux).

**Native integrations**:
- Notifications: use OS notification APIs, respect Do Not Disturb / Focus modes.
- Global shortcuts: register sparingly, avoid conflicts with OS shortcuts.
- Protocol handlers / deep links: register custom URL schemes (`myapp://`) for OAuth callbacks and cross-app linking.
- Drag-and-drop: support file drops on app icon (macOS) and window content.
- Clipboard: read/write with proper content type handling (text, HTML, images).
- Multi-window management: track window state, restore positions, handle multi-monitor setups.

**Offline-first**:
- Desktop apps are offline by default. Design data sync, not data fetch.
- Use local storage (SQLite, IndexedDB, or app-specific files) as the source of truth.
- Sync to cloud when connectivity is available; handle merge conflicts.
