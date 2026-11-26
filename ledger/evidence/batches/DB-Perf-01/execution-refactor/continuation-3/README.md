# Cursor pull continuation and current-host recovery

## Current measured continuation

The public0f product below is the first measured intermediate candidate. Its
18 ordinary, 12 ABI and 18 allocation commands have now completed successfully.
The [measured checkpoint and next decision](measured-checkpoint-0f3816c.md) records
the actual gains, the remaining final-close retry tail and the new close-ready
implementation work. Final 1800-second credit remains **0/4**. Earlier build-only
statements below describe the archived pre-execution checkpoint.

The interrupted cursor-channel source was not committed or archived in the
previous workspace. That workspace is absent in this continuation. Work resumed
from public `ada28311a384ad149fdc3f9db3b14473aedf0061`, preserving its transaction
worker fences, deadline correction, command-arena changes and CI separation.
Only the missing channel implementation was reconstructed in task worktrees.

The frozen public product source is
[Korda 0f3816c4](https://github.com/IzuSharp/Korda/commit/0f3816c4006488821f40afde91bbbd717d57ccd6),
tree `9935773d28b3043618285cf0ecd5c476539b2f8c`. It is tree-identical to reviewed
local `6da0074513d9cb1ff9f13748b058211ec706f230`; the commit identities differ.
[source-parity-final.json](source-parity-final.json) records the checked Git
objects. Final native producers and ordinary candidate consumers use the
fetched public source. Final local long-test credit remains **0/4**.

The earlier integrated checkpoint
[e0b5bdfd](https://github.com/IzuSharp/Korda/commit/e0b5bdfd6520a74a430a94f4b0ca0b903b1af75e)
and its original [source-parity.json](source-parity.json) remain unchanged.
Its [CI 45733034030](https://github.com/IzuSharp/Korda/actions/runs/45733034030)
completed successfully. The final source has its own successful
[CI 45734731584](https://github.com/IzuSharp/Korda/actions/runs/45734731584):
10 jobs succeeded; `modules` and `publish` were skipped. Linux, interop,
independent PostgreSQL and SQLite checks, security and Verify all succeeded.
The separate [final CI observation](public-ci/0f3816c-ci-45734731584-final.json)
does not borrow success from e0 and does not establish publication, local
performance acceptance or a merge.

## Actual implementation

Ordinary SQL/Fluent, explicit relation loads and CRUD returning results now
capture a lazy cursor channel. The first accepted pull opens and validates the
cursor, performs the preserved second execution-admission check, then fetches.
Later generations reuse the channel, managed completion source and scoped batch
owner. A detached ready callback follows provider/read-guard release. Final
close joins independent native tails; the generic operation quiet contract is
unchanged. The obsolete unpublished result-batch extension, HostStreamBatch,
borrowed memory wrapper, per-batch generic operation entry and compatibility
bridges without production callers are removed. The original 42 declarations
and public C# APIs remain frozen.

Cross-review found and corrected pre-ready cleanup exceptions and destructor
queue-post failures. Unknown cleanup is poisoned and reported as unreleased;
its bounded native accessor remains quarantined. The accepted request's primary
error survives a later cleanup exception. Setup failures before coordinator-slot
reservation can finish after an overlapping stop even when every scheduler
offer is rejected. Final source includes those corrections and their explicit
failure-boundary tests.

## Development evidence and limits

[DB-Exec-02-correctness-receipt.json](DB-Exec-02-correctness-receipt.json) is the
original isolated development receipt. Its supplemented
[runner and command receipt](development/DB-Exec-02-correctness-receipt.json),
[scheduler receipt](development/pull-scheduler-races-02/receipt.json),
[primary-error record](development/native-primary-error/README.md), sources and
raw logs retain the exact stage boundaries. These staged checks are not a claim
that a single final package binary ran their combined suite locally.

| Executed check | Observation |
| --- | --- |
| Data.Abstractions actual Release Native AOT | 25 managed cases passed |
| Data.Streaming actual two providers | 60 provider cases, 615 assertions; scoped/borrowed/race/reuse checks also passed |
| Data.NativeHost actual two providers | 590 main assertions; 42 transfer-record checks; 32 held-mapper scenarios; generation reuse, setup/callback/take failures and pre-reservation stop covered |
| Public fetch matrix | 0/1/32/64/100/1000 rows: exact 1/1/2/3/4/32 accepted requests, takes and publications per provider; one business SQL each, no generic operation before any delivered row, 0 or 1 final close operation |
| Native sealed channel tests | streaming261, transactions120, relations ABI469 and C17 layout target all passed on isolated source22a856a |
| Native primary-error correction | Original mixed-tree repro failed; fixed a781e51 ctest run passed 4/4 targets. The raw ctest log reports target results, not a directly recoverable 265-assertion count |
| Refused scheduler and overlapping stop | Final test92d3b06, managed962071d, nativea781e51: actual Release Native AOT passed 8 cases / 72 assertions across both providers; original setup-error identity, separate stop-error identity, one publication, zero roots/slots/owners and normal-stop session reuse retained |
| Real PostgreSQL a781e51 development gates | Protocol325; B02 11 groups plus 11 isolated-HOME groups; provider183, zero failures and `postgres_verified`. Unknown commit remains durable1/Unknown with native retirement; see [native-pg-a781](native-pg-a781/summary.json) |
| CI planner/tooling | 45 tooling tests passed; ownership index and exact42+3+8 signature checks passed |

The original new test expecting exactly one generic close failed. Review proved
that an already-retired channel/cursor snapshot legally eliminates that close;
the corrected test retains exact pull counts, zero per-batch generic operations
and all ownership predicates. The first failure remains retained. NativeHost's
successful isolated run predates the later cancellation-registration guard,
scheduler correction and native cleanup sealing. The final source's existing
CI is recorded separately above; the development suite is not relabeled as a
final local package gate.

The first scheduler-specific run also failed: the test left its deliberate
failure hook installed during the later session-reuse probe. The second run
cleared that test instrumentation before probing reuse and passed; product
code did not change between those attempts. Both original logs are retained
under `development/pull-scheduler-races-{01,02}`. Native primary-error repro
used the 22a856a host with the then-uncommitted test additions later committed
in a781e51. It is not represented as a clean checkout of 22a856a.

The first workspace build lacked staged native provider assets and failed at
the existing asset guard. The before-package builder's first two attempts were
interrupted after unsupported shared compiler/parallel build IPC stalled. The
third used build-only `UseSharedCompilation=false DOTNET_PROCESSOR_COUNT=1` and
passed. These settings are not inherited by performance processes. The native
format gate passed after the committed ABI-probe formatting correction.

## Same-host inputs and remaining work

The locked .NET11.0.100, LLVM23.1.5, CMake4.3.3, Ninja1.13.2, PostgreSQL/libpq18.0
and SQLite3.51.3 inputs were restored and hash-verified. The immediate before
`f0078da720e07031bc56464995af6791c41aaae8` native profiles and two independent
packages were rebuilt here. External PackageReference Native AOT consumers for
both before providers and Dapper.AOT1.1.0 with Npgsql11.0.0 or
Microsoft.Data.Sqlite.Core11.0.0 were rebuilt. Generated sources and exact
binary/package hashes remain in their receipts. Both final 0f3816c native
producers completed configure/build/install with exit0; their distinct profiles
and exact images are bound in [producer-inputs](producer-inputs/README.md).
Both local provider packages and four ordinary candidate Native AOT consumers
were built successfully. Compilation is recorded as **built**, without a query
execution or timing claim.

[consumer-inputs.tar.gz](consumer-inputs.tar.gz) preserves all 12
ordinary external consumers: before/candidate/Dapper × PostgreSQL/SQLite ×
query-phases/mixed-workload. It includes original build receipts, actual C#
sources/projects, SDK/configuration files, available asset graphs and the actual
captured generated C# sources, including Dapper.AOT parameter factories and row
readers. Its [manifest](consumer-inputs.manifest.json) and
[recovery instructions](consumer-inputs.README.md) bind every archived file.
Source/project/asset/log hashes were checked against each build receipt.
Restored package caches, binary outputs, PostgreSQL data and private certificates
are excluded. Consumer binaries and packages retain their receipt hashes and
must be rebuilt from the recorded inputs if the scratch workspace is lost.

Same-SQL phase measurements, allocation/ABI observations, arrival-rate
calibration, matched before observations and the four serial uninterrupted
1800-second candidate/Dapper cells still need their own executed records.
Current final long credit is **0/4**. Historical f0078da7 results and previous
diagnostic numbers are not reassigned here.

## Recovered local diagnostics and retained tool failures

[allocation-recovery/README.md](allocation-recovery/README.md) binds the newly
recovered allocation overlay, its exact builder and observer sources, all ten
build attempts and generated mapper patches. The successful SQLite before and
Dapper attempts compiled Native AOT executables; that recovery receipt grants
no execution or timing credit. The adopted tool is commit54361c2, included in
public0f3816c. Later local provenance-only commits b82e4d1 and 660ddd8 were not
incorporated into the frozen product source.

The overlay observes actual generated mapper, List-constructor and List-Add
allocation scopes separately from whole-process allocation and GC windows.
Mapper scopes can include codec/driver scratch. `FrameworkOnlyBytes` remains
null, and all instrumented timing is explicitly ineligible for production
latency/throughput comparison.

The final candidate's 53-export FFI shim initially failed compilation because
the diagnostic generator reused `result` as a local status variable when the
ABI already had an output parameter of that name. Its original receipt, C
source and compiler errors are retained under
[diagnostic-failures/ffi-candidate-sqlite](diagnostic-failures/ffi-candidate-sqlite/README.md).
The separate local tool-only fix7d6d5f8 changes that generated name. This is a
diagnostic compilation failure; the public0f product/package identity is
unchanged. Rebuilt overlays and later executions require separate receipts.

[archive-index.json](archive-index.json) lists the copied original paths,
archive paths, sizes and SHA-256 hashes. Every copied byte was checked; the
existing initial index and original e0 parity remain intact. Derived explanatory
files and the final parity have a separate [documentation index](documentation-index.json).

All benchmark/profiling/calibration/load work remains local Linux x64. The
actual impact plan selects existing interop, shared database and independently
validated PostgreSQL/SQLite package scopes. It adds no performance workflow,
job, button, schedule or hidden test step. Review and ordinary eligible merges
follow complete correctness and measurement acceptance.
