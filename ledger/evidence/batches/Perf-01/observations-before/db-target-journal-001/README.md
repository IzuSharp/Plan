# Actual compact-target journal profile and complete-evidence audit

The root-owned profiling-only 171/s, 120-second PostgreSQL mixed/C16 run
`db-generator-target-streamed-001` completed with **20,522/20,522 measured
successes**, valid generator accounting and the unchanged service standard.
The loaded product and all application/native hashes match the earlier
`db-generator-streamed-001`: clean product
`ea5fa528035d025bd7a28698ee7c71194432236c`. The new profile's measurement-driver
commit is `99035efb3b35a534e7d817d5bbd93642e5675640`. Timing, workload settings, producer
artifacts and A21 bytes were checked equal; only DB measurement-tool storage and
receipt reading changed. These are not before/after product optimization rows.

| Existing profile observation | Earlier retained target outcomes | Journal / streamed target receipt |
|---|---:|---:|
| Target measurement RSS sampled peak | 152,498,176 B | 55,144,448 B |
| Target final reconciliation RSS sampled peak | 181,960,704 B | 78,344,192 B |
| Target measurement CPU (% of one core) | 52.392805 | 51.666363 |
| Scheduler lifetime RSS high-water | 90,337,280 B | 89,706,496 B |
| Measured successful-operation p99 | 101.755224 ms | 74.715633 ms |
| Complete application receipt bytes | 42,562,221 | 42,562,221 |

The target's sampled measurement peak is 97,353,728 B (63.84%)
lower, and its sampled final reconciliation peak is 103,616,512 B
(56.94%) lower in these two observations. This is
an actual measurement-harness memory difference, not an independent-process
noise analysis, a product speedup claim or proof of the eventual long-run peak.
Target phase samples do not establish its whole-lifetime serialization peak;
`getrusage` above is explicitly the separate scheduler process. Mutation/oracle
and 20 Hz resource ledgers remain finite O(requests/duration).

## Full payload proof was retained

The authorized post-run audit ran on CPU 8 in 2.821 seconds after
the profile completed. `audit.json` is a verbatim copy of its actual receipt:

- All **20,538** final receipt outcomes equal the journal rows, with full values
  and the same completion order. This count is 20,522 measured plus **16 warmup**;
  independent recovery remains in its separate receipt.
- The journal's **17,491,951** bytes, row count and live SHA-256 agree, and it is
  sealed, closed and successfully published. Its SHA is
  `dda3041ac597e75326634d700c8b38bac668b1876232fad27ced54b0b639f562`.
- All **20,522** A21 records retain matching full normalized values by ID and
  **389,918** counter entries. The audit independently checked **10,261** complete
  100-row pages and **10,261** durable-cycle normalized results against the fixed
  input contract.
- The complete final receipt, journal, A21 observation and profile/source/manifest
  hashes are pinned in the audit. The current Python files match the profile's
  frozen pins; A21 remains
  `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53`.

The equality of old/new final file sizes does not claim their complete bytes are
identical: real concurrent completion order and run metadata can differ. The
finite test separately proved exact pretty-byte equivalence for identical input
values; this audit proved exact journal-to-final-receipt content/order for the
actual completed run.

Original evidence is under
`/workspace/scratch/01c249676f47/perf01-evidence/profiling/before/db-generator-target-streamed-001`;
the original audit is
`/workspace/scratch/01c249676f47/perf01-evidence/functional/db-target-receipt-audit-001/audit.json`.
Successful final receipts embed every outcome and are sufficient for the existing
public archive. The duplicate journal also remains locally available. Interrupted
journals and partial temporary receipts retain failure status and earn no credit.

No new application load or instrumentation was started by this audit. The root
has started fresh compact-v5-target DB calibration. Earlier compact-v4 selections
remain preparation evidence, and no old noise band is reused. This profile earns
**zero** 30-minute acceptance credit.
