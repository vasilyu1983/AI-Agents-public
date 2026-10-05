# Recovery Strategy Design

Purpose: design a recovery capability, not a backup job. Use this when planning data
protection for a production database, reviewing an existing backup setup, or answering
"are we backed up?" with something better than yes.

Grounded in Campbell and Majors, *Database Reliability Engineering* (O'Reilly, 2017),
ch. 7, "Backup and Recovery".

## Table of Contents

- [Frame It as Recovery, Not Backup](#frame-it-as-recovery-not-backup)
- [Failure-Scenario Taxonomy](#failure-scenario-taxonomy)
- [Planned Scenarios](#planned-scenarios)
- [Unplanned Scenarios](#unplanned-scenarios)
- [Scope and Impact Dimensions](#scope-and-impact-dimensions)
- [Building Block 1: Detection](#building-block-1-detection)
- [Building Block 2: Tiered Storage](#building-block-2-tiered-storage)
- [Building Block 3: A Varied Toolbox](#building-block-3-a-varied-toolbox)
- [Building Block 4: Testing](#building-block-4-testing)
- [Tier Mapping: Which Data Gets Which Investment](#tier-mapping-which-data-gets-which-investment)
- [Replication Is Not a Backup](#replication-is-not-a-backup)
- [Design Checklist](#design-checklist)

## Frame It as Recovery, Not Backup

Backups are a means; recovery is the requirement. The distinction is not pedantic — it
changes what you measure and what you test.

> The simple question "Is your database backed up?" is a question that should be
> followed with the response, "Yes, in multiple ways, depending on the recovery
> scenario." A simple yes is naive and promotes a false sense of security that is
> irresponsible and dangerous.
>
> — *Database Reliability Engineering*, ch. 7, p. 122

Start from the availability and durability targets in your SLOs. Two constraints fall
out of them: you must be able to recover inside the uptime budget, and you must capture
data often enough to meet the durability target. A daily backup with transaction logs
living only on node-local storage fails the second constraint — that node dying loses
everything since the last backup.

Two context questions that are easy to miss:

- **Cross-system consistency.** If an order lives in a relational database but triggers
  a workflow held in a queue or key-value store, recovering the database alone can leave
  the workflow orphaned or replayed. Decide what "consistent" means across the whole
  data ecosystem, not per datastore.
- **Application-version skew.** Restoring data written by an older application version
  into a newer one can logically corrupt it. Version your data or know explicitly that
  you have not.

## Failure-Scenario Taxonomy

Enumerate scenarios before choosing tools. DBRE splits them first into planned and
unplanned — a split that matters because it determines how often your team exercises
the recovery path.

### Planned Scenarios

Treating recovery as an emergency-only tool means the team only ever uses it under
stress. Fold it into routine work instead, and you get familiarity plus real timing
data for SLO calibration.

- Building new production nodes and clusters
- Building other environments (dev, integration, operational test, demo)
- ETL and pipeline processes feeding downstream datastores
- Operational tests (capacity and load testing need full datasets; feature testing
  needs subsets, which exercises point-in-time and object-level restore)

Instrument every run — time per stage (uncompress, copy, log apply, verify), backup size
compressed and uncompressed, and throughput pressure on the hardware. This is what tells
you the recovery path is still viable before you need it.

### Unplanned Scenarios

| Scenario | Character | Detection difficulty |
|----------|-----------|----------------------|
| User error | `UPDATE`/`DELETE` without `WHERE`, script run against prod instead of test, right action at the wrong time | Usually immediate, but impact can surface days or weeks later |
| Application errors | A deploy that destructively mutates, removes, or adds incorrect data | Hardest — DBRE calls these "the scariest of the scenarios discussed because they can be so insidious" |
| Infrastructure services | Config management pointing at the wrong environment or pushing bad config | Moderate; can be quiet |
| OS and hardware errors | Corruption along the path from database through caches, filesystems, controllers, disks | Can be silent — see below |
| Hardware failures | Disk, memory, CPU, controller, network device failure; network partitions causing data divergence | Fast, via monitoring |
| Datacenter failures | Cascading network failure, disaster, storage backplane congestion | Fast, but tests every assumption |

On silent corruption: disk ECC corrects small errors and detects errors up to roughly
twice what it can correct, but larger errors are passed to the controller **as good
data** and propagate into backups. DBRE's stance is that this argues for skepticism
about environments where you cannot inspect the implementation, and for checksumming
filesystems such as ZFS where data integrity is critical.

### Scope and Impact Dimensions

Each scenario also carries a scope and an impact level, and the combination determines
the response.

**Locality scope:** single-node/local · cluster-wide · datacenter or multiple clusters.

**Dataset scope:** single object · multiple objects · database metadata (the data is
fine but users, permissions, or file mappings are lost).

**Impact:**

- SLO impacting — application down or majority of users affected
- SLO threatening — some users affected
- Features affected — not SLO threatening

Impact determines the *approach*, not just the urgency: non-SLO-affecting data loss can
be handled slowly and methodically to avoid making it worse, while SLO violations demand
triage and service restoration first, cleanup after.

Multiplying these out:

> With recovery scenario, scope, and impact, we have a potential combination of 72
> different scenarios to consider. That's a lot of scenarios! Too many really to give
> each the level of focus they need. Luckily, many scenarios can utilize the same
> recovery approach. Still, even with this overlap, there is no way that we can fully
> plan for every eventuality. Thus, building a multitiered approach to recovery is
> required to help make sure we have as extensive of a toolkit as possible.
>
> — *Database Reliability Engineering*, ch. 7, p. 122

That is the argument for the four building blocks below: you cannot enumerate every
failure, so you build breadth instead of trying to.

## Building Block 1: Detection

Recovery you start too late is not recovery. User and application errors routinely go
unnoticed for days or weeks — long enough that the good backup has aged out. Detection
is therefore a first-class part of the strategy, not a monitoring afterthought, and it
has a second job: extending the window in which recovery is still possible.

Detection approach by failure class:

- **User error** — remove ad hoc production access. Wrap changes in scripts or APIs that
  support parameterized execution across environments, a dry-run stage with validated
  estimates, a test suite, post-execution validation, soft-delete or easy rollback, and
  logging of every modified row ID. Soft-deletion is what buys the extended recovery
  window.
- **Application errors** — data validation, run downstream of the application rather than
  inside it. Prioritize fast checks on critical components: external pointers to files,
  referential integrity, PII. Make engineers accountable for data quality rather than
  delegating it to the storage engine.
- **Infrastructure services** — compare running infrastructure against golden images on a
  schedule; version infrastructure so drift is detectable.
- **OS and hardware** — mostly covered by log and metric monitoring, but edge cases need
  deliberate work. Block-level checksums are the example: not every filesystem does it,
  and teams with critical data should choose one that does.
- **Hardware and datacenter failures** — standard operational monitoring suffices.

## Building Block 2: Tiered Storage

Different recovery needs want different cost, latency, and durability profiles. One
storage tier cannot serve all of them.

| Tier | Characteristics | Serves |
|------|-----------------|--------|
| Online, high performance | High throughput, low latency, high price; only a few recent copies | Node replacement, capacity addition, fast test environment builds |
| Online, low performance | Large cheap disks, lower throughput; many older copies | Finding and repairing user/application errors that escaped early detection |
| Offline | Tape, Amazon Glacier; off-site, slow to retrieve, vast and cheap | Audit, compliance, business continuity |
| Object storage | API access, object versioning, high availability via replication | Programmatic recovery of individual unstructured objects |

## Building Block 3: A Varied Toolbox

- **Full physical backups** — the fastest full restore, needed at node, cluster, and
  datacenter scope. Requires either a lock for a consistent snapshot or a shutdown. In
  asynchronously replicated environments, take them from the primary where possible;
  replicas cannot be trusted to be in sync. Left uncompressed on fast storage because
  decompression costs recovery time.
- **Incremental physical backups** — bridge from the last full backup forward. Since a
  full backup is expensive in both performance impact and storage, incrementals let an
  older full backup be brought current quickly.
- **Full and incremental logical backups** — portable and good at extracting subsets.
  Not for rapid node recovery; ideal for forensics, moving data between datastores, and
  recovering specific subsets from a large dataset.
- **Object stores** — optimized for recovering specific objects, and reachable by API so
  applications and admin tools can do it programmatically.

Note the physical/logical tradeoff: logical backups are row-by-row rather than file
copies, so both backup and restore are slow and restore pays the full database overhead
of locking and redo/undo generation.

## Building Block 4: Testing

Recovery testing is a deliverable, not a formality. Quarterly or monthly testing leaves
long windows in which backups can silently stop working.

Two approaches, ideally both:

1. **Recovery as an everyday process.** Build integration and test environments from
   backups; regularly replace production nodes from them. This tests continuously and
   produces the timing data needed to calibrate against SLAs.
2. **Continuous restore-and-verify.** Where the environment does not offer enough natural
   rebuilds, run a constant loop restoring the latest backup and validating it.

Validate in tiers, cheap checks first:

- Fast: checksums on schema definition files and object metadata, database instance
  starts successfully, replication thread connects
- Slower: row counts on objects, checksums over insert-only (immutable) data subsets,
  most recent ID in an auto-increment sequence

Capture these validation values *at backup time* so there is something to compare
against. Offsite tiers still need occasional testing even when the rest is automated.

## Tier Mapping: Which Data Gets Which Investment

The four strategies below combine the building blocks. Most systems need more than one.

### Online Fast Storage, Full + Incremental

- **Use cases:** replacing failed nodes, introducing new nodes, building feature
  integration and operations test environments
- **Detection:** monitoring for node/component failure; capacity planning for growth
- **Toolbox:** full and incremental physical backups, left uncompressed for restore speed
- **Retention:** daily full is typically the highest frequency achievable given backup
  latency; about a week of retention is usually more than enough. That means seven
  uncompressed copies plus incremental change data — adjust frequency and retention if
  the capacity or budget is not there
- **Testing:** exercised constantly by integration testing; add daily node
  reintroduction and a continuous recovery process

### Online Slow Storage, Full + Incremental

- **Use cases:** application errors, user errors, corruption repair, operations test
  environments
- **Detection:** data validation — when it fails, engineers use these backups to
  establish what happened and when, and to extract clean data
- **Toolbox:** compressed full and incremental physical backups, plus logical backups
  such as replication logs for recovery flexibility
- **Retention:** a month or longer, enabled by compression and cheap storage. Highly
  dynamic environments need longer, since undetected corruption is likelier
- **Testing:** continuous automated recovery is critical here precisely because real
  recoveries are rare; add periodic game-day runs of specific scenarios such as a single
  table or a data range

DBRE flags this as the messiest tier: there are too many permutations of damage to
pre-plan, and recovery code often has to be written during the incident, which itself
introduces bugs.

### Offline Storage

- **Use cases:** audit and compliance, business continuity
- **Detection:** not a substantial part of this component
- **Toolbox:** compressed full backups
- **Retention:** seven years or more — often a regulatory requirement rather than a
  choice. Not time sensitive; business continuity restores can be staged

### Object Storage

- **Use cases:** application errors, user errors, corruption repair at object granularity
- **Detection:** data validation and user reports
- **Toolbox:** versioned object store with inspection, placement, and retrieval APIs
  exposed to engineers and admin tooling
- **Testing:** because object-level recovery becomes part of the application, standard
  integration testing generally covers it

## Replication Is Not a Backup

> Replication is blind, and can cascade user errors, application errors, and corruption.
> You must look at replication as a necessary tool for data movement and synchronization,
> but not for creating useful recovery artifacts. If anyone tells you that they are using
> replication for backups, give them some side eye and move on. Similarly, RAID is not a
> backup. Rather, it is a redundancy.
>
> — *Database Reliability Engineering*, ch. 7, p. 126

The mechanism is the point: replication faithfully reproduces whatever the primary did,
including the `DELETE` without a `WHERE` clause. A replica is protection against a node
dying, not against a mistake or a corrupt write — those propagate at replication speed.
The same reasoning applies to RAID, to multi-AZ synchronous replicas, and to any storage
redundancy: they defend against hardware loss and nothing else.

Delayed replicas are a partial exception worth knowing — a replica held deliberately
behind the primary gives a window to stop replay after a destructive change. Treat it as
a fast-recovery convenience layered on top of real backups, never as a replacement.

## Design Checklist

- [ ] Recovery targets derived from SLO availability and durability indicators, not from
      backup-job convenience
- [ ] Failure scenarios enumerated across planned and unplanned, with scope and impact
- [ ] Cross-datastore consistency addressed for workflows spanning multiple systems
- [ ] Detection defined per failure class, including the slow-to-surface ones
- [ ] Recovery window extended by soft-deletes, logging, or delayed replicas
- [ ] More than one storage tier in use, matched to the scenarios each serves
- [ ] Both full/incremental physical and logical/object-level recovery paths available
- [ ] Recovery exercised by routine work, not only by drills
- [ ] Continuous restore-and-verify running, with tiered validation checks
- [ ] Validation baselines captured at backup time
- [ ] Restore duration measured often enough to trust the number
- [ ] Nobody on the team believes replication or RAID is the backup
