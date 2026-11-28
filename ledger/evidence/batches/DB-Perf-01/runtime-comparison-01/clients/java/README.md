# DB-Runtime-Compare-01 Java preparation client

This is a local comparison client under Plan evidence. It does not change Korda,
its public API, NuGet packages, CI, release rules, or the historical benchmark.
No workflow invokes this client. No long stress run is started by either build
script.

## Status and evidence boundary

The 35 cases are implemented using jOOQ Fluent queries and typed DTOs, with the
explicit historical `raw-sql` case retaining a parameterized raw-SQL entry.
`Contract.java` contains the authoritative manifest's independently validated
expected row counts and FNV digests; expected values are never obtained from the
current database query results. `source-provenance.json` binds the inputs.

Finite correctness and diagnostic receipts have `TimingComparisonEligible:
false`, with reasons. Building a Native Image or passing a short correctness
check does not admit a formal comparison. Independent review, frozen inputs,
workload/environment admission, and the matrix owner's explicit admission file
remain necessary before accepting any 30-minute result. Operational errors are preserved in the receipt and cause
a nonzero command exit. Oracle failures are sticky for the process lifetime and
also produce a sidecar; output paths use create-new semantics.

The final preparation executable is
`30f437c78ff6b9e1dcb16a70f97ab44eee660b07320536dd4fcd4a044402043e`.
Both real Native Image database probes passed 35 independent cases plus 64
warmup operations, with zero oracle failures and exit code zero. The probes
used one worker and never entered offered load. PostgreSQL was stopped cleanly
at `2026-11-28T08:31:22Z`. Three negative admission checks also passed before
opening a database connection. `verification-summary.json` indexes the frozen
source, final build, full receipts, retained ELF/JAR/source archive and known
measurement limits. No 30-minute run was performed during this preparation.

The source deliberately supports only the restored fixture dimensions
(8 tenants, 1,024 orders each, 32 requested/batch rows), persistent connections,
and the original fixed-rate offered-load mode. It rejects unsupported dimensions
or session strategies rather than silently changing the expected workload.

## Pinned toolchain and libraries

| Component | Version / selection |
| --- | --- |
| Java | 25.0.5.1, latest Java 25 security level at preparation |
| GraalVM | Community 25.6.5.1+2.1; official 2026-11-24 feature release |
| Native Image | The distribution's native-image; Serial GC, `-O3`, `-march=x86-64`, no PGO |
| Native build resources | 2 compiler threads, 3 GiB build JVM heap; these do not limit application runtime memory |
| Maven | 3.10.2 |
| jOOQ OSS | 3.21.10 |
| PostgreSQL JDBC | 42.7.15; `prepareThreshold=0` |
| SQLite JDBC | 3.51.3.0; JNI wrapper separately linked to the exact baseline SQLite library |
| JSON parser | jackson-core 2.23.0, streaming parser; no reflective DTO deserialization |
| Native Build Tools | native-maven-plugin 1.1.19 with its reachability metadata |

Oracle's advertised 25i6 download URL returned HTTP 403 in this executor.
The official GraalVM Community release for the same feature/security level was
downloaded and verified against its published SHA-256. This client does not
claim to use Oracle GraalVM. Runtime receipts include the actual Java/vendor/VM
strings and ELF hash. `dependency-lock.json` is generated after a successful
build and records all resolved runtime JAR hashes.
`toolchain-provenance.json` records the official archive URLs and verified
published checksums. `build-identity.json` is written only when the source hashes
before and after the build agree; it binds that source to the actual JAR, ELF,
compiler identity, arguments and reachability metadata archive.

Official sources:

- <https://www.graalvm.org/release-notes/25.6/>
- <https://github.com/graalvm/graalvm-ce-builds/releases/tag/graal-25.6.5.1>
- <https://www.jooq.org/download/>
- <https://jdbc.postgresql.org/download/>
- <https://github.com/xerial/sqlite-jdbc/tree/3.51.3.0>
- <https://graalvm.github.io/native-build-tools/latest/maven-plugin>

## SQLite engine identity

