# Perf-01: independent review of the empty-only retry guard

**Accepted for an isolated source experiment; no blocking source issue found.** The exact reviewed commit is `08d716ed2eab448a1a890cb579d086c131613291`, tree `c95491f4c7b86703d0d4f697eb185cd4f5fc1a47`, parent `a5748ad4e03825e3da7706d074887952da6c2d43`. No compilation, regression, workload or performance result is claimed.

## Exact change

The clean Git diff contains one file and two inserted lines: `if (Count == 0) return;` and a blank line at the beginning of `CallbackCoordinator.Retry`. Removing only these bytes recovers the parent file exactly. The candidate file SHA-256 is `4d2f79814b425b5ead5ea2918c021cd3f29910c396c026a801967eb5af968ada`.

The active full-capacity scan, Reserve, Release, Dispose and the entire CoordinatedCallback implementation remain unchanged. No occupied-prefix field, native/ABI/public API change or `2c88` test revision is included. The original A06 Program remains `aff1c550…`, not the corrected prefix-experiment Program `260f8bf9…`. Original A07 and B04 sources also match the parent.

## Concurrency and lifetime

`Count` observes `_count` under the same `_gate` as reservation and release. An observed zero means no occupied slot at that instant. A context reserved just afterward still uses the original immediate `Signal()` path. If that scheduling attempt is rejected, the original dirty/retry state remains set and the context stays registered, so a subsequent nonempty timer pass can retry it.

There is a timing caveat: a reservation just after the empty check can miss this timer pass, whereas the former full scan might have reached the new slot. Following rejected scheduling, that work may wait for a later tick. The configured timer period is not a strict wall-clock bound, and this review does not promise unchanged wake latency.

If the last slot is released after a positive Count observation, the unchanged scan may simply examine empty slots. Dispose still closes admission; it stops the timer only when closing and empty. No new lock nesting, callback under the reservation gate, release point, root lifetime or dirty/scheduled lost-wake protocol is introduced.

## Costs and applicability

Every nonempty tick acquires the reservation gate once more before the original scan. Active full scans are unchanged. `Server.Native/NativeHost.cs` reserves its persistent control slot at construction and releases it at retirement, so a live Server normally cannot use this empty fast path. It should not be presented as a solution to that Server's idle scan cost.

DataSource can have no operation slots between retirements, making its observed idle CPU a relevant target. The allocation, CPU and latency outcome still requires equivalent measurements. This smaller change is a separate experiment; evidence for the unselected occupied-prefix variant is not transferred.

## Existing B04 route, without a Rust engine rebuild

The existing `tests/Data.NativeHost/NativeWeave.Data.NativeHost.Tests.csproj` references the two provider projects. Both support `NativeWeaveSqliteAssetPath` and `NativeWeavePostgresAssetPath`; their build targets hash and copy those supplied assets and generate the normal engine metadata. The project has both ordinary and Linux x64 AOT lock files. The diagnostic native owner-count export used by the fixture is unconditional in `native/database/host/src/abi.rs`.

The supported sequence is a locked JIT restore/build, original two-provider consumer run, locked Linux x64 AOT restore/publish, then the same original consumer run as a Native AOT executable. Use the existing `--no-restore`, Release, `PublishAot=true`, `IlcTreatWarningsAsErrors=true`, no shared compilation, single MSBuild node and existing asset-path properties. Do not substitute a Rust build for the supplied precompiled assets.

The original runner is:

```text
python tests/Data.NativeHost/run.py --postgres-bin <locked PostgreSQL bin> --output <fresh JIT logs> -- dotnet <Release net11.0 test DLL>
python tests/Data.NativeHost/run.py --postgres-bin <locked PostgreSQL bin> --output <fresh AOT logs> -- <Native AOT test executable>
```

The fixture has no `--require-aot` mode; appending that string does not create an AOT runtime assertion. Preserve actual publish/executable identity in the resulting receipts. The runner retains its 180-second consumer limit and stops the isolated PostgreSQL cluster in `finally`. Its startup commands rely on the existing finite outer owner for the overall deadline and descendant retirement. Fresh log directories and the shared timing lock remain necessary for coordinated execution.

This existing fixture checks real per-operation retirement, pool-admission cancellation, failure cleanup, cursor/transaction semantics, source/session close and zero final native resource counters. Together with the original A06/A07 suites it is the concrete targeted regression scope identified by this review. No new fixture, execution plan or gate was introduced here.

[Exact hashes and source checklist](empty-retry-source-review-001.json).
