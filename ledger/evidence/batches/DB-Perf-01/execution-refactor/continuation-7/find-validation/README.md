# Private complete-key Find: finite correctness and integration evidence

The Find author completed the selected private-shape implementation, finite
native and Native AOT correctness checks, and a native integration check with the
three previously reviewed PostgreSQL transaction-proof commits. This directory
preserves all available author logs and source snapshots, including failed
attempts. It does not grant performance, final package-consumption, CI, merge or
publication acceptance.

## Source identities and scope

| Input | Exact identity | Meaning |
|---|---|---|
| Baseline | Korda `47fe650dfed5d7bba1c4d74c4a127c5d08b66082` | Original production Find body used by the literal test oracle. |
| Find-only commit | `dc235553309e1f5c282fd530fabd225204070d05`, tree `080875d44e84bc991e462c95598f40c007ace0f8` | 25 changed source files, complete final patch and source blobs are archived. |
| Find + PostgreSQL integration | `583ef70932508ab58333e5f1472a99ed576acc1d`, tree `cc4742f90ee9f47e288cb22391c1d37cc2a2b4cd` | Clean committed source for the native transaction/protocol gate. |
| PostgreSQL originals | `4169adc70baf43c9f6f99e4fe09e76216b451055`, `7db7050e76d1567378165fc39e2c9bc44db97230`, `3713d666de61bace1c83720e9de71a477d91773e` | Cherry-picked locally as `bd9f288a505c177f2522d63801dbe217048d2c21`, `c5d4f9b6b5f5a7d10cc138207a1b502a0b349c2a`, `583ef70932508ab58333e5f1472a99ed576acc1d`. |
| Independent review | Plan `14960056b810649b15f6d25fd24fcf86df3ce124` | Fixed review text and its original rehash receipt are archived. Reviewer read source/logs and rehashed; author ran the checks. |

The Find-only final checks ran on the exact worktree content subsequently
committed as `dc23555`. The final commit did not yet exist when those binaries
were built; this record does not claim it was embedded in their informational
revision. The 25 committed blob hashes, full final patch, raw logs and six local
artifact hashes bind that content. The independently rebuilt public candidate
and its package consumers are separate root-owned gates.