The baseline engine is SQLite 3.51.3. The normal Xerial JAR bundles an engine
compiled with different options, so the benchmark must not load that engine.
`build_sqlite_jni.py` compiles the unmodified Xerial `NativeDB.c` JNI layer and
links it dynamically to the already-built baseline `libsqlite3.so`. It neither
compiles nor patches SQLite. `sqlite-jni-build.json` records the source revision,
commands and both native hashes. JNI headers are generated from the matching
Xerial source with the pinned JDK.

The SQLite command requires both `--sqlite-jni-directory` and
`--sqlite-native-library`. Startup sets the standard Xerial native-library path,
then checks `/proc/self/maps`: exactly one SQLite engine must be mapped and its
real path must equal the explicitly selected library. A bundled or system-engine
fallback is a sticky correctness failure. The receipt records engine version,
source ID, compile options, loaded image hashes and effective pragmas.

## Build, without running a workload

Assume `JAVA_TOOLS` points at the task's `toolchains/java` directory and
`SQLITE_PREFIX` at the restored baseline `toolchains/native-db/sqlite` directory.
Place the official GraalVM and Maven distributions under their pinned names.
Clone the official Xerial `3.51.3.0` tag into
`$JAVA_TOOLS/xerial-sqlite-3.51.3.0`; the JNI builder verifies its exact revision.

```bash
python3 maven_build.py --toolchains "$JAVA_TOOLS"
python3 build_sqlite_jni.py --toolchains "$JAVA_TOOLS" --sqlite-prefix "$SQLITE_PREFIX"
python3 maven_build.py --toolchains "$JAVA_TOOLS" --native
```

The Maven helper reads the existing environment proxy per invocation and, when
necessary, uses a task-local trust store containing the OS's already trusted
public CA certificates. TLS validation remains enabled. Proxy settings are
temporary and are not committed. The first invocation only compiles a JAR; the
third builds a real native executable. No JVM fallback is used as a Native Image
result. The GraalVM 25.6 `--no-fallback` option is deprecated because fallback
support is no longer present; the build log preserves that diagnostic.

### Native Image compatibility metadata

The first executable built from the reviewed source failed during the fixture
metadata query, before any of the 35 business cases. jOOQ's SQL type registry
eagerly creates array types through dynamic `Class.arrayType()` calls; the
selected upstream 3.20.0 reachability metadata omitted those arrays. The observed
first failure was `UShort[]` during `SQLDataType` initialization. The failed ELF
identity, exact stack and build log remain under `verification/native-final/`;
that directory's name does not imply a successful result.

An independent JIT correctness run with GraalVM's metadata agent recorded all
38 array types used by this initializer. Their lookup metadata is included in
`src/main/resources/META-INF/native-image/`; no reflective constructors, jOOQ
implementation patches, SQL changes or DTO shortcuts were added for this fix.
`verification/native-metadata-agent/` retains the actual agent output, finite
run receipt and source-level cause. The metadata-corrected executable and the
later final admission-enabled executable both passed the real Native Image
database checks. The authoritative final receipts are under
`verification/native-campaign-final/`; the earlier intermediate success is
retained under `verification/native-metadata-fixed/`.

Related upstream reports: <https://github.com/jOOQ/jOOQ/issues/19124> and
<https://github.com/oracle/graalvm-reachability-metadata/issues/752>.

## Correctness probe

Copy the shared seed database to a private verification path first. Never run
two database consumers against the shared seed file.

```bash
target/runtime-comparison-java \
  --provider sqlite --connection /absolute/path/private-copy.sqlite \
  --sqlite-jni-directory "$JAVA_TOOLS/sqlite-jni" \
  --sqlite-native-library "$SQLITE_PREFIX/lib/libsqlite3.so" \
  --case mixed --mode prepared --session persistent \
  --concurrency 1 --warmup 64 --verify-only --idle-seconds 0 \
  --output /absolute/path/new-sqlite-correctness.json

target/runtime-comparison-java \
  --provider postgresql \
  --connection 'jdbc:postgresql://127.0.0.1:48277/private_database?user=korda&sslmode=disable' \
  --case mixed --mode prepared --session persistent \
  --concurrency 1 --warmup 64 --verify-only --idle-seconds 0 \
  --output /absolute/path/new-postgresql-correctness.json
```

