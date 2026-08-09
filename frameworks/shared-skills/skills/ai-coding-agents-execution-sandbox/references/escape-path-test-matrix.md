# Escape-Path Test Matrix

Checklist of sandbox escape attacks to verify before shipping any execution sandbox. Run against every new sandbox configuration, every interpreter upgrade, and every network-policy change.

---

## How to Use

For each row: mark **Status** as `pass`, `fail`, or `skip` (with reason). A sandbox is not shippable until all non-skipped rows are `pass`. Re-run after any change to the allowlist, mount points, or interpreter set.

---

## 1. Symlink Attacks

Goal: traverse outside the allowed filesystem root by following symlinks.

| ID | Attack | Description | Expected Result | Resolution if Failing |
|----|--------|-------------|-----------------|----------------------|
| SYM-01 | Absolute symlink outside sandbox root | Create a symlink pointing to `/etc/passwd` inside the sandbox work dir, then read it | Read blocked by mount namespace or realpath check | Add realpath normalization before every file open; reject paths resolving outside the allowed tree |
| SYM-02 | Relative symlink traversal (`../../../`) | Create a symlink with a `..`-heavy target pointing to `/etc/shadow` | Blocked | Resolve symlinks before path permission check; do not check the link itself |
| SYM-03 | Symlink to a device file | Create a symlink targeting `/dev/sda` inside the sandbox | Blocked — device file outside allowed types | Disallow device-type files in allowed path list; mount with `nodev` |
| SYM-04 | Symlink chain to allowed path that later escapes | Create a chain where the final target escapes the sandbox root | Blocked at chain resolution | Limit symlink depth (e.g. ≤ 8) and re-check final target after each hop |

---

## 2. Shell and Interpreter Wrappers

Goal: escape by invoking a different binary that bypasses the allowlist.

| ID | Attack | Description | Expected Result | Resolution if Failing |
|----|--------|-------------|-----------------|----------------------|
| INT-01 | Calling an unlisted interpreter via PATH | Invoke `perl` (not in allowlist) to shell out to a host command | Blocked — execve denied for unlisted binary | Enforce execve allowlist via seccomp or ptrace; PATH alone is insufficient |
| INT-02 | Invoking interpreter via absolute path | Run an unlisted interpreter using its full path rather than its name | Blocked if binary not in allowlist | Allowlist must be path-based, not name-based |
| INT-03 | Using `env` to indirectly exec | Use the `env` utility to launch an unlisted interpreter | Blocked | `env` itself should be scrutinized; deny exec of unlisted binaries launched from it |
| INT-04 | SUID binary escalation | Call any SUID binary present in the sandbox image | No SUID binaries present | Build images with zero SUID binaries; mount with `nosuid` |
| INT-05 | Script shebang bypass | Write a script whose shebang line points to an unlisted interpreter | Blocked — shebang interpreter not in allowlist | Shebang execution must respect the interpreter allowlist |

---

## 3. Environment Variable Injection

Goal: manipulate sandbox behavior by injecting or overriding env vars.

| ID | Attack | Description | Expected Result | Resolution if Failing |
|----|--------|-------------|-----------------|----------------------|
| ENV-01 | `LD_PRELOAD` injection | Set `LD_PRELOAD` to a hostile shared library before exec | Ignored — `LD_PRELOAD` stripped from child env | Strip `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT` before exec |
| ENV-02 | `PYTHONPATH` / `NODE_PATH` injection | Override module search path to a directory containing a hostile module | Hostile module not loaded | Reset or whitelist interpreter-specific path vars |
| ENV-03 | `HOME` override to writable path | Set `HOME=/tmp`; tools that auto-write to `~/.config` now write outside sandbox | Writes contained inside sandbox root | Validate `HOME` and `XDG_*` vars; map them to sandbox-scoped paths |
| ENV-04 | `TMPDIR` redirect outside sandbox | Point `TMPDIR` to a host path mounted read-write | Writes land inside sandbox | Override `TMPDIR` to a sandbox-internal temp dir |
| ENV-05 | `PATH` injection of hostile binary | Prepend `/tmp` to `PATH`; place a hostile shim named after a trusted binary | Shim blocked by execve allowlist | Enforce execve allowlist; do not rely solely on `PATH` ordering |

---

## 4. Package-Manager Network Calls

Goal: exfiltrate data or fetch hostile packages via package-manager side channels.

| ID | Attack | Description | Expected Result | Resolution if Failing |
|----|--------|-------------|-----------------|----------------------|
| NET-01 | `pip install` to arbitrary registry | Install from a non-approved index URL | Blocked — outbound HTTP to non-approved host denied | Network egress policy: allow only approved registry hosts; use `--no-index` flag by default |
| NET-02 | `npm install` with `postinstall` script | Install a package whose `postinstall` runs a network call | Network call blocked | Both exec and network allowlists must be enforced during install |
| NET-03 | `cargo fetch` to unapproved registry | Run `cargo fetch` when crates.io is not approved | Blocked or routed through approved mirror | Add approved registries to network allowlist; block others |
| NET-04 | DNS exfiltration via package registry lookup | Craft a package name that encodes data in its DNS query | DNS to non-approved resolver blocked | Block DNS to non-approved resolvers; use internal DNS with logging |
| NET-05 | Build-time arbitrary code via `setup.py` | Install a package whose build script calls out to the network | Blocked by exec allowlist or network block | Combine exec and network allowlists; pre-vet wheels and disable network during install |

---

## 5. Additional Attack Surface (extend as needed)

| ID | Area | Note |
|----|------|------|
| PROC-01 | `/proc` self-maps | Ensure `/proc` is not mounted or is mount-masked |
| PROC-02 | Ptrace of sibling process | Deny `ptrace` via seccomp `PTRACE_ATTACH` block |
| FS-01 | Bind-mount inside sandbox | Deny `mount` syscall via seccomp |
| FS-02 | `chroot` / `pivot_root` inside sandbox | Deny via seccomp |
| SOCK-01 | Unix domain socket to host | Only permit sockets within sandbox network namespace |

---

## Pass Criteria

A sandbox passes this matrix when:
- Every `SYM-*` and `ENV-*` row returns the expected block.
- Every `INT-*` row returns a block for binaries absent from the interpreter allowlist.
- Every `NET-*` row returns a block or redirect through the approved egress policy.
- No test results in data exfiltration, privilege escalation, or filesystem access outside the sandbox root.
