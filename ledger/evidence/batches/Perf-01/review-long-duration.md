# Perf-01 independent long-duration verifier review

Reviewed NativeWeave commit
`3ad5f10a25eb6f52dc6d6e583db48ff840d2ffe5` in
`tests/Perf01/{verify_long.py,test_verify_long.py,README.md}`, with its
database README clarification. Reviewer: the protocol agent, independent from
the database agent who authored the verifier. Source-only commands ran on
CPU 8; this reviewer executed no syntax compile, synthetic test, verifier,
database, application, benchmark or build.

## Duration proof and protocol ordering

The accepted additional bound is `D - C >= 1800 seconds`: C is the
earliest observed successful ordinary completion; D is the last successful
ordinary operation's controller dispatch-start. Both use the same controller
monotonic clock. Original first-to-last dispatch span remains required and
cross-checked against the driver's reported value.

For protocols, `run.py:249–255` at companion driver commit
`d9c9572322c176f409f316e898103ca01d2eedcc` records dispatch before writing the
command to IPC. `Client/Program.cs:99–127` completes the actual independent
HTTP/hash or gRPC/protobuf/status/trailer checks, writes its raw operation record,
then emits the completion. The controller's `read_events` timestamps that
line before passing it to A21's `RunState.event`. A21
`nativeweave_bench.py:303–343` retains the observed completion on an on-time
success and does not turn a late timeout into success. Thus the selected
completion is after real work, and the later dispatch precedes its real work.
No cross-process Stopwatch conversion is needed for this subtraction.

The verifier's compact ID ledger requires every offered ID once, all logical
outcomes successful, valid event ordering, a common frozen arrival origin and
period, and dispatch lag within the original policy. Protocol inputs come from
the hashed frozen oracle. Raw client logical status, correctness flag and
scenario/protocol must match the same ID. `http-cancel`, `grpc-cancel`
and `grpc-deadline` are excluded from both duration endpoints while retaining
their original logical checks and accounting.

The IPC bound D minus the first dispatched command's admission remains
diagnostic only. A later ID can complete before the first ID is admitted; adding
an independent 1800-second threshold to that particular admission would reject
some correctly proven ordinary-operation spans. The final source and synthetic
regression preserve this distinction. Neither admission nor a scheduled guard
alone establishes wire/codec duration.

The prospectively scheduled 1802 seconds is not itself evidence. Protocol
preparation now allows that bounded value in
`0bab962f56aacd3dd77f7e3d0b6a421e95ca782f`; the database agent independently
source-reviewed that narrow Python-only change. It changes no period/count
formula, C# client/server or existing long-profile mix. Both versions must use
the same frozen choice and still pass the observed proof.

## Other gates and resolved review findings

The source retains original validity/completion and all-success counts,
fixed 500 ms arrival p99 and 256 MiB application RSS constraints, same-process
recovery, native identity and owner-drain checks. The raw p99 test counts samples
at or below the limit using the same nearest-rank threshold; it does not average
percentiles or silently discard slow successes. Codec measurement-phase RSS is
read across the interval, so normal endpoint snapshots cannot hide an observed
middle peak. Missing measurements stay unavailable or fail the required gate.

Database arrays are streamed rather than loading the entire A21 ledger;
protocol and codec JSONL are streamed. A bounded ID bitmap detects range/duplicate
errors. The finite synthetic source includes actual-shaped records for both
database providers, protocol oracle/client evidence, codec evidence, probe
exclusion, late first admission, missing IDs, errors, lag, RSS/tail/recovery
failures and hash/profile rejection. Reading these tests is not claiming they
have passed execution.

One source-review blocker was fixed before acceptance: malformed but valid JSON
shapes could raise AttributeError, and non-finite numeric corruption could raise
OverflowError, outside the previous failure-receipt exception set. The final
source catches these schema/conversion failures as unsuccessful zero-credit
receipts, and the finite test source covers summary arrays, null target shapes
and infinite lag. A bounded nonempty codec sequence prevents invalid modulo
selection. Existing receipt paths are refused; failed inputs are not rewritten.

The documentation also now distinguishes prior-hash verification from newly
pinning an input. Protocol/codec raw files have recorded expected hashes.
Database raw observation/resource files lack a prior hash in the existing
summary; this verifier hashes their current bytes and checks consistency but
does not prove arbitrary historical edits never happened. That limitation
must remain visible when packaging final evidence.

## Disposition and remaining execution

No remaining source blocker was found in the reviewed duration/order,
full-count, p99, resource, protocol-join, schema-failure and cleanup scope.
The author's Plan record is
`209dafdf7e0c3b2ffefe15927d86449674c25bea`. Root must still execute the
finite synthetic tests and run the verifier against each actual completed long
cell. A passed single-cell receipt does not establish paired before/after
equivalence, measured noise significance, freedom from host interference, or
completion of all ten required segments.
