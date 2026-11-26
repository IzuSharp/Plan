# Command completion selected after accepted cancellation and row-path measurements

This continuation follows the blocked public `bc6ba1a` observations in
[continuation 4](../continuation-4/README.md). The original CI failure is
retained there. Final four-cell 1800-second credit is still **0/4**; the
correctness and development evidence below is not performance acceptance.

## Exact public candidates and current status

- [8058128](https://github.com/IzuSharp/Korda/commit/805812872d9d8860bb3bf9e55db18772f3579d85), tree `9866611a2abbe104cf0790b4a04b229183384633`: accepted cancellation correction, narrow ready scheduling and removal of the unused RetiredValueTask bridge. [Existing CI 45748812544](https://github.com/IzuSharp/Korda/actions/runs/45748812544) succeeded. Both independently produced packages pass public validation; four ordinary external-package Native AOT consumers build successfully.
- [31693e3](https://github.com/IzuSharp/Korda/commit/31693e3883f1192a34fcb9e9c49acdcca4ad321c), tree `21625a56598f3811008b8e5fcb71cb5758917056`: adds one-scope buffered row admission/materialization, its original-suite regressions and local workload ABI counting. [Existing CI 45749741438](https://github.com/IzuSharp/Korda/actions/runs/45749741438) succeeded. The exact ordinary packages/consumers completed the local short observations below. The buffered change is not a consistent performance winner across routes and sizes.
- [933d16b](https://github.com/IzuSharp/Korda/commit/933d16bf673dff5310db37cc444ba5019842d81d), tree `cdf18c758acc507d1ea84cbd20e1db1813cc5710`: current published source, tree-identical to local `12ac0e6ebd7503fa106106c26278ec98f4e115d9`. It adds the primary command-error correction and the local buffered-terminal measurement tool. [Existing CI 45752759759](https://github.com/IzuSharp/Korda/actions/runs/45752759759) has now succeeded. The short-run consumer packages remain pinned to 805/316; no timing is reassigned to 933 or the prospective one-shot implementation.

All three retained PR CI receipts report ten successful jobs, including the
existing Linux/interop and independent PostgreSQL/SQLite scopes, and the expected
modules/publication skips. They establish their own correctness/package checks,
not a new release or performance acceptance. The later 933 terminal receipt is
retained separately from the earlier short-run archive.

The phase consumer uses `AsAsyncEnumerable` / `StreamAsync`; it does not execute
buffered terminals. A separate ordinary consumer now invokes the actual public
buffered terminal with the same SQL and complete DTO result. Its results are
kept separate from both streaming phases and independent ABI diagnostics.

## Completed local short observations

The actual [outer run record](ready-row-short-01.manifest.json) binds ten serial
groups and **76 commands including ten separate fixtures**, all exit 0: 36
streaming phase commands, 12 public buffered commands, 12 ordinary single-case
commands and six independent ABI diagnostics. Phase and buffered groups use
256 iterations × three windows per route, rows 1/100/1000 and batch 32. Single
cases use C1, persistent sessions, requested prepared mode, 15 seconds, numeric /
transaction rollback / transaction commit. Fixture initialization uses ordinary
Korda and is excluded from timing. No database consumer, benchmark or profiler
ran in CI.

Clients use CPUs 0–3, owned PostgreSQL uses 4–7 and the observer uses 8. The
original host observation and process/PG resource ledgers are retained. No
cgroup or final host-admission credit is inferred. The PostgreSQL process-tree
observations remain their recorded non-atomic accounting scope; they are not
relabeled as complete cumulative server CPU.

- [Ready-scheduling streaming phases](analysis-phase-ready-01.md): all 18
  before/candidate/Dapper row observations are retained. Omitting an unnecessary
  pre-ready scheduling offer preserves the asynchronous callback/publication
  path; individual observed timings do not prove one queue item was saved on
  every batch.
- [Row-candidate streaming phases](analysis-phase-row-01.md): all 18 observations
  are retained, but this route cannot measure the buffered scope change.
- [Actual buffered A/B](analysis-buffered-row-01.md): all 12 commands pass strict
  source/package/generated-code/SQL/result/owner checks. On the prepared
  1,000-row route PostgreSQL CPU changes from 4,493.008 to 4,219.307 µs/op and p99
  from 6,130.919 to 4,195.328 µs; SQLite CPU changes from 3,783.089 to 3,718.742
  µs/op. However SQLite prepared 100-row p99 changes from 632.477 to 1,013.469 µs,
  and PostgreSQL prepared 100-row CPU rises from 644.155 to 695.659 µs/op.
  These are mixed observations, with no universal gain or framework 0 B claim.
- [Single-case ordinary/FFI analysis 02](analysis-single-row-02.md): four completed
  directories, twelve ordinary observations, six diagnostics and six paired
  business checks pass. Ordinary CPU, allocation and GC remain whole-process
  totals. Dapper numeric placeholders are explicitly matched to its actual
  generated SQL; transaction receipts contain lifecycle descriptions, not each
  executed statement. Same business results do not establish identical
  transaction SQL text.

The [failed analysis 01](analysis-single-row-01.md) is preserved. Its ordinary
metrics already validated; its structural expectation incorrectly assigned the
three `FindAsync` calls to mutation pull. Actual `Orm.Relations/Crud.cs` builds
ordinary query pulls. Analysis 02 changes only those two expected counts and
rereads the same measurements; no workload retry replaces the first result.
The archive preserves the failed analyzer bytes by a documented reconstruction
matching the exact original input SHA, plus the corrected source and both
reports. All ordinary/diagnostic input hashes remain unchanged.

## Why the next target is one-shot command completion

Both numeric diagnostics have zero generic starts/retirements. The transaction
cases still use three mandatory generic operations for rollback and four for
commit, plus zero or one conditional transaction close per business operation:

| Provider/case | Successful business operations | Generic starts / OK retirements | Conditional transaction close | Pending / all retire attempts |
| --- | ---: | ---: | ---: | ---: |
| SQLite rollback | 2,065 | 6,483 | 288 | 1,438 / 7,921 |
| SQLite commit | 1,820 | 7,331 | 51 | 1,416 / 8,747 |
| PostgreSQL rollback | 2,681 | 8,935 | 892 | 1,197 / 10,132 |
| PostgreSQL commit | 2,214 | 9,362 | 506 | 1,142 / 10,504 |

The corresponding **ordinary** rollback p99 is 24,510.464 / 26,607.616 µs on
SQLite/PostgreSQL, CPU 2,364.371 / 2,397.881 µs per business operation, and total
managed allocation about 63 KB/op. Commit p99 is 31,064.064 / 28,311.552 µs with
about 67 KB/op. These latency values never come from the instrumented process.
Pending counts attempts, not unique operations or 10 ms expirations. Source
inspection separately shows generic terminal notification precedes callback/work
lease retirement and no later native notification replaces the retry tick.
The evidence supports replacing that completion structure; it does not prove
all latency or CPU is attributable to it.

The [agreed target and contract matrix](command-completion-proposal.md) uses an
independent ReadyState/Worker, 48-byte typed request, 32-byte typed result and
four private exports; release and cold close/snapshot proof reuse the frozen
ABI. Capture and provider/business functions remain shared. Every temporary
input accessor and Source reservation leaves before ready; independent request
and Source fences protect notification tails and unknown acceptance. Count/Any
use a direct scalar conversion path, and transaction Unknown results retain
their existing early decision boundary. Local ABI checkpoint `d497dd2` has no
implementation, AOT, correctness or timing credit by itself.

Next: validate the complete new native/managed path and actual public-package
entry points, repeat these same ordinary/independent-count observations, then
calibrate the 35-case load and run the four serial final 1,800-second cells.
Current final credit is still **0/4**. No merge/release acceptance, framework
zero allocation, unexplained timer attribution or historical long-run credit is
inferred from this checkpoint.

## Primary errors through parent cleanup

The five original-code negative controls in
`primary-error-development-01.tar.gz` reproduce cleanup-launch errors replacing
a provider/capacity error. The unchanged tests pass after the two
`Session::execute` catches retain the original exception, attach secondary
cleanup evidence without overwriting existing provider/correlation/bulk fields,
and retain poison/discard plus retryable cleanup. Existing Host review,
transaction (120) and streaming (369) checks pass with their original logs.
This correction is published in 933 and covered by its successful existing CI;
it is separate from unimplemented one-shot completion and does not retag the
316 measurements.

## Cancellation failure, narrowed correction and original-suite recovery

The deterministic native fixture was first committed as local
`6c09ecd253c70a93e670bddb59b24652c7f3cd77`, with the exact bc6 product bytes.
Holding an accepted worker until Stop returned reproduced status 4/code 8,
`database admission is closed`. Rich error take returned that same error;
the reproduction did not establish a missing buffer or double take.

Local correction `7960d381f5c8c0c62c2fb12394e494d73df37c62` atomically marks
the active cancellation before publishing channel closure under the same
channel mutex. The provider wake remains outside that mutex. Both admission
checks retain Source, Session, cancellation and channel-close precedence.
Only an already admitted CursorPull requests cancellation precedence in the
final Cursor::fetch window. The frozen standalone fetch entry keeps its
default Closed precedence. Already frozen provider errors, SQLSTATE,
correlation and cleanup diagnostics are not rewritten.

The native development receipt records **369 streaming checks, 120 transaction
checks and 183 real-provider checks in 11 groups**, all passing. The provider
verifier includes real PostgreSQL TLS, cancellation/drain/reuse, transaction
and connection replacement behavior. The explicit frozen-error identity
assertion is separately identified as injected, not a real PostgreSQL event.
An untested intermediate draft build and the original failing fixture remain
recorded; the overwritten original reproduction executable has no invented
binary hash.

The managed recovery preserves three attempts:

| Attempt | Actual result |
| --- | --- |
| Original bc6 source, original packaged assets | AOT publish succeeds; unchanged Orm.Relations suite fails in CallbackCancellation, exit 250. |
| Original retained ELF, corrected native bytes substituted | Exit 250 before SQLite admission: the embedded provider asset SHA check rejects the new bytes. No hash check was disabled. |
| Same bc6 managed/test source, newly generated matching provider profile | AOT publish and the unchanged two-provider suite exit 0: 1,417 assertions, 382 managed retirements and final original owner counters zero. |

The last attempt verifies all **605 tracked src/tests files byte-for-byte**
against public bc6. The generated provider source and assets JSON change only
the native SHA values. Its ELF is
`be94f8b039f57fb60b0a834e56724499a01f00121aaa059a24d6f237e6da3932`.
This establishes a native-only correctness correction through the original
managed suite, with the normal asset integrity policy intact. It does not
substitute for the final integrated source's CI or package consumption.

## Unselected inline-completion experiment

The local `bf974378932ec3d42f31eb791e8bede6a69b41ea`
[experiment patch](ready-inline-unselected.patch.gz) and unexecuted `535fb00`
[test patch](ready-inline-unexecuted-tests.patch.gz) are preserved as
deterministic gzip files. The [patch manifest](inline-experiment-patches.json)
records their original SHA-256 values and exact restoration commands;
decompression restores every original byte, including unified-diff context
spaces. Existing evidence archives retain their original bytes. These are not selected product changes
and have no AOT execution or performance credit. A managed Release compile
had succeeded; review then found an additional exception boundary before AOT.

The actual ILCompiler 11.0.0 package pins
[dotnet/dotnet@297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f](https://github.com/dotnet/dotnet/commit/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f).
Its [ManualResetValueTaskSourceCore](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/Sources/ManualResetValueTaskSourceCore.cs)
publishes its completion sentinel before dispatching the continuation. Its
[ThreadPool dispatch](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/ThreadPoolWorkQueue.cs)
is not a no-throw primitive. Moving the setter into the unmanaged ready
callback therefore requires a separate post-publication failure policy.
Rewriting a reusable generation, calling SetException again, or disposing an
already delivered batch is not a valid recovery. General FailFast or silently
declaring dispatch success would not preserve the existing contract.

The selected implementation in public 8058128 is narrower: keep ready
callbacks, coordinator processing and asynchronous completion unchanged;
omit only Request's initial scheduling signal when an accepted request is
healthy and not yet ready. The decision and readiness share a mutex. Early
readiness still triggers setup's Resume; later readiness independently
signals work. Fault, stop, uncertain acceptance, unreserved setup failure,
registration and close paths retain their own progress notifications.
This can avoid an empty pre-ready work-item execution. It does not establish
that every batch saves one queue operation; actual A/B observations are needed.

## Correctness and deletion evidence

The ready scheduling fixture preserves the coordinator, callback and asynchronous setter. Four scenarios per provider verify early readiness, exactly three accepted late generations, rejected admission with a cancellation registration followed by retry, and a real delayed synchronization-context completion tail. Both original NativeHost provider suites pass, including 71 new assertions per provider, 246 held-mapper assertions, 276 close assertions and all final native owner counts zero. Two fixture compile failures are retained with their subsequent fixes. The rejected inline experiment is not silently substituted for this implementation.

The unused `RetiredValueTask<TResult>` bridge, its SafeHandle-only constructor/owner discriminator, retired-publication virtual hook and AsyncNativeCalls observation hook were deleted. Real `AsyncOperation<T>`, its early Task terminal and separate retirement, NativeResourceOwner and DataSource retirement observation remain because they still have callers. Six ownership cases moved to the live operation entry. The original A07 suite passes 451 assertions, including 90 ownership assertions, 73 matched creations/releases and zero live result/input buffers. Two initial fixture failures are retained. API metadata/XML and Release AOT sample checks pass. This is removal of a dead path, not a claim that all generic database operations are gone.

The buffered candidate removes the standalone row-byte entry and performs byte charging, row/byte budget checks, counter advancement and projection materialization within one read lease. Two original Release AOT suites pass: B06 615 assertions / 60 cases; 364 row-lease assertions; 12 new public buffered held-mapper scenarios / 170 assertions per provider. Original pre-mapper limits remain exactly 5, 1 and 0 mapper invocations for the row cap, byte cap and oversized row controls. API metadata reports zero public symbols changed. No performance credit is inferred from fewer scopes.

The published mixed workload still uses generic completion for transaction
begin/finish, nonreturning mutation and conditional transaction close. The
35-case manifest does not contain `CountAsync` or `AnyAsync` terminals. Current
diagnostic consumers now bind the actual 316 ordinary consumers; the historical
bc6 diagnostic builds remain separately preserved. The new one-shot target
therefore also needs explicit public Count/Any correctness coverage beyond this
35-case workload. Instrumented receipts continue to forbid timing/allocation
credit.

## Retained evidence

| Archive | SHA-256 | Read-back verification |
| --- | --- | --- |
| `cancel-native-regression-01.tar.gz` | `03b8eec7bb3fd83617a7336cb6a2cb2f22bfd16e6b6e7f733f182c8fc7de91fb` | 31 members; deterministic encoding and every extracted byte checked |
| `cancel-managed-regression-01.tar.gz` | `6ab5da5e9d45384b49b7522c14d6102e1a38ddf3740339e38ebcf6cf6f7fb6a6` | 46 members; original failure, integrity rejection and successful paired rebuild retained |
| `ready-defer-development-01.tar.gz` | `d95894a18e7293f93a51cfd01f8a0bc97b4a44d49377315bb9d6e29671a420cb` | 39 members; original compile failures, actual AOT pass and scheduling proofs |
| `retired-cleanup-development-01.tar.gz` | `a20e3a6f6d55170bc5476f05f9cc1fa655a550b4ea882858c45727a4254a97ad` | 121 members; original two fixture failures, successful original gate and ownership migration |
| `row-scope-development-01.tar.gz` | `8f07e76b20ee1f007b2683e071f593f03cabc2f832f54fdc81054a847c6fb454` | 35 members; two original AOT suites, limits and held-mapper evidence |
| `primary-error-development-01.tar.gz` | `49a706634c082be4baef4516c0017cdbf1315aaed60fd1f274529ca8e8341917` | Original five failures, same corrected tests and existing native gates; every original/extracted byte checked |
| `ready-row-short-01.tar.gz` | `8e6920fdbad4fccbf51f98dd367a7ba7900db3b7e897189b3999868d32f931c0` | 507 members, 2,424,887 bytes; ten groups/76 commands, actual raw results/logs/resources, build/source inputs, failed analysis 01 and corrected 02; deterministic encoding and read-back verified |

External manifests list individual original bytes and their hashes. Binary
outputs and reproducible database data are excluded from these archives;
their recorded hashes and exact source/build identities remain. The helper
`prepare_load_index.py` only binds existing local plans to the retained strict
analyzer. It starts no process and grants no timing or final-run credit.

The [documentation gate receipt](documentation-gates-01/receipt.json) retains
the two passing Design gates and the original Plan gate at the workflow's
frozen `38f8ce8` snapshot, including its earlier frozen-history checks. A direct
attempt to run that historical Plan verifier on the current tree is also
preserved: it rejects eight already committed repository-rename paths before
examining this continuation. The verifier and historical acceptance inputs
remain unchanged. These results validate their recorded documentation/history
scope and grant no new product or performance acceptance.