At integration receipt readback, the root had advanced to
`040911c5abdee740c0cd9fbf8295bf511c9cc69d`, tree
`bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. Its differences from the integration
source were the local FFI diagnostic inventory and the later package export
inventory closure correction. The root had previously reported public
`cb233a7a60dc9e9ef2110811d78db11b1c009438`, tree
`0ea8d431f2d322dc9278e516da99d084413add7f`. Neither identity is silently treated
as the source of this author's earlier checks. The `NWPKG005` package failure,
inventory correction and rerun belong to the root's package evidence.

## Implemented path and retained contracts

The private bit-29 `db.find.shape.v1` factory compiles a complete ordered-key
equality query with its full projection and existing terminal-3 semantics.
Source capability/export closure follows the other current private extensions;
the frozen 42 declarations remain unchanged. No public prepared capability is
required or conferred by the private plan.

The source LRU retains that immutable plan by exact managed Table reference,
with independent entry and conservative retained-byte limits. Same metadata
cannot substitute another mapper. Each caller has its own lease through
retirement; eviction and source close release only the cache reference. Private
ordinal parameter definitions reuse the canonical parameter-schema writer and
consume no public parameter IDs. The arena and plan share the registered
projection. The cache retains no Session, connection or physical statement.

Repeated Find calls copy the already owned key snapshot into one execution
values frame and reuse the existing cursor-pull, TypedStream, DTO-reader and
retirement paths. The former per-call production Fluent/NWQC builder is removed;
its exact body has a live caller only in the correctness oracle. Private Find
also bypasses the general native ShapeCache because it already retains this
exact compilation. Native checks prove two Find executions leave that cache at
zero and ordinary/Prepare executions still enter it.

Admission preserves the original invalid-key/open/cancellation ordering and
the original model-before-key order on a cache miss. Lightweight scalar counts
retain per-key Column/Value/equality/WHERE quota order, with root expanded count
one. The factory returns actual fixed logical bytes separately from retention
charge. Checked managed admission occurs before execution-frame allocation or
returning a Task, with native rechecking before dispatch. It does not recreate
a command tape. Actual baseline errors remain distinct: oversized expression
frame `ArgumentException`, query quota `InvalidState`, metadata capacity
`ResourceLimit`; their synchronous boundaries are checked against old Find.

## Observed final gates

| Gate | Exact observed result | Archived raw evidence |
|---|---|---|
| Find-only native queries | 1,017 checks; 52 SQL/ordered-argument goldens | `raw/query-tests-06.log`, `raw/build-09.log` |
| Find-only Release Linux x64 Native AOT, real SQLite and isolated PostgreSQL | 1,152 assertions; 118 actual managed retirements | `raw/publish-06.log`, `raw/orm-run-06.log` and its three server/consumer logs |
| Find segment within that final AOT run | SQLite 192; PostgreSQL 192 | Both provider lines and the overall suite report owner indexes `[0..5,8,9]` at zero. |
| ABI/signature/format | 42 frozen signatures unchanged; additive Find signature; both actual product C ABI harnesses passed; locked native and managed whitespace checks passed | `raw/abi-signatures-final.log`, final format logs, six artifact hashes in the author receipt |
| Integrated native transaction lifecycle | 13 retained families; 120 checks | `raw/pg-integrated-transactions.log` |
| Integrated actual PostgreSQL protocol | 432 checks; final source/session/operation/cursor/buffer owners zero | `raw/pg-integrated-protocol.log` and its three server/consumer logs |

Empty successful format logs are preserved as raw bytes, while successful tool
exit observations are stated in the author receipt. The C ABI harnesses produced
no stdout log; their successful compile/run exit observations and executable
hashes are recorded, not inferred from an empty file.

Find assertions cover exact mapper identity across sessions and eviction, key
snapshots, configured money/binary composite schema, private/public registry
isolation through repeated evictions, count eviction, actual byte eviction,
execution through held leases, source close during mapper failure, cancellation,
no rows, schema changes and exact synchronous quota/error priority. Native
checks additionally cover Source mismatch, private import rejection, statement
shape and argument parity, and the Find-only general-cache bypass.

Run-05 remains historical: SQLite Find 192, PostgreSQL Find 194, complete suite
1,154 assertions / 119 retirements. The final run-06 is 192 / 192 and 1,152 / 118.
The suite adds two checks and one retirement per actual retirement callback;
these totals are observations rather than a fixed count of logical cases.
The original immutable receipt incorrectly summarized run-05 as 194 for each
provider. Its bytes remain unchanged, and
[find-validation-erratum.json](find-validation-erratum.json) corrects that one
sentence against the unchanged raw logs.

## Failed attempts retained

| Evidence | Observed failure and correction |
|---|---|
| `build-01.log` | Source owner was accessed as an unsupported variant type; corrected to `source_owner`. |
| `query-tests-01.log` | The native parity helper omitted actual Fluent projection field 5; corrected the oracle encoding. |
| `restore-01.log`, `restore-02.log` | Canceled exit 130 after stalling at project determination. No unverified network/audit cause is assigned. Locked restore from the existing local cache succeeded in `restore-03-offline.log`. |
| `orm-run-01.log` | SQL counter baseline included second-Session setup; moved the baseline after setup. |
| `orm-run-02.log` | Initial logical-quota expectation was wrong. Exact old Find proved `InvalidState` and synchronous failure; actual fixed logical fee was exported and used by managed admission. |
| `orm-run-03.log` | Model registration `ResourceLimit` preceded key admission in old Find; restored that cold-path order. |
| `orm-run-04.log` | The expectation of asynchronous compiled-argument rejection was wrong; old and new both reject synchronously. Corrected the assertion without introducing deferred-error state. |
| `format-managed.log` | `--folder` rejects the `--no-restore` option; valid folder whitespace command passed. |
| `build-07.log`, `query-tests-05.log` | New cache-bypass fixture omitted its ABI constructor argument and then used an invalid zero ABI hash; corrected to the existing nonzero fixture convention. |

The archive-only preflight failure is retained as `raw/archive-attempt-01.json`: comparing `git show` output to the saved parent-to-commit patch failed before compression; the exact fixed `git diff --binary` command independently used by the reviewer matches the saved bytes. No product source or raw log changed.

All intermediate success logs are retained too. There is a complete stage-04
working-tree patch and a complete final patch. Earlier failed iterations were
not each source-snapshotted: their raw diagnostics are preserved, but this record
does not invent exact complete source identities for those attempts. They are
development evidence, not final source-bound acceptance or timing samples.

## Archive and integrity

[manifest.json](manifest.json) lists every member, byte length, SHA-256 and
origin. [raw-evidence.tar.gz](raw-evidence.tar.gz) contains:

- `raw/`: every available file under the author's evidence directory, including
  the unchanged receipts, all failures, all final logs, final patch and stage-04
  patch;
- `source/find-final/`: the exact 25 changed source blobs from `dc23555`;
- `source/postgresql-integration.patch`: the exact patch from `dc23555` to the
  integrated `583ef70` tree;
- `review/`: the independent review at fixed Plan `1496005` and the reviewer's
  original receipt.

Tar entries are sorted regular files with mode `0644`, uid/gid/mtime zero and
empty owner names. Gzip has an empty filename and mtime zero. Readback verifies
the full member set, each length/hash and metadata, both unchanged receipts and
their source/log bindings, and identical deterministic archive reconstruction.
[readback.json](readback.json) records the result. No build or database load was
executed during archival.

The author receipt, erratum, integration receipt and reviewer receipt are also
copied unchanged alongside the archive for direct reading. The original author
receipt has SHA-256
`7440ad341d66c9d9c0e61adeaa32c3626ca79dc2a31abcbef1480cf8ed5a46a2`;
its erratum is
`3fbf173549b655e18407c97319c436bd43de966cad9aaa698b947acabdfe0dc9`.
The reviewer rehash independently matched 25 committed source blobs, 58 evidence
files and six local artifacts before the native integration rebuild. This
archive extends that inventory with the later integration logs and receipts.

Binaries are omitted from Git to keep this evidence archive small. Their
original exact sizes/hashes are retained in the two author receipts. The final
AOT ELF and its copied Find-only provider assets remain separate from the
later integrated native build. Source snapshots, patches, pinned baseline and
commands below permit reconstruction; reproducibility does not mean an
unexecuted reconstruction has passed.

## Reproduction commands

Use the repository's locked Linux toolchain/dependencies. This run used the
already provisioned task environment, .NET SDK 11.0.100 / Native AOT 11.0.0,
LLVM 23.1.5 and PostgreSQL 18. Commands below are the local finite gates, not
instructions to add a CI job. Run from the Korda source worktree. Recreate the
Find-only source from baseline plus `raw/find-final.patch`, then apply
`source/postgresql-integration.patch` for the separate integration gate.

```bash
source /workspace/scratch/4a65d70f0fe1/tools/task-env.sh
cmake --preset linux-x64-release -B /tmp/DB-Exec-10-find/native \
  -DFETCHCONTENT_SOURCE_DIR_NW_JSON=/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-07-pack-sqlite/artifacts/dependencies/nlohmann-json/json \
  -DFETCHCONTENT_SOURCE_DIR_NW_SQLITE=/workspace/scratch/4a65d70f0fe1/worktrees/DB-Exec-07-pack-sqlite/artifacts/dependencies/sqlite/sqlite-amalgamation-3510300 \
  -DPostgreSQL_ROOT=/workspace/scratch/4a65d70f0fe1/tools/postgres/install
