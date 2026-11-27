# Bounded relation capacity — measured integration decision

The [prior hypothesis](relation-capacity-hypothesis.md) has now passed its isolated resource and correctness gates. Select it for combined validation as a reduction in temporary managed allocation and copying. **CPU, latency, release RSS and framework-wide zero allocation are not established benefits.** This decision precedes adding the isolated source to the integrated product branch; final mixed acceptance remains pending.

Ordinary source is `6b872e31bb12d5529fdf472cb598a044922dd5c0`; diagnostic source is `0c9c5a647ab20e26a4ac9635d8940852a27fc758`. Product commits to integrate are `c0643e2`, `cd83697`, `6b872e3` only. The latter two correct new test expectations to original expression-budget and public error mapping behavior. They do not change product quotas or exception order. The diagnostic source is excluded.

## Causal result

Both real databases completed 128 checked related32 diagnostic businesses. Every request retained 53 rows, digest `2847736615530494015`, one SQL, PostgreSQL's existing four protocol submissions, and zero owners. All 511,392 records/provider completed with zero reported loss. New reserve allocations are counted explicitly, not hidden outside old growth scopes.

| Resource per business | Previous private-transfer candidate | Capacity candidate |
| --- | ---: | ---: |
| Growth allocations | 98 / 129,328 B | 5 / 15,992 B |
| New empty-reserve allocations | 0 | 31 / 64,232 B |
| Combined array allocations | 98 / 129,328 B | 36 / 80,224 B |
| Growth bytes copied | 63,488 | 7,936 |
| Reserve bytes copied | 0 | 0 |
| Fresh From allocation | 51,712 B | 51,712 B |
| Final graph allocation / used tape copy | 60,504 B / 59,680 B | 60,504 B / 59,680 B |

The net observed saving is **49,104 managed B and 55,552 copied B/business**. The earlier private clone-removal saving is not counted again. Diagnostic timing is excluded. The first PostgreSQL capacity trace was interrupted by disk exhaustion; its partial trace and failure remain. The successful `run-02` is separate. Only hash-verified duplicate archives and reproducible new build intermediates were reclaimed, with receipts; original raw data and actual ELF/debug/native/package/generated inputs remain.

## Ordinary reversed screen

An explicitly quiet window ran 16 processes serially, with 256 warmups and 4,096 measured operations/process: related32 and public union32, both providers, AB then BA. All 65,536 businesses passed, with zero business/oracle failures and zero retained native owners. Exact source, package, native, generated reader, workload, SDK and library matches were checked before comparisons. These isolated consumers use the original matched native pair; their absolute values must not be added to the newer integrated-native measurements.

| Related32 round | CPU delta | Service p50 delta | Service p99 delta | Peak RSS before → after MiB |
| --- | ---: | ---: | ---: | ---: |
| SQLite AB | −2.44% | −0.57% | −13.36% | 32.97 → 32.63 |
| SQLite BA | +0.29% | 0.00% | +8.70% | 32.86 → 32.93 |
| PostgreSQL AB | +5.73% | +0.44% | +7.96% | 31.66 → 30.67 |
| PostgreSQL BA | −6.15% | 0.00% | −22.22% | 31.18 → 31.05 |

All four pairs reduced whole-process managed allocation by 48.89–48.98 KB/success, approximately 8.65%. CPU and latency directions change between rounds, as do unrelated public-union controls. This supports the exact allocation/copy mechanism, not a stable endpoint gain or a stable CPU regression. Gen0 counts increased while Gen1 counts decreased; one PostgreSQL candidate process recorded one Gen2 collection. Do not infer fewer collections from fewer bytes. These consumers have no idle-release RSS or GC-pause observation, so neither receives credit.

The existing Binding AOT suite passed 253 assertions. The SQLite/PostgreSQL relation suite passed 1,224 assertions and 131 retirements with all owner counters zero, including parent-count, equal-length nonidentical keys, mixed-length ordering, quota/failure, public Combine and cleanup controls. Independent root source review found no additional mutable cache, borrowed span escape, public API change, early quota admission or semantic capacity charge. The hint remains private, bounded by2048 and the original envelope maximum, and only touches an empty uniquely owned command under its admission gate.

Full records are under `experiments/relations-recovery-04`: `capacity-results.md`, `capacity-resume.json`, `capacity-consumers/diagnostic/{sqlite/run,postgresql/run-02}`, `capacity-ordinary-01`, and correctness/cleanup receipts. Preserve those identities in the next immutable evidence append. Rebuild the actual combined package consumers after integration and repeat mixed regressions before freeze.
