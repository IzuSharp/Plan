# Perf-01: recovered binding diagnostics and published experimental source

**The binding retry experiment has now been checked at scalar, complete SQLite application and real TLS gRPC levels.** The latency observations are promising, with explicit CPU and tail costs. None of these diagnostics replaces the original failed comparison or qualifies a final product. The epoch-002 formal status remains **15/16 short comparison scenes, 0/15 capacity executions and 0/10 accepted 30-minute segments** for the currently selected `2f40348c` artifacts.

## Completed equivalent diagnostic work

| Diagnostic and actual cohorts | Successful measured work | Observed latency | Observed resource cost | Disposition |
| --- | ---: | --- | --- | --- |
| Real TLS gRPC, buffer-only `ea006711` → 1 ms `a5748ad4` | 12 processes, 3,876 calls; 37 finite commands retired | p99 lower in 13/15 paired case observations; server-stream p99 higher in two pairs | Active server CPU higher in all six profile pairs, by about 1.40–2.30 percentage points of one core | Continue evaluation; no formal mean/noise decision |
| Sequential SQLite scalar, current `2f40348c` → `a5748ad4` | Six processes, 6,000 scalar calls and 24,000 native-operation observations | All three corresponding mean/p99 observations lower; current-process means vary substantially | Fixed-work process CPU lower in all three pairs; allocation includes the observer; idle CPU/RSS unavailable | Useful layer diagnostic; no business throughput or formal noise inference |
| Complete SQLite application, current `2f40348c` → `a5748ad4` | Six processes, 18,006 successful operations; 1,501 measured durable commits per process | Mean of process p99 values: 172.307494 → 47.522623 ms; cycle 220.725469 → 52.231711 ms | Mean measurement CPU time: 20.936667 → 23.523333 s (+12.355%); short idle CPU: 3.355638% → 7.072850% of one core | All original per-cell validity/service/durability/drain checks pass; CPU cost remains |

These cohorts are different from one another and from the frozen EA5 baseline.
Do not chain their percentages into a manufactured final-before/final-after
improvement. Each detailed report preserves individual process rows, original
hashes, actual loaded libraries and the limits of its measurements:

- [TLS gRPC report](binding-retry-ablation-001/README.md), [numerical projection](binding-retry-ablation-001/projection.json), [independent review](binding-retry-ablation-review-001.md).
- [Scalar report](binding-retry-retirement-002/README.md), [numerical projection](binding-retry-retirement-002/projection.json), [independent result review](binding-retry-retirement-results-review-002.md), [root presentation review](scalar-presentation-review-016.json).
- [Complete application report](binding-retry-application-recovered-001.md), [numerical projection](binding-retry-application-recovered-001.json), [independent review](binding-retry-application-recovered-review-001.md).

The full application uses the original strong C# Fluent/DTO/transaction path,
Release Native AOT, SQLite WAL with `synchronous=FULL`, a frozen 50/s schedule,
concurrency 16 and equivalent fresh databases. All six processes completed
3,001/3,001 operations; independent queries verified 1,637 items, operations
and outbox rows per process. Surfaced BUSY/LOCKED and explicit business retries
were zero. Internal busy-handler retry counts remain unavailable. The original
formal C16 p99 failure of **567.131236 ms** remains unchanged and ineligible.

### Documentary limitations preserved

The original scalar001 package-source prerequisite failed before consumer
construction because its recipe incorrectly treated three native package rows
as managed rows. Both scalar002 executions used the correct consumer/result
paths, but retained stale001 output collection patterns; their original outer
output inventories remain empty. A separately identified 18-artifact
post-execution receipt adds traceability without rewriting those records. The
independent review acknowledges its earlier source-review miss.

The recovered ordinary-app outer recipe omitted seven preflight pins for the
HTTP Python libraries and `taskset`. All six actual frozen-input maps nevertheless
contain the same hashes as the original C16 configuration. The full report lists
this difference and the path/argument-order/metadata-timeout differences. It does
not claim that the stronger outer preflight was executed. The recovered runs
were reused only after exact-source, artifact, per-cell predicate and retirement
checks; no duplicate load was needed. The unavailable descriptor/memory
observation at current repetition 3 final shutdown is retained.

## Callback scan experiment and functional identity

