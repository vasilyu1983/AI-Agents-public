# Sandbox Policy Format

Documents the canonical format for expressing an execution sandbox's interpreter allowlist and filesystem/network policy. This format is runtime-agnostic: it describes what a policy must specify; translating it to an enforcement backend (an LSM such as Landlock, AppArmor, or macOS Seatbelt profiles; seccomp filters; mount namespaces; or container OCI specs) is a separate step. Each field must map to a backend that can actually check it; see the **Enforced by** column in the Field Reference.

## Table of Contents

- [Policy File Structure](#policy-file-structure)
- [Field Reference](#field-reference)
- [Common Traps](#common-traps)

---

## Policy File Structure

A sandbox policy is a single TOML file (or equivalent JSON/YAML) stored at `.agent/sandbox-policy.toml` (project-level) or `~/.agent/sandbox-policy.toml` (user-level). Merge the scopes per value type: scalars take the higher-trust source (managed, then user, then project), lists merge, and `denied` entries from any source always apply. A project file may narrow the policy but must never widen user or managed policy; a repo cannot grant itself sandbox capability.

```toml
# sandbox-policy.toml

[meta]
version = "1"
description = "Sandbox policy for the coding-agent session"

# ── Interpreter allowlist ──────────────────────────────────────────────────────
# Each entry specifies a binary path (exact) that may be exec'd.
# Glob paths are NOT supported — exact paths only, to prevent wildcard escapes.
# The list is checked against the resolved realpath of the target binary.
#
# Trap: listing a directory rather than a binary allows any binary inside it.
# Resolution: always list the specific binary path.

[[interpreters]]
path    = "/usr/bin/bash"
version = ">=5.0"          # advisory; enforced only if version_check = true below

[[interpreters]]
path    = "/usr/bin/python3"
version = ">=3.11"

[[interpreters]]
path    = "/usr/bin/node"
version = ">=20.0"

[[interpreters]]
path    = "/usr/local/bin/rg"   # ripgrep — read-only tool, no shell

[interpreters_policy]
version_check   = false   # set true to enforce version constraints above
deny_unlisted   = true    # deny exec of any binary not in [[interpreters]]
shebang_follows = true    # shebang interpreter must also be in allowlist

# ── Filesystem policy ─────────────────────────────────────────────────────────
# allowed_read  : paths the agent may open for reading
# allowed_write : paths the agent may open for writing (implies read)
# denied        : explicit deny; takes precedence over allowed_* above

[filesystem]
sandbox_root     = "/sandbox"                # all relative paths are anchored here
resolve_symlinks = true                      # always resolve symlinks before checking
max_symlink_depth = 8

allowed_read  = [
  "/sandbox",
  "/dev/null",           # device nodes: mount /dev with nodev and re-open only these
  "/dev/zero",
  "/dev/urandom",
  "/usr/lib",
  "/usr/share",
  "/etc/localtime",
  "/etc/resolv.conf",    # DNS resolver lookup only
]

allowed_write = [
  "/dev/null",
  "/sandbox/work",
  "/sandbox/tmp",
]

denied = [
  "/etc/passwd",
  "/etc/shadow",
  "/proc",
  "/sys",
  "/root",
  "/home",
]

# ── Network policy ────────────────────────────────────────────────────────────
# egress_allow : CIDR or hostname patterns permitted for outbound connections
# dns_resolvers: only these resolvers may be queried
# Trap: allowing "*.pypi.org" permits subdomain takeover; use exact hostnames.
# Resolution: list exact hostnames or narrow CIDR ranges.

[network]
allow_egress = false          # default deny; entries below override per-host

[[network.egress_allow]]
host    = "pypi.org"
port    = 443
protocol = "tcp"

[[network.egress_allow]]
host    = "files.pythonhosted.org"
port    = 443
protocol = "tcp"

[[network.egress_allow]]
host    = "registry.npmjs.org"
port    = 443
protocol = "tcp"

[network.dns]
resolvers        = ["127.0.0.1"]   # internal resolver only
log_queries      = true            # detect encoded-name exfiltration from logs; resolver restriction is the control

# ── Environment variable policy ───────────────────────────────────────────────

[env]
# Variables to strip before exec (injection vectors)
strip = [
  "LD_PRELOAD",
  "LD_LIBRARY_PATH",
  "LD_AUDIT",
  "PYTHONPATH",
  "NODE_PATH",
  "RUBYLIB",
  "PERL5LIB",
]

# Variables to force-set (override anything the caller provides)
[env.force]
TMPDIR = "/sandbox/tmp"
HOME   = "/sandbox/home"
PATH   = "/usr/local/bin:/usr/bin:/bin"
```

---

## Field Reference

### `[interpreters_policy]`

A declared field is not an enforced field. Every row names what enforces it (kernel backend, proxy, runner, or nothing), and every enforced field needs a fail-closed test proving the backend applied it. A field whose enforcer is absent at runtime — domain rules with no active proxy, a missing backend binary that falls back to unsandboxed execution — must fail startup, not run silently.

| Field | Type | Default | Meaning | Enforced by |
|-------|------|---------|---------|-------------|
| `version_check` | bool | `false` | If `true`, reject a binary whose reported version does not satisfy the `version` constraint | Runner pre-exec check (advisory; a binary can misreport) |
| `deny_unlisted` | bool | `true` | Reject `execve` for any binary not in `[[interpreters]]` | A path-aware mechanism: LSM, seccomp user-notify, ptrace, or `noexec` mounts plus one bin root. Not plain seccomp |
| `shebang_follows` | bool | `true` | A script's shebang interpreter must also appear in `[[interpreters]]` | The same exec enforcer (the kernel execs the shebang interpreter) |

### `[filesystem]`

| Field | Type | Meaning | Enforced by |
|-------|------|---------|-------------|
| `sandbox_root` | string | All relative paths resolved against this root | Mount namespace or LSM |
| `resolve_symlinks` | bool | Resolve symlinks before permission check (must be `true`) | Runner path check; the kernel mount view is the backstop |
| `max_symlink_depth` | int | Maximum symlink chain length before abort | Runner path check |
| `allowed_read` | string[] | Paths open for read (prefix match after realpath) | Mount namespace or LSM |
| `allowed_write` | string[] | Paths open for write (implies read) | Mount namespace or LSM |
| `denied` | string[] | Explicit deny; overrides `allowed_*` | Mount namespace or LSM; device nodes via a `nodev` mount |

### `[network]`

| Field | Type | Meaning | Enforced by |
|-------|------|---------|-------------|
| `allow_egress` | bool | Master egress switch; `false` = default deny | Network namespace with no route except the proxy |
| `egress_allow[].host` | string | Exact hostname (no globs) | Egress proxy (hostname only unless it terminates TLS) |
| `egress_allow[].port` | int | TCP/UDP port | Egress proxy |
| `egress_allow[].protocol` | string | `"tcp"` or `"udp"` | Egress proxy |
| `dns.resolvers` | string[] | Permitted DNS resolver IPs | Network namespace or proxy |
| `dns.log_queries` | bool | Log all DNS queries for audit | The internal resolver |

---

## Common Traps

**Trap:** Denying all of `/dev` breaks ordinary tools that write to `/dev/null` or read `/dev/urandom`.
**Resolution:** Mount `/dev` with `nodev` semantics and re-open only `/dev/null`, `/dev/zero`, and `/dev/urandom`.

**Trap:** Listing `/usr/bin` in `allowed_read` exposes all binaries to read and copy.
**Resolution:** Only include specific binaries in `[[interpreters]]`; do not add interpreter directories to `allowed_read`.

**Trap:** Using glob patterns for `egress_allow` hosts.
**Resolution:** Use exact hostnames only. Globs allow subdomain takeover and can be exploited via crafted DNS.

**Trap:** Forgetting to strip `LD_PRELOAD` before exec allows attacker-controlled shared libraries to run inside the allowed binary.
**Resolution:** The `[env].strip` list is mandatory; do not omit it even for "trusted" binaries.

**Trap:** Symlink-resolved path falls inside `allowed_write` but the symlink target is outside the sandbox root.
**Resolution:** `resolve_symlinks = true` and check resolved path against `sandbox_root` prefix before allow.
