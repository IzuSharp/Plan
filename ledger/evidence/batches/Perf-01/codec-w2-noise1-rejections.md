# Perf-01: preserved W2 codec noise-cell queue rejections

## Disposition

The first before004 W2 noise cell at **268 operations/s**, two workers, failed
the zero-unexpected-error service standard: **16,108 offered, 16,105 successful,
three rejected**. The driver reports a complete, valid observation, successful
12/12 recovery, and zero correctness errors. This is a retained service failure,
not an invalid observation or a passing noise sample. It earns no long-duration
credit. The owner stopped the remaining W2 noise cells.

The rejected requests failed the target driver's **64-slot BlockingCollection
admission**, before worker admission or a native codec call. Both workers were
occupied while a backlog accumulated. Nearby long public codec calls and a
permitted generator catch-up burst are observed; the telemetry cannot apportion
their causes.

No workload, build, test, profile, rate change, or runtime change was performed
for this investigation. The owner explicitly permitted a bounded post-run read
on CPU 8 after stopping timing. The original cell remains untouched.

## Evidence and identity

Original cell:

    /workspace/scratch/01c249676f47/perf01-evidence/noise/codec-before004-w2/noise-1

The measured interval was **2026-11-19 14:05:40.501925–14:06:40.603405 UTC**.
Actual first-to-last dispatch span was **60.101185698 seconds**. Draining
completed at **14:06:51.654907 UTC**, followed by **5.021153396 seconds** of idle
observation. The target exited zero.

| Binding | Value |
|---|---|
| Product source | ea5fa528035d025bd7a28698ee7c71194432236c |
| Before004 manifest SHA-256 | d34298ebc8dc82b525f19860555947a1a04eff2bf8aecc38cede2922c81285a7 |
| Driver source producer | aa3399f0418a6d0910cc56697abfaa3769f32b54 |
| driver.py SHA-256 | 95e15eb609dc761e9de95bcef5b1bb84af9fcc3711ecdf5632ad6e34856c0165 |
| Corpus manifest SHA-256 | 92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d |
| Actually loaded native SHA-256 | 3a472d8e51ad5d69a28ade2b00cd23fc9a2bb8d9fa1e2c4df47b769316acff79 |

The [bounded extraction source](checks/codec-w2-noise1-rejections-001/extract.py)
and [derived receipt](checks/codec-w2-noise1-rejections-001/receipt.json) retain
all failures, selected nearby calls, observed backlog snapshots, telemetry,
resources, and final owner counters. Receipt SHA-256:

    739249b1ec313a0c5d82c9520ab28b7e0bdc55f819810f3f3f4c48395c510da0

The successful extraction streamed 21,508 operation rows, 64,625 event rows,
and 96 resource rows under explicit file/row/line bounds. It verified their
complete SHA-256 digests against the producing summary. It retained only a
fixed local operation context, approximately two seconds of event timing,
surrounding telemetry/resources, and final drain observations. It did not scan
calibration ledgers. The exact executed source bytes are retained in
[executed-source.json](checks/codec-w2-noise1-rejections-001/executed-source.json);
its SHA-256 matches the receipt. The reproduction script differs only by removal
of an extra blank line at end of file. No extraction was repeated for that
formatting adjustment.

## Admission failure and local timeline

