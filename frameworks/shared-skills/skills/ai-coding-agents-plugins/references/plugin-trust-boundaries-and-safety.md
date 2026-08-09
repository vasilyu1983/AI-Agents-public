# Plugin Trust Boundaries And Safety

## Table Of Contents

- [Design Goal](#design-goal)
- [Install-Time Trust Boundary](#install-time-trust-boundary)
- [Runtime Restrictions](#runtime-restrictions)
- [Validation And Path Safety](#validation-and-path-safety)
- [Policy And Marketplace Controls](#policy-and-marketplace-controls)
- [Recommended Host Rules](#recommended-host-rules)

## Design Goal

Coding-agent plugins can introduce tools, prompts, callbacks, file access patterns, MCP servers, and networked processes. The trust boundary therefore cannot live only inside plugin content. It has to live in the host.

The `claude_code` source demonstrates a good split:

- plugin installation and enablement are explicit user or policy actions
- plugin manifests are validated before load
- some capability classes are allowed only at the manifest level
- nested agent files are not allowed to quietly escalate certain powers
- policy and marketplace rules can block sources before the plugin becomes active

## Install-Time Trust Boundary

The strongest pattern to copy is this: trust decisions happen when a plugin is installed or enabled, not when a nested file is first discovered.

You can see this in two places:

- the UI warns users to trust a plugin before installing, updating, or using it
- plugin agents in `loadPluginAgents.ts` intentionally ignore `permissionMode`, `hooks`, and `mcpServers` declared inside agent files

That second rule matters. It prevents a third-party plugin from hiding elevated behavior inside a single agent file under `agents/`.

Use that same boundary:

- manifest-level capabilities are the install-time trust surface
- nested files may configure allowed behavior inside those capabilities
- nested files should not be allowed to introduce new high-risk capability classes

## Runtime Restrictions

The `claude_code` plugin runtime places important restrictions on plugin content:

- plugin-provided agents can declare tools, memory, isolation, model, effort, and other bounded metadata
- plugin-provided agents cannot silently add per-agent hooks or MCP servers
- built-in plugins are still treated as plugins in the UI and registry, but their enablement and trust model remains host-controlled

The design lesson is clear:

- let plugins contribute bounded runtime behavior
- keep privileged capability creation in host-controlled or manifest-controlled layers
- document which fields are ignored for third-party plugin content

Do not treat "a Markdown file with frontmatter" as automatically trusted just because it lives under a plugin directory.

## Validation And Path Safety

The validation layer in `validatePlugin.ts` and `schemas.ts` is doing real security work, not just linting:

- path traversal checks reject `..` in plugin component paths
- reserved source names such as `inline` and `builtin` are blocked for authors
- official marketplace impersonation is checked through reserved names and source validation
- runtime load is tolerant, but author-facing validation is stricter so typos and schema drift surface early

That is the right split for coding-agent plugin hosts:

- runtime parsing should be resilient enough not to crash sessions
- author tooling should be strict enough to catch dangerous or broken manifests early
- identity and path validation should happen before any component is activated

## Policy And Marketplace Controls

The source also shows that trust is not only about the user:

- org policy can force-disable plugins
- marketplaces can be allowlisted or blocklisted
- official marketplace names are protected against impersonation
- plugin install and enable commands honor policy and source restrictions

For enterprise or team-grade coding-agent runtimes, copy this model:

- user settings decide ordinary enablement
- policy settings can override user settings
- marketplace and source restrictions apply before install and enable
- the runtime should explain whether a plugin is disabled by the user, blocked by policy, or unavailable for source reasons

## Recommended Host Rules

Use these as defaults when designing a new coding-agent plugin runtime:

- treat plugin trust as a host policy problem, not a plugin author promise
- keep install-time trust separate from runtime component loading
- block nested content from introducing high-risk capability classes outside manifest-approved surfaces
- validate paths, reserved names, and source identity before activation
- namespace plugin-provided components so the user can audit provenance
- keep a separate built-in plugin registry even if built-ins eventually normalize into the same loaded-plugin shape
- make disable and uninstall remove future behavior immediately, even if some capabilities need a later full reload to fully refresh registries

If the runtime cannot safely support third-party plugins, do not fake it. Support built-ins or repo-local extensions only, and keep the trust boundary honest.