cmake --build /tmp/DB-Exec-10-find/native \
  --target nw_database_sqlite nw_database_postgresql nw_query_tests -j 3
/tmp/DB-Exec-10-find/native/tests/nw_query_tests

dotnet restore tests/Orm.Relations/Korda.Orm.Relations.Tests.csproj \
  -r linux-x64 -p:PublishAot=true --locked-mode \
  --source /workspace/scratch/4a65d70f0fe1/tools/nuget-packages -p:NuGetAudit=false \
  -p:UseArtifactsOutput=true -p:ArtifactsPath=/tmp/DB-Exec-10-find/managed -nr:false -m:1
dotnet publish tests/Orm.Relations/Korda.Orm.Relations.Tests.csproj \
  -c Release -r linux-x64 -p:PublishAot=true --no-restore \
  -p:IlcTreatWarningsAsErrors=true -p:UseSharedCompilation=false -nr:false -m:1 \
  -p:UseArtifactsOutput=true -p:ArtifactsPath=/tmp/DB-Exec-10-find/managed \
  -p:KordaSqliteAssetPath=/tmp/DB-Exec-10-find/native/libnw_database_sqlite.so \
  -p:KordaPostgresAssetPath=/tmp/DB-Exec-10-find/native/libnw_database_postgresql.so \
  -o /tmp/DB-Exec-10-find/orm-aot
python3 tests/Data.NativeHost/run.py \
  --postgres-bin /workspace/scratch/4a65d70f0fe1/tools/postgres/install/bin \
  --output /tmp/DB-Exec-10-find/evidence/orm-run-06 \
  -- /tmp/DB-Exec-10-find/orm-aot/Korda.Orm.Relations.Tests --require-aot
```

The local cached restore did not change repository restore/CI policy. Compile
and run `native/cpp/tests/database_abi.c` separately against each product `.so`
with `clang -std=c17 -Wall -Wextra -Werror -UNDEBUG`, linking that exact asset and
setting its directory as rpath. Check `python3 tests/Query.Binding/generate.py
--check`, locked `clang-format --dry-run --Werror` on the changed C/C++ files,
`dotnet format whitespace --folder --include <changed C# files>
--verify-no-changes --verbosity minimal`, and `git diff --check`.

After applying the three PostgreSQL changes, the separate committed-source gate
was:

```bash
cmake --build /tmp/DB-Exec-10-find/native \
  --target nw_database_sqlite nw_database_postgresql nw_postgres_sync_tests nw_transaction_tests -j 3
/tmp/DB-Exec-10-find/native/tests/nw_transaction_tests
python3 tests/Data.NativeHost/run.py \
  --postgres-bin /workspace/scratch/4a65d70f0fe1/tools/postgres/install/bin \
  --output /tmp/DB-Exec-10-find/evidence/pg-integrated-protocol \
  -- python3 -c 'import os,sys; os.execv(sys.argv[1], [sys.argv[1], os.environ["NW_TEST_POSTGRES"]])' \
  /tmp/DB-Exec-10-find/native/tests/nw_postgres_sync_tests
```

This author stops here. Whole-query latency, CPU, allocation, RSS and throughput
benefits require the root's same-condition local measurements; zero additional
managed allocation is not claimed. Final package closure, public consumption,+ordinary diff-selected CI and publication remain independently evidenced.