The [functional evidence reconciliation](callback-scan-executed-evidence-review-001.md)
confirms actual A06 and B18 executions for `092e5e2c74d7419772f2455a2922ae4238f389de`.
A06 passed 6,343 JIT / 6,344 AOT assertions and five Rust tests, with the original
three expected negative fixtures preserved. B18 passed 1,036 JIT / 1,037 AOT
assertions, 18 assembled commands and 25 package commands. Both finite owners
retired with no remaining observed owned children.

The tested tree equals initial scan candidate `59eec092`. Current reviewed
`2c88e5db` has identical product bytes and only a callback-test correction.
The [source review](callback-scan-source-review-001.md) explains that correction;
the earlier test pass is not execution credit for the corrected test bytes.
The B18 component-native receipt is explicitly reused; its component library
is distinct from the actually supplied Server library `8b726c39…696f78c0`.

The existing controller subsequently completed the scan candidate's protocol
producer and 12-cell TLS diagnostic. Its final ablation execution is
`b66210f8c27ed70c44dad68d90d1bf58544713c0e5529d749adbb40e1ec7e08e`, with
37 commands exited and retired between **11:13:35.890088 and 11:20:53.711270 UTC
on 2026-11-21**. Independent numerical projection and the retention decision are
separate follow-up work. This checkpoint awards no performance acceptance to it.

## Experimental product sources are retrievable

The experimental source is now published in isolated NativeWeave branches,
without changing the selected product PR. Publication commits have exactly the
same Git trees as the actual local source identities below. All **11 versioned
changed-file entries** were fetched back and matched exactly.

| Recorded local source | Published source snapshot | Identical tree |
| --- | --- | --- |
| `a5748ad4e03825e3da7706d074887952da6c2d43` | [`543dbc4464c46de51200f96095b1d41c334554c2`](https://github.com/IzuSharp/NativeWeave/commit/543dbc4464c46de51200f96095b1d41c334554c2) | `f2816e3364b90512958ca51e5d2c4c3f02766bb9` |
| `092e5e2c74d7419772f2455a2922ae4238f389de` | [`091e2ed308c8d4b782c9fd65546ba052316fdb4b`](https://github.com/IzuSharp/NativeWeave/commit/091e2ed308c8d4b782c9fd65546ba052316fdb4b) | `cebf4fde46b529b1ec92fc6134e33ed09c36fc4f` |
| `2c88e5dbbc197079c48c3c41d51101b2d58bb3a5` | [`7b39ee141e20c35f8e4e551fad64003a72ae9be7`](https://github.com/IzuSharp/NativeWeave/commit/7b39ee141e20c35f8e4e551fad64003a72ae9be7) | `dc5c79861ca56dfe14fb43b379b6a8bea6e4aa94` |

Branches are `task/Perf-01-binding-retry-linux` and
`task/Perf-01-callback-scan-linux`. The [publication receipt](experimental-product-source-publication-001.json)
records exact file hashes. Source publication does not relabel an execution,
select an experiment for retention, satisfy CI or change formal acceptance.
The initial source-only experiment notes remain historical preparation records;
the later actual reports above supply execution status.

## Retention and remaining acceptance

The completed PostgreSQL C16 archive was saved, retrieved to a distinct path and
checked against all 25 member hashes as recorded in checkpoint015. Subsequently,
the 24 selected original observation/event files were rehashed and reversibly
staged out. The additive staging receipt is
`9abe6e79d17c7003da1ff2fa519e42a337782f91596ea5c36be4332264528250`.
The archive SHA-256 remains
`568d263ecdf6f500f509a252f8cbe3dcd995b8f04130ae1d533c207af8501092`.
Restore those exact members before a future raw reread. All other metadata,
resource samples, oracles, databases and actual measured binaries were outside
that selection. The earlier checkpoint's statement that originals were still
present describes its earlier observation, not the current storage state.

Public synthetic numerical/review/source records remain in Git while repository
history is retained. The archive retains the previously recorded owner/account
deletion policy; no fixed expiration is invented. Public resource-series export
still needs an actual completed helper execution.

Next: resolve the measured CPU/tail tradeoff; select and actually build matching
final artifacts; complete affected shared/data/server regressions; perform the
original equivalent formal comparisons and 15 capacity executions; then obtain
all ten uninterrupted effective 30-minute segments. Existing failures and invalid
attempts remain preserved. Both task PRs remain draft/unmerged. Normal post-merge
CI/preview and the separate domain-package release boundary are unchanged.
