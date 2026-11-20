# Recovery epoch 001: fresh producers and actual identities

Status: **source preparation; product producers unrun**. This scope reconstructs the small build
orchestration that was private and lost. It does not claim to recover the old
owner/guard, output bytes, 963 weak-OFF source, source review, noise or execution
credit. Root owns actual launch after independent source review and the bounded
ownership checks. The original public producer implementations are unchanged.

The prospective recovery freeze is `eda07013…`; actual toolchain receipt
`663c591a…` records the new compiler/SDK/PostgreSQL identities. Every producer
uses the same frozen public driver commit `2e3995df…`. Product roles are clean
EA5 main and clean retained-ON 2e checkouts. The latter is a candidate, not a
conclusion that optional weak reuse deserves retention.

## Fixed build sequence

Each product role has eight serial producers:

| Producer | Original entry point | Result boundary |
| --- | --- | --- |
| Native SQLite/PostgreSQL/Server | `eng/task07_native.py` in actual product | Three actual Release native assets and tools/source hashes |
| Complete B24 | `src/Packaging.Domain/prepare.py` in actual product | All 14 managed projects plus three native leaves; fresh selected previous feed and unused mixed upgrade feed |
| Reference | Frozen `tests/Reference.TaskService/package_probe.py` | Actual JIT/AOT builds; build-only `partial` is not a service/long pass |
| Observer | Frozen `tests/Perf01.Database/prepare_observer.py` | Same catch/log/rethrow observer on both roles; actual package resolution additionally bound |
| Protocols | Frozen `tests/Perf01.Protocols/build.py` | Native AOT server/client; original six producer commands |
| Codec | Frozen `tests/Perf01.Codec/driver.py prepare` | Original A17 JIT/AOT/negative/ordinary-edit checks and separate two-package consumer/direct build |
| Retirement probe | Frozen `tests/Perf01.Shared/prepare.py` | Profiling consumer built, not executed |
| Page probe | Same entry point, `--probe page` | Profiling consumer built, not executed |

`common` then runs the existing direct-protocol builder against the new before
common client, the existing database direct/managed comparator producer with
its golden-vector checks, and the existing deterministic codec corpus command
against the new before direct executable. These are three original commands,
not a new harness. Common controls are reused by both product roles. The after
codec producer still makes its own direct artifact as the original producer
requires; measurement must select the bound common before direct comparator.

`bind-pair` has zero producers. It rechecks both actual role bindings and common
inputs and requires the same external archive/content population per consumer.
No threshold, scheduler, reader, percentile or workload is added here.

## Source, freshness and NuGet semantics

The native/B24/A17 packaging producer/helper bytes checked are equal at EA5 and
2e and are pinned individually. Full role commits/trees and actual producer
inventories are retained. Every tracked managed project's `bin` and `obj` must
be absent initially and immediately before the B24 managed producer. A fresh
product `target` is also required. Checkouts/output/cache roots are independent;
there is no automatic resume, cleanup or stale COMMON assembly import.

The observer's original implementation does not choose `NUGET_PACKAGES`.
The outer build explicitly supplies its role's **same fresh reference cache**.
The post-build binding accepts exactly that canonical `packageFolders` path,
with zero or one trailing slash, and compares the observer to the complete
saved reference AOT resolution. It retains both package feeds and verifies all
17 selected archives and the actual consumer/native/executable bytes.

NuGet has two distinct hash populations. Each bound resolved archive records
raw ZIP SHA-256 and raw ZIP SHA-512, plus the separate NuGet assets/extraction
`contentHash`. The archive sidecar must agree with raw SHA-512; assets and
extraction content hashes must agree. Local NativeWeave packages must exactly
match the selected feed and their raw/content hashes must coincide. Signed
external packages may have different raw and content hashes; the original
successful restore and metadata are retained, signature-entry presence is
recorded, and both actual identities must match across the paired consumers.
This does not implement a new package-signature verification policy or treat
an unverified sidecar as proof of the measured executable. Unknown/malformed
resolution, aliases, changed feeds and mismatched paired archives fail.