`--verify-only` runs each of the 35 contracts once per worker and the separately
configured warmup; it never enters the offered-load scheduler. The four write
cases restore their target and verify the full durable row. The output reports
the actual runtime; JIT diagnostics use a distinct route label and collector
identity, never a Native Image/Serial claim.

`verify_native.py --task-root /absolute/path/DB-Runtime-Compare-01 --output
/absolute/path/new-evidence-directory` automates exactly these finite probes,
checks the frozen ELF/source identity, and retains command exit codes and both
JSON receipts. Use it only while holding the campaign owner's exclusive PG
instance ownership. It copies SQLite's seed, uses the task-owned
`db_perf_java_preflight` PG clone, and stops the PG instance it started. It does
not enter the offered-load scheduler or launch a 30-minute run.

### Formal campaign admission

The campaign owner supplies one `--formal-admission /absolute/path/admission.json`
file per database after reviewing the final executable and both Native Image
correctness receipts. The client does not create approval documents. The flat
JSON schema is `DB-Runtime-Compare-01.java-admission.v1`, with these required
fields:

| Field | Required value |
| --- | --- |
| `ApprovedForFormalMeasurement` | `true`, set by the campaign owner |
| `ExecutableSha256` | SHA-256 of the exact executable being run |
| `ContractSha256` | `76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2` |
| `Provider` | `sqlite` or `postgresql`, matching the command |
| `Case`, `Mode`, `SessionMode` | `mixed`, `prepared`, `persistent` |
| `Concurrency` | SQLite 4; PostgreSQL 8 |
| `RequestsPerSecond` | SQLite 3,000; PostgreSQL 3,600 |
| `QueueCapacity`, `Seconds`, `WarmupPerWorker`, `IdleSeconds` | 64, 1,800, 64, 15 |
| `CSharpGcBudgetMiB`, `CgroupRequired`, `JavaMemoryCapBytes` | 192, `false`, `null` |

The application checks both the admission values and its actual arguments against
the fixed matrix. Formal commands must include `--verify`, preserving the
independent 35-case sweep before each worker's separate 64-operation warmup.
The policy bytes' SHA-256 and the executable hash are included
in the result. Additional provenance/evidence fields may be present in the
document. Verification-only, empty-driver and JIT diagnostic runs cannot consume
formal admission. Without admission, offered load requires the explicit diagnostic
flag and remains ineligible for timing comparison.

Only an admitted run that finishes the complete offer/drain/idle sequence, has
successful operations, reconciles every counter, records no business or oracle
errors, and retains the complete time series sets `TimingComparisonEligible:
true`. Existing finite receipts remain finite evidence. This campaign treats
192 MiB as a requested C# GC budget; collector-specific enforcement and actual
RSS must be reported separately. It is not a validated process-memory or RSS
ceiling, and this revised campaign does not require cgroups.

## Restored workload semantics

- All business inputs remain tenant 1. Mutation target is order 1,024. No
  worker-specific sharding, reduced write frequency or write exclusion is used.
- `early-stop` issues a full nine-field query with limit 1,024, materializes only
  three orders, then closes the cursor. Close is inside the operation duration.
- `empty-sum` preserves SQL `NULL`; no `COALESCE(0)` is introduced.
- `nullable-order` uses `CustomerId ASC NULLS FIRST`; `customer-totals` and the
  other specified ascending keys use `NULLS LAST`, as the manifest requires.
- Money remains exact signed cents in the digest. SQLite integer cents and PG
  numeric values are converted using `BigDecimal`, with exact scale checks.
- JSON is parsed into `Settings`, including `Channel` and `Gift`; it is not
  replaced by string slicing or seed-derived values.
- Every related parent remains in input order, including empty groups. Child
  rows are owned DTOs, sorted by child ID before hashing. Row counts count only
  child rows.
