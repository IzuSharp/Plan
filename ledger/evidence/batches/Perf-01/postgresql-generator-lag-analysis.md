# Perf-01 PostgreSQL revision-3 generator pauses

This is a bounded read-only analysis of two completed, invalid calibration
cells. Root authorized reading these existing ledgers during the exclusive
calibration window; the analysis ran only on CPU8 and started no application,
test, profile or new load. It changes neither the 100 ms dispatch-lag criterion
nor either original invalid verdict.

Inputs are under
`perf01-evidence/calibration/before-postgresql-v3r1/`:

- `13-confirmation-2-190`
- `17-confirmation-2-171`

The analysis streamed each `observation.json`, read its existing `summary.json`
and `plan.json`, and correlated the selected application's
`generator-resources.jsonl` and `application/resources.jsonl`. Event times below
are the raw A21 per-operation `admission_ns` and
`target_completion_observed_ns` fields, ordered on the controller monotonic
clock. This is not a new instrumented trace of individual Python calls or an
independent measurement of file-write duration.

## Observed pauses

| Cell | Successful / offered | Arrival p99 | IDs above 100 ms dispatch lag | Individual lag | Previous-to-first-bad dispatch gap | Scheduled time within measurement |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| 190/s confirmation 2 | 11,401 / 11,401 | 242.064451 ms | 10239 | 104.919316 ms | 110.059014 ms | 53.889474762 s |
| 171/s confirmation 2 | 10,262 / 10,262 | 131.894956 ms | 9841, 9842, 9843 | 117.215516, 111.441795, 105.603527 ms | 123.002713 ms | 57.549705473 s |

Both raw A21 records are invalid with the sole recorded reason
`generator saturation: dispatch lag`. Correct responses and a p99 below 500 ms
do not make them valid generator observations.

For 190/s, dispatch10238 is at `12827528401022` ns and dispatch10239 at
`12827638460036` ns. The last observed completion before the pause is cycle10234
at `12827530846012` ns; the next observed completion is page10237 at
`12827639941071` ns, an event-observation gap of **109.095059 ms**. Subsequent
dispatches catch up: IDs10240 and10241 are recorded at `12827638545034` and
`12827638554638` ns.

For 171/s, dispatch9840 is at `13109482049596` ns and dispatch9841 at
`13109605052309` ns. The last observed completion before the pause is cycle9816
at `13109486263940` ns; the next is cycle9826 at `13109605261645` ns, an
event-observation gap of **118.997705 ms**. Catch-up dispatch9842/9843 occurs at
`13109605126541` / `13109605136226` ns.

The A21 process's own nominal 20 ms resource sampler also stops producing start
timestamps across each interval. Consecutive starts are:

| Cell | Last earlier sampler start | Next sampler start | Interval |
| --- | ---: | ---: | ---: |
| 190/s | 12827523549360 ns | 12827638693127 ns | 115.143767 ms |
| 171/s | 13109465463022 ns | 13109603542299 ns | 138.079277 ms |

That sampler executes in the A21 scheduler process and observes the child target
process's memory. Its sampled RSS value must not be mislabeled scheduler RSS.
Scheduler CPU/RSS below comes from the separate named-role observer.

## Resource correlation

No measured interval of the target's nominal 1 Hz target/scheduler/controller
resource collection overlaps either dispatch gap. The target process continues
sampling the actual application during the A21 pause:

- 190/s: observations starting at `12827577428756` and `12827629625603` ns
  take 1.264989 and 1.249165 ms respectively.
- 171/s: observations starting at `13109515974029` and `13109571572607` ns
  take 5.134242 and 1.274244 ms respectively.

All observed generator masks near the pauses are `[0,1]`. Descriptor counts are
stable around these windows. The existing 1 Hz observations give the following
coarse CPU context; CPU percentages use one core as 100%.

| Cell | Role | Measurement CPU | CPU over the roughly 1 s interval spanning pause | RSS before → after that interval |
| --- | --- | ---: | ---: | --- |
| 190/s | Scheduler | 14.3596% | 24.7803% | 237,109,248 → 239,849,472 bytes |
| 190/s | Target | 67.1950% | 60.4755% | 92,209,152 → 93,290,496 bytes |
| 190/s | Controller | 1.4890% | 0.9911% | 76,632,064 → 76,632,064 bytes |
| 171/s | Scheduler | 11.9654% | 17.8559% | 226,418,688 → 228,966,400 bytes |
| 171/s | Target | 53.4737% | 60.5365% | 90,701,824 → 91,582,464 bytes |
| 171/s | Controller | 1.2302% | 0% | 72,814,592 → 72,814,592 bytes |

Scheduler measurement RSS peaks are 255,164,416 bytes at 190/s and 234,553,344
bytes at 171/s. These are generator resources, separate from the application's
256 MiB service limit. The coarse CPU intervals do not identify or rule out a
short stall; low average CPU is not causal evidence.

## Source localization and remaining uncertainty

In `src/Benchmarks.Harness/nativeweave_bench.py`, `read_events` records
`observed_ns` immediately before synchronous raw-event JSON/base64 writing,
`flush`, `json.loads` and `state.event` (lines383–393 in the inspected source).
The last visible pre-gap event in both cells is a cycle completion near ten
thousand operations. The dispatch loop at lines407–438 and the synchronous
`observe_process` call in the nominal 20 ms sampler at lines396–402 provide no
intermediate progress timestamps during the same gap.

The evidence localizes absent progress to the A21 process's event reader,
dispatcher and sampler. An ordinary yielding wait on `stdin.drain` alone would
permit the other event-loop tasks to run, so it does not by itself explain all
three pausing while the separate target process continues sampling. This is a
source-based distinction, not a measured identification of one blocking call.

The cohort has no GC callback durations, synchronous file-write/flush durations,
end-of-`observe_process` timestamps or operating-system scheduling trace. It
cannot distinguish synchronous event logging, JSON/counter processing, procfs
sampling, Python GC or external descheduling. No missing cgroup or hardware
control is inferred from this evidence.

A bounded hypothesis for a later separately owned diagnostic window is Python
collection of the growing retained object graph: `RunState.records` keeps each
decoded `target_counters` and normalized result, while resource samples are also
retained. The growing scheduler RSS and occurrence near ten thousand operations
make this worth instrumenting. They do not prove that GC caused either pause.
Any diagnostic run must remain outside formal timing and preserve the original
invalid samples. There is no new acceptance, throughput or optimization claim
in this note.
