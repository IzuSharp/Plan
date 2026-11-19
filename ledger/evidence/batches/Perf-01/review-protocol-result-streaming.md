# Independent review: protocol result metadata streaming

Date: 2026-11-19. Reviewer: Perf-01 codec subagent, separate from the protocol
patch author. Disposition: **source review passed**. Execution remains the
integration owner's gate; this review ran no benchmark, build, syntax check,
test or raw-ledger scan. All shell source reads used CPU 8 while database
calibration retained exclusive measurement resources.

## Exact reviewed source

The implementation and finite-test source are NativeWeave commit
`4c28329129ce50cc8273128889c349e97410c795`, based on
`ce2a3c75cbd535490897d062b6cbb7c095408307`. The subsequent documentation-only
correction at `1f0b3930458c21c325b2e3c7a57fdf73fd76de02` was also read; it leaves
the verifier and test source unchanged.

| File | Reviewed SHA-256 |
| --- | --- |
| `tests/Perf01/verify_long.py` | `3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82` |
| `tests/Perf01/test_verify_long.py` | `ab3027984343172e4911af3a406a46fabdd44cc105aeb85cbaece130ab1d3120` |

## Preserved acceptance contract

`check_protocol` now pins and hashes the complete original `result.json`, then
uses the existing `JsonStream.selected_object`/`skip` implementation to retain
only consumed metadata. It validates skipped container syntax and the end of
the document. The result bytes and schema are unchanged. The full-file digest
remains in the verification receipt, and the existing final
`Evidence.unchanged` check still detects input stat changes during verification.

The projection retains every field used by the existing protocol checks:
profiling eligibility, validity and service/drain/duration flags, invalid
reasons, status and exit code, all five operation counts, plan and evidence
hashes, recovery status/failures/call count, the measured dispatch span and
resource window, and the nested successful-arrival p99. The profiling-only
rejection formerly supplied by `Evidence.load` is explicitly applied after
projection.

All later checks are unchanged: frozen plan and producer hashes, independent
client results, oracle tokens, complete/unique request identities, expected
probe classification, continuous schedule and dispatch-lag limits, ordinary
operation duration proof, raw latency threshold, reported finite p99, sampled
RSS, recovery, actual native identity, Native AOT client and owner retirement.
The generic JSON parser, `Evidence.load`, database and codec branches, and timed
protocol driver are untouched. Other small summaries retain the 64 MiB guard.

## Finite-test source assessment

Three added methods exercise the intended boundary without a large workload.
The positive fixture uses actual multi-chunk JSON and a simulated 65 MiB stat,
proves the old small-summary loader would reject it, forbids whole-file
`read_text` and decoded histogram dictionaries, and checks the complete result
hash and returned p99. Negative fixtures cover all projected flags/counts,
recovery failures, tail limits or missing p99, span mismatch, plan/raw-evidence
hash mismatches, truncated or trailing JSON, malformed skipped containers and
missing metadata. Every negative expects no acceptance and zero duration
credit. Existing independent-client and probe-duration cases remain in place.
These are source-reviewed tests, not an execution or measured-memory claim.

## Documentation finding and resolution

The first README wording described the detached frozen database checkout as
already present. Root clarified that creating and verifying this checkout is
planned after the active calibration. Commit `1f0b393` now states that
prospective requirement explicitly; no existence claim remains. The integration
owner must preserve the exact parser bytes used by frozen timing plans while
advancing this separate post-run verifier. This review did not create, modify
or probe the active measurement checkout.

No remaining source blocker was found in the reviewed scope. Long-file parsing
time, peak RSS and actual long-load acceptance remain unmeasured by this review.