- `tx-commit`, `tx-rollback`, `partial-update`, and `stale-conflict` execute real
  full-row reads and updates. The stale write must affect zero rows. Omitted
  fields, NULL and the restored durable full row are checked.
- SQLite controls use explicit `BEGIN IMMEDIATE` plus `COMMIT`/`ROLLBACK`. This
  avoids JDBC's automatic new-transaction-after-commit behavior. PostgreSQL uses
  normal JDBC READ COMMITTED transactions, with completion/retirement before the
  final persisted-state read. Transaction control SQL is separate from Fluent
  query/update construction and is explicitly recorded.

### SQL differences intentionally adopted

The user permits equivalent SQL improvements. The following are explicit:

| Case | Java SQL strategy | Contract preserved |
| --- | --- | --- |
| left-join | Direct LEFT JOIN to customers; removes the unused derived projection and match marker | Identical nullable customer-name DTO and order |
| related | One bounded `IN` query with tenant filter and explicit parent/child order; replaces 32 UNION ALL branches | Same input parent keys, all empty groups, owned child DTOs and exact digest |
| all Fluent queries | jOOQ renders quoting, aliases, casts and dialect pagination | Parameters and relational business results are checked against the frozen oracle |
| raw-sql | Retains the workload's explicit raw SQL case | Same parameterized text DTO contract |

The actual rendered SQL and bind values are captured before measurement.
Prepared mode reuses jOOQ graphs per worker, with no retained JDBC statement or
server-prepared assertion. PG `prepareThreshold=0` matches the historical
Npgsql `MaxAutoPrepare=0` policy. `related` and transaction graphs are rebuilt per
operation. `fetchLazy()` controls application materialization; no claim is made
that pgJDBC does not internally buffer a result (default fetch size is retained).

## Scheduler and measurement

`OfferedLoad.java` ports the original scheduler contract: planned operation
`i` is due at `start + i / rate`; admission is a bounded FIFO attempt and never
waits for capacity. Full queues increment rejection counts. Accepted work drains
completely after the offering deadline. The accounting assertions are:

```text
attempted = planned = sent + rejected
started = sent = succeeded + failed
```

The queue stores job indices/timestamps in preallocated primitive arrays rather
than allocating one Java object per arrival. The producer uses the same coarse
1 ms sleep / short spin strategy as the C# source. JDBC runs on one dedicated
platform thread per worker; its synchronous scheduling is recorded as a runtime
difference, not disguised as .NET async scheduling.

Four 8,192-bin logarithmic histograms preserve the original base-2 / 128
subdivision definition: successful service, successful planned-to-complete,
all-completed planned-to-complete, and planned-to-start. Per-case counters and
planned/sent/started/succeeded/failed/rejected/rows per second are retained.
Overflow of the bounded time-series buffer is marked explicitly.

Client user/system CPU uses `/proc/self/stat` with the actual `CLK_TCK` value;
RSS/HWM/PSS and Java heap figures have separate fields. After all connections
close, the optional idle measurement performs no forced GC. PG server resources
must be captured by the external campaign owner and are not included in client
CPU. Backend PIDs are reported for that association.

Allocated bytes are reported only when the actual runtime supports the process
`ThreadMXBean` allocation counter. Unsupported values are `null`, not zero.
No native-allocation attribution is claimed. GC counters are process scoped;
MXBean collection milliseconds are not labelled as a validated pause histogram.
JFR support is compiled in but no recording is automatically started in a timed
cell. The Java runtime has no imposed application memory cap. The revised C#
policy, including Dapper.AOT, requests a 192 MiB GC budget and does not require
cgroups; actual RSS must be reported without a hard-memory-limit claim. An
in-process SQLite engine and its caches are part of the client's memory use.
The external PostgreSQL server's memory is reported separately.

Historical 30-minute settings, for later admitted execution by the campaign
owner, are SQLite `C4 / R3000 / queue64` and PostgreSQL
`C8 / R3600 / queue64`, `--seconds 1800 --warmup 64 --idle-seconds 15`.
All matrix cells must run serially. No long-run receipt exists merely because
these arguments are documented.
