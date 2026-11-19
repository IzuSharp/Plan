# Failed before gRPC long attempt: exact operation extraction

This checkpoint retains the failed 128 calls/s before attempt without changing its
verdict or the product. The domain driver completed, but `valid=false` and
`service_standard_met=false`. The frozen long verifier rejected it at the valid
flag and assigned **zero seconds of valid long-run credit**. Its exact receipt,
execution receipt and log are copied under `data/`.

## Findings

All **230,670 measurement client records** were inspected. They contain 230,647
logical successes, **17 `rejected` / `ResourceExhausted`**, **5 `cancelled` /
`Cancelled`**, and **1 `failed` / `IntegrityFailure`**. Expected protocol probes
remain successes: 4,613 `ExpectedCanceledStream` and 6,921
`ExpectedDeadlineExceeded` outcomes. The other 219,113 successes are `GrpcOK`.

The sole correctness failure is measurement ID **22468**, scenario `grpc-cancel`:
`Wait headers were not committed.` It records one submitted request, zero response
messages and zero response bytes. The actual frozen client checks the required
`perf-started: yes` initial header before reading this stream and before setting
its intentional-cancellation flag. The record therefore establishes a required
initial-header assertion failure, **not a recorded protobuf/content mismatch**.
The adapter did not retain this call's underlying terminal status or trailers;
nearby `ResourceExhausted` records do not establish that missing status. The
original broad `response/protobuf/hash correctness failure` invalid reason is
preserved unchanged.

Failures are early clusters, not a late-only pattern. Relative times below use the
client's recorded 1 GHz timestamp frequency and its first measurement start. A
cluster is descriptive: adjacent failed-operation starts no more than one second
apart are grouped together.

| Client start interval, seconds | Last completion, seconds | Rejected | Unexpected cancelled | Header assertion |
| --- | ---: | ---: | ---: | ---: |
| 13.897160–14.141298 | 14.174201 | 10 | 2 | 0 |
| 175.569773–175.570549 | 175.574686 | 1 | 2 | 1 |
| 370.649541–370.827084 | 370.882483 | 4 | 1 | 0 |
| 402.952433–402.959253 | 403.205007 | 2 | 0 | 0 |

No later non-ok measurement operation was recorded through the final client
start at 1,802.099671 seconds. All **179,090 measurement IDs above 51579** are
logical successes. This later successful interval does not repair the failed
attempt or prove that another rate will pass.

Each selected operation joins the exact client record, controller request,
dispatch, admitted/completed events, and frozen Oracle entry. Selected-operation
dispatch lag ranges from **0.128104 to 42.905356 ms**. This is a description of
these 23 operations, not an assessment of the entire generator's scheduling.

## Existing resource observations

The extraction includes only 19 existing resource snapshots that bracket the
selected operations, with original file line numbers and per-operation time
offsets. Native gauges are embedded in `execution/server/managed-resources.jsonl`;
there is no separate native-resources ledger for this cell. UTC timestamps align
the snapshots with controller dispatch records. Completion UTC is estimated from
the dispatch UTC anchor plus the controller's own monotonic elapsed time.

The original result reports measurement maxima of 53,426,604 native payload bytes,
3,147,372 managed payload bytes, 21 active requests and 26 retiring requests. It
reports server CPU at 49.222863% of one core, sampled server RSS maximum
121,081,856 bytes, 2,526,112,386,832 managed allocated bytes and 174,370 Gen2
collections. These are recorded aggregate or sampled observations. They do not
identify a rejected native grant, a request's quota ledger, or between-sample
ownership peaks. No quota cause is inferred from them.

The final closed record reports `Completed`, `Disposed`, zero pending requests,
and zero retained managed/native bytes. Successful cleanup does not change the
measurement failure.

## Evidence and reproducibility

- [Extraction receipt](data/receipt.json): all 23 exact selected records and joins,
  original result flags, source hashes, 19 resource observations, and limitations.
- [Frozen verifier rejection](data/long-verification.json),
  [its original execution receipt](data/long-verifier-execution.json), and
  [its log](data/long-verifier-execution.log): exact copies, not regenerated verdicts.
- [Extraction execution](execution.json) and [log](execution.log): the actual
  bounded CPU8 offline extraction, 2026-11-19 16:47:37.946570–16:47:44.542966 UTC,
  exit 0. The existing timing lock was held exclusively. No load, profiling,
  build or product mutation was performed.
- [Extractor](extract.py): reuses the frozen reader and the selection/join method
  from `../grpc-v5r1-failed-operations-001/extract.py`, with an explicit 300,000-row
  cap for this fixed 230,670-operation cell and a 256-failure cap. It checks full
  raw-file SHA256 values, original count/status binding, complete selected joins,
  and unchanged file identities before writing the checkpoint.
- [SHA256SUMS](SHA256SUMS): hashes of the committed checkpoint files.

Raw input directory:
`/workspace/scratch/01c249676f47/perf01-evidence/long/before/grpc-001`.
The raw files were not modified. The original result SHA256 is
`6e6fec1cbca36e7fa0b78afe64323f7d0e3fa35f20b76bc65665462dc72308e8`;
the client operations SHA256 is
`e8950817ece2ad6b9bbb8af3e74cac63bdc4e1cdf743256652f49f97d461d98f`.
The receipt pins all consumed raw inputs and the actual frozen client source
`perf01-build/before/protocols-v2/source/Client/Program.cs`, SHA256
`6bfc40c993b7f02ffd4406606d78b692c298482cc786717cdd05316688a4ea4d`.
Source classification comes from `ExecuteAsync` lines 111–126 and the `Wait`
header check at line 207 of that exact source.

Run only after formal timing has stopped, using a fresh output directory:

```sh
taskset --cpu-list 8 \
  /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B \
  ledger/evidence/batches/Perf-01/checks/grpc-before-long-failed-operations-001/extract.py \
  --root /workspace/scratch/01c249676f47 \
  --nativeweave /workspace/scratch/01c249676f47/.worktree/Perf-01-linux/NativeWeave \
  --output /workspace/scratch/01c249676f47/perf01-evidence/diagnostic/grpc-before-long-failed-operations-reproduction-001
```

This small failure checkpoint is intended for permanent Plan history. Publication
and readback of the complete raw long-run evidence remain part of the existing
Perf-01 archive task; this extraction does not claim that upload is complete.
No new load, prospective rate, or acceptance rule is selected here.