The A17 Core envelope remains at the producer's fixed experimental
`0.1.0-proof.1` in separate role caches. It is not merged with B24 Core. Its
identity is actual source/archive/executable bytes, not the shared version text.

## Finite ownership and operational space guards

The new build-only owner reuses public B23 `OwnedTree` PID/start-time checks and
pidfd signals. It adds Linux subreaper adoption to observe escaped-session
compiler descendants. Normal leader exit is insufficient: all owned/adopted
children must retire, including zombies being reaped. A remaining child makes
the command fail even if the leader returned zero. Timeout/cancellation uses
the same identity-bound termination and records forced cleanup separately;
it never proves native application retirement. The entire stage holds the
single new epoch timing lock. Neither the owner nor its callers silently retry.
The three synthetic fixture assertions distinguish normal zero exit without
signals, actual timeout with termination, and a zero-exit leader rejected for
its live detached descendant; unrelated failures cannot satisfy a negative case.

The actual first fixture invocation stopped before spawning a test child:
subreaper admission succeeded, but this executor does not expose
`/proc/PID/task/PID/children`. Its failed receipt
`d440b032368f2bbbe249c3b51f5cd79aab8dde80a7775568cfd0c626ec507d67`
remains unchanged. The narrow recovery adaptation enumerates numeric procfs
entries with the existing strict stat parser and selects actual PPid equal to
the owner. It is used for initial admission, adoption, protected normal exit
and final retirement. Only disappeared-process races are skipped; permission
or malformed-record failures refuse the gate. The same three fixtures must run
at fresh `owner-fixtures-002`; this source change has not passed them yet.

Root selected **16 GiB free at stage entry** and **8 GiB before each producer**.
These are operational headroom guards, not peak-space guarantees or changes to
the formal 256 MiB application resource limit. A failed floor preserves the
partial stage and stops. Compiler intermediates and the A17 temporary package
consumer remain under task-owned roots; this scope deletes nothing.

Only the reviewed build environment is forwarded. Workload-advertising download
notification is disabled for CLI producers on both roles; this build-only
override does not change any formal runtime environment. All original build
options/ISA differences remain (protocol/shared v2; B21/A17 compiler defaults).
The original direct protocol builder is offline and may require the locked
registry dependencies to have been provisioned first. This wrapper never
downloads, upgrades, rewrites locks or provisions tools on its own.

## Root invocation and finite validation

Set `ROOT` to this recovery workspace and `PREP` to this exact reviewed scope.
Use the actual SHA-256 of `inputs.json` and `sources.json`; do not paste hashes
from an earlier source revision. The retained-ON product worktree must first be
created at exact 2e, separate from the frozen driver checkout.

```sh
taskset -c 8 "$PYTHON" "$PREP/check_owner.py" --driver "$ROOT/.worktree/Perf-01-linux/NativeWeave" \
  --output "$ROOT/perf01-recovery/epoch-001/control/owner-fixtures-002"
taskset -c 8 "$PYTHON" "$PREP/build.py" --root "$ROOT" --inputs "$PREP/inputs.json" \
  --inputs-sha256 "$INPUT_SHA" --source-index-sha256 "$SOURCE_SHA" --stage before
```

The bounded synthetic checks cover a normal exit, timeout and a detached child
whose leader exits normally. They create no product build or measurement.
The required fresh output keeps every case receipt/log even if an assertion
fails; nothing is deleted. Successful stdout includes each exact receipt hash.
Run them only after source review, retain stdout/stderr/exit and exact source
identity in a separate actual receipt, and preserve a failure rather than
editing its result. They have not run as part of preparation.

For `common` and `after`, supply `--before-receipt-sha256` with the actual
completed before execution hash. For `bind-pair`, also supply
`--after-receipt-sha256` and `--common-receipt-sha256`. Every stage creates a fresh
`control/build-STAGE/execution.json` and `binding.json`. All commands and their
actual stdout/stderr/exit/owned process observations have separate receipts.
Success means new producer artifacts are bound; functional smoke, repository
gates, qualification, noise, capacity and all ten long segments remain separate.

No current artifact hash or execution result is invented. The source index is
not a runtime receipt. Root must publish/retrieve curated actual results and
preserve the new raw/operational closure explicitly before claiming recovery.
