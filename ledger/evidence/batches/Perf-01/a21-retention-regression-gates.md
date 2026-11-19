# Perf-01 A21 retention investigation and regression gates

This source-only note does not approve or implement deferred retention. First
run the separately reviewed profiling launcher at NativeWeave
`47897840bc4875df1a9ff343490deea26be00cc6` in an exclusive diagnostic window.
It records actual generation-specific GC intervals and synchronous generator
method durations without changing GC policy. Its outputs are profiling-only.
Root and the independent codec reviewer reported no source blocker; neither the
author nor independent reviewer executed it before this note was written.

## Existing callers

| Caller | Use of A21 | Consequence for a possible change |
| --- | --- | --- |
| `src/Benchmarks.Domain/cell_worker.py:23` | Calls `a21.run_cell` for B23 and Perf-01 database cells | A run-cell-specific opt-in could be kept within the relevant path; preserve its exact completed observation schema and supervision ownership. |
| `tests/Perf01.Protocols/run.py:174,209` | Constructs `a21.RunState` and calls `state.event` directly | A global change to RunState affects HTTP/gRPC even if they never call A21's run_cell. Protocol lines208 already replace completion counters with one shared unavailable-counter dictionary; its per-completion counter graph is not the same as DB's separately decoded graphs. |
| `tests/Perf01.Protocols/run.py:317,338` | Removes target_counters when serializing final/partial request ledgers | The shared live dictionary remains available during the load; any default-semantics change needs protocol regression. |
| `tests/Perf01.Codec/driver.py` | Uses A21 hashing, host/resource helpers and percentile calculations, not RunState or run_cell | A scoped retention change should not change its execution; frozen A21 file hashes still affect provenance if the common file changes. |
| `src/Benchmarks.Domain/run.py:164–211` | Validates B23 observation schema before reporting | Preserve IDs, statuses, cardinality, stage timestamps, all outcome counts, histogram shape and measurement denominator. |
| `src/Benchmarks.Domain/export_cohort_observations.py:298–314,452–458` | Reads concurrency and last-counter/report fields | Do not change fields or silently improve an existing unavailable field while changing retention. |
| `tests/Perf01/verify_long.py` and Plan comparison extractors | Read raw scalar timing/status fields; comparison code also checks the original normalized value | Reconstructed final observations must remain readable and equivalent. Long credit is a separate existing check. |

`RunState.event` stores target_counters before the late-completion branch, while
the normalized row value is assigned only when the request has not already
finished. Late event payloads are preserved in `late_events`. Those distinctions
are part of the current schema; a generic reconstruction that fills every row's
value from its last wire completion would change semantics.

## Existing executable gates

`tests/Benchmarks.Harness/test_harness.py` contains the following relevant gates:

- `AccountingTests.test_malformed_counter_and_event_shapes`,
  `test_unknown_counter_is_not_zero` and `test_complete_counter_inventory`:
  malformed counters and unobserved-versus-zero distinctions remain live checks.
- `test_duplicate_completion_and_wrong_result` and
  `test_domain_oracle_requires_exact_dataset_and_preserves_result_shape`:
  duplicate/wrong results and independent structured Oracle semantics remain.
- `test_timeout_keeps_late_completion` and
  `test_late_event_cannot_win_before_timeout_poller`: deadlines cannot be won by
  a late event merely because timeout polling has not yet run.
- `ProcessTests.test_actual_dispatch_and_all_outcomes_are_retained`:
  unsuccessful outcomes remain in the ledger and denominator.
- `test_integrity_fault_stops_further_dispatch_and_retains_rows` and
  `test_malformed_event_is_persisted_before_rejection`: malformed wire bytes are
  retained, while live corruption still stops subsequent dispatch.
- `test_generator_capacity_invalidates_cell` and
  `test_generator_dispatch_lag_invalidates_cell`: generator failures remain
  invalid, with unchanged limits.
- `test_every_completion_counter_is_retained`:
  distinct per-operation counter values must survive final serialization.
- `test_late_completion_throughput_uses_observed_endpoint`:
  late target completion extends the measured denominator, not just the timeout
  timestamp.

The documented finite command is:

```sh
python3 -m unittest discover -s tests/Benchmarks.Harness -v
```

Use the locked Python and a separately permitted window. This note did not run
it. `tests/Benchmarks.Harness/verify.py` additionally builds/runs the three scalar
routes and the omission control; it is a larger component gate, not a DB load
or a substitute for semantic-equivalence fixtures.

## Minimal additional semantic comparison, if a change is justified

Feed the current and candidate state logic the same finite wire events and exact
controller timestamps. Keep the current behavior as the reference. Compare
complete final records, late_events, seen/completed/in-flight state, errors,
last-observed timestamps, byte counters, histograms and measurement denominator.
This deterministic test should cover:

1. Distinct structured values and changing per-operation counter values on
   ordinary, failed, rejected and cancelled completions.
2. A completion arriving after explicit timeout, and a completion crossing its
   deadline before the polling loop runs. Preserve the original row value's
   absence, retained counters, full late-event payload and later endpoint.
3. Malformed JSON and counter shapes, duplicate IDs/completions, wrong Oracle
   values, out-of-order admission and a corrupt final event. Rejection must
   happen during live dispatch, before post-load reconstruction.
4. Exact original raw-event bytes and hash. Never reinterpret a persisted but
   rejected event as an accepted payload during reconstruction. An accepted
   event index/offset may be a scalar bookkeeping input; it must not silently
   accept all parseable raw rows.
5. Interrupted/incomplete replay or malformed raw evidence: preserve the
   partial records and failed status, never fabricate fully reconstructed
   success. Root's existing watchdog still owns all processes.

A retention-only experiment must not recompute arrival/admission/completion
timestamps or move the observation endpoint after replay. Reconstruction and
serialization cost belongs outside the timing window but still needs bounded
cleanup and a complete final artifact. The default direct RunState contract
should remain unchanged unless its other callers receive an explicit migration
and the corresponding regressions.

## Remaining retained graphs

Deferred completion payloads would address only part of the Python object graph.
`Oracle.__init__` in A21 loads the entire expected-value dataset before the
measurement, including repeated 100-row page expectations; `run_cell` also
retains its nominal 20 ms resource samples. The profiler's post-run retained
result count is deliberately not a live during-load census of every graph.
These source facts do not establish which allocation/collection caused the
observed pauses. Preserve that distinction when deciding the smallest effective
measurement fix after profiling.