[Program.Main at the pinned driver source](https://github.com/IzuSharp/NativeWeave/blob/aa3399f0418a6d0910cc56697abfaa3769f32b54/tests/Perf01.Codec/Program.cs#L55-L79)
creates the bounded queue and emits the normal rejected completion only when
queue.TryAdd(work) returns false. [Worker](https://github.com/IzuSharp/NativeWeave/blob/aa3399f0418a6d0910cc56697abfaa3769f32b54/tests/Perf01.Codec/Program.cs#L153-L206)
emits admission before calling the public codec; caught codec/oracle exceptions
produce failed, a different terminal status.

| ID | Measurement index / cycle slot | Scheduled offset | Dispatch lag | Dispatch to observed rejection |
|---|---:|---:|---:|---:|
| 7680 | 2292 / 52 | 8.552238156 s | 0.413424 ms | 0.137547 ms |
| 7681 | 2293 / 53 | 8.555969499 s | 1.207831 ms | 0.111659 ms |
| 7682 | 2294 / 54 | 8.559700842 s | 0.792333 ms | 0.094793 ms |

All three have no admission timestamp, and their target completion contains
only kind, id, and status=rejected. The first two were 256-byte compressible
owned compression requests; the third was 1 MiB near-incompressible owned
compression.

At each rejection the event ledger contained **67 dispatched outstanding
requests**: two observed active workers and 65 requests not yet observed admitted,
including the rejected request itself. This is consistent with 64 occupied
queue slots. The derived count includes pipe and observer delay; it is not a
direct queue-depth gauge. The target's rejection itself establishes that
admission failed.

| Observed active ID | Public operation | Public-call elapsed | Whole operation elapsed |
|---|---|---:|---:|
| 7600 | 4 MiB near-incompressible compression, NativeBuffer | 227.472362 ms | 228.331619 ms |
| 7615 | 1 MiB near-incompressible compression, array | 39.317744 ms | 39.488281 ms |

A preceding nearby 4 MiB near-incompressible array compression, ID 7533, reported
**338.283978 ms** for the public call and **345.324274 ms** for the whole
operation. The largest nearby gaps between observed admissions were
**145.183766 ms** and **113.386724 ms**. These elapsed/observer measurements
cannot divide the time into CPU execution, runtime suspension, and operating
system scheduling.

## Generator and GC limits of attribution

Across the bounded two-second dispatch context, maximum dispatch lag was
**47.321612 ms**, below the frozen **100 ms** limit. One 100 ms bin preceding
the rejection had **38 dispatches**, compared with approximately 26–27 at an
evenly spaced 268/s; the minimum adjacent dispatch gap was **0.009814 ms**.
A catch-up burst exists even though each failed request itself was dispatched
close to its scheduled time. It may contribute to admission pressure. It does
not make this cell invalid under the frozen generator rule.

Cumulative telemetry bracketing the failure changed gc0 from **81 to 84**
and gc1/gc2 from **65 to 67**. The same records reported zero correctness
errors. Collection counters have no pause start/end timestamps or per-thread
attribution. They establish collections in the roughly one-second bracket,
not a specific GC pause causing rejection.

The nearby resource bracket recorded target CPU **30.71→32.38 seconds** over
approximately one second, target RSS **97,263,616→68,042,752 bytes**, and generator
RSS fixed at **24,141,824 bytes**. The whole measured interval used
**62.96 target CPU seconds**, or **104.755036% of one core**. Its success-only
p99 was **133.087639 ms**. Average CPU and acceptable success p99 do not
override the three admission failures.

The final drained event and all five idle events report native live owners,
retained capacity, and active calls at zero, correctness errors zero, and released
owners **21,531**. Managed collection counters remained unchanged during idle.

## Relation to the earlier 384/s calibration

The [small-metadata phase comparison](checks/codec-w2-noise1-rejections-001/phase-comparison.json)
checks all three final 384/s confirmation plans against this cell. Their fixed
driver/A21/manifest/native/corpus/sequence, worker count, queue capacity,
inflight bound, deadline, lag allowance, and codec settings match. Calibration
used **5 seconds warmup and 4 seconds recovery**; this noise cell used
**20 seconds warmup and 10 seconds recovery**. Both used 60-second measurement
and five-second idle observation.

The [scheduler source](https://github.com/IzuSharp/NativeWeave/blob/aa3399f0418a6d0910cc56697abfaa3769f32b54/tests/Perf01.Codec/driver.py#L370-L420)
starts the same fixed, seeded, shuffled 160-entry sequence at index zero for
each phase while continuing global IDs. It waits for all pending completions
before returning from a phase. All **5,388 warmup** and **12 recovery** operations
succeeded. Failures 8.55 seconds into measurement are therefore not unretired
warmup requests. Different warmup lengths can leave different runtime and
allocator state; this diagnostic did not isolate that effect.

The three observed 384/s calibration confirmations remain valid historical
results for their recorded configurations, with 23,080/23,080 successes each
and p99 **110.590555 / 116.248592 / 110.282025 ms**. They do not establish that
the different fixed-load phase configuration is robust or guarantee the
prospective 307/s long run. This lower-rate failure also does not prove a
monotonic capacity bound or prove that 307/s must fail.

## Owner's before-only follow-up decision

Before any product edit or candidate observation, the owner selected a
deterministic whole-cohort stepdown: floor(0.9 × 268) = **241/s**, with
ceil(16000 / 241) = **67 seconds** measurement, unchanged 20-second warmup,
10-second recovery, queue 64, inflight 256, and all resource/latency/error bounds.
All three fresh processes must pass, including at least 16,000 actual successful
observations and at least 100 in each of the 32 case/action/interface rows.
Any failure remains preserved; the entire next cohort steps down again. No
favorable subset is reused.

If the 241/s triplet qualifies, the proposed paired long rate becomes
floor(0.8 × 241) = **192/s** under that matching phase configuration. This
prospectively replaces the old 307/s proposal; it is not a product improvement
or completed long result. The separate W1 noise receipt remains valid and is
already frozen at SHA-256
998e5701b312198e2a91e68ae62070d261e6bc2ae161561b4f9d535aaaf5f83c.
The owner authors and executes the revised command document. This diagnostic
changes no driver, engine, queue, policy gate, or command file.

## Reproduce this post-run extraction

Use a fresh receipt path; the extractor refuses overwrite:

~~~sh
source /workspace/scratch/01c249676f47/perf01-toolchain/env.sh
taskset -c 8 /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  ledger/evidence/batches/Perf-01/checks/codec-w2-noise1-rejections-001/extract.py \
  --cell /workspace/scratch/01c249676f47/perf01-evidence/noise/codec-before004-w2/noise-1 \
  --output /workspace/scratch/01c249676f47/perf01-evidence/codec-rejection-audit-new.json
~~~

The extraction hashes its source and consumed inputs. It is a diagnostic reader,
not a replacement for service, population, noise-freeze, or 30-minute gates.
