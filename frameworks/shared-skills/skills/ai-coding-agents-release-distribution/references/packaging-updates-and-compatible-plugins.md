# Packaging, Updates, And Compatible Plugins

Treat a coding-agent CLI as a distributed product, not just a local binary.

## Packaging questions to answer early

- how the CLI is installed
- whether dependencies are embedded or discovered dynamically
- whether plugins ship in-tree, from a marketplace, or from local paths
- how enterprise-managed installs differ from self-serve installs

## Update channels

Common channels:

- stable
- beta
- nightly
- enterprise-pinned or managed

Each channel should define:

- who receives it
- how fast it rolls out
- whether auto-update is allowed
- what rollback path exists

## Plugin compatibility

Keep separate compatibility contracts for:

- core runtime API
- plugin manifest shape
- plugin capability negotiation
- cached plugin assets

Do not let “plugin installed successfully” imply “plugin is semantically compatible.”

## Edge cases

- **Marketplace lag**: a plugin built for the previous core version may still install but behave incorrectly.
- **Partial upgrades**: cached plugin bundles or generated metadata may survive an upgrade and need a compatibility check at startup.
- **Managed enterprise builds**: channel pinning and plugin allowlists may intentionally lag the public release cadence.
- **Remote runtimes**: client and server versions may differ and need explicit negotiation rather than optimistic assumptions.

## Practical tip

The runtime should detect plugin or cache incompatibility before a user starts a session, not halfway through a task.
