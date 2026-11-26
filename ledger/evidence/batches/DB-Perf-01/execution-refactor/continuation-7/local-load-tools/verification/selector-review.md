# Independent review of the local cohort selector

Reviewer: native_review, 2026-11-26. This is a pure offline source/control review;
no consumer, database, benchmark, calibration, pressure run or CI action starts.

## Disposition

Accept `select_load_cohorts.py` at SHA-256
`507afc98c5b448bba3daeae3c3fb77ea748d983029f42a6baf5870098abba43d`
for deriving the explicitly selected local plans. This does not qualify a host,
choose concurrency/rate, bind consumer packages to product source or accept a
performance campaign. Those are independent gates.

The selector requires the unchanged continuation-4 generator at SHA-256
`68deb860bd8ae1f0f268220e5c3b72606ff666b08a7511e1245d750b3fb1cc78`.
It reads and hashes the existing original plan, verifies its complete expected
format and all four commands, and preserves the original plan bytes. It does
not modify or execute the generator or runner. The runner is imported only to
call its read-only `validate_plan`; its database/process entry is under `main`.

| Derived lane | Required original lane | Original measured commands | Derived measured commands | Duration each |
| --- | --- | --- | --- | ---: |
| Baseline | offered, 30 seconds | before / candidate / dapper | before / candidate | 120 seconds |
| Final | final, 1800 seconds | before / candidate / dapper | candidate / dapper | 1800 seconds |

The original candidate fixture is preserved byte-for-byte as the first command,
with `--initialize --operations 0` and `timingRequested=false`. Its existence
does not add a measured cohort. Source input identities intentionally retain all
three cohort binaries, while the final derived command list contains only the
fixture plus candidate and Dapper. Both databases use this same selection.

Command argv equality fixes SQL-case roster, dataset, requested rows, mode,
session mode, warmup, queue capacity, rate, concurrency and affinity. Baseline
and final phase selection cannot reinterpret a wrong source lane. Durations,
timeout and final idle interval remain explicit. Every long-run acceptance flag
stays false; `finalCreditRequestedFor` expresses a requested later analysis,
not an awarded result.

Input executable/native/tool hashes and the complete original format are checked
again after deriving and validating the result. The original plan, generator,
selector and checkout HEAD are rechecked before writing. The exact full runner
source commit must equal HEAD, and its runner/manifest bytes must equal Git's
committed blobs. Consumer/native/package source provenance is explicitly left
to the separate freeze, rather than falsely inheriting that runner commit.

The target plan and result directory must be fresh, the plan cannot be inside
the result directory, and original evidence locations cannot be reused. Final
creation uses exclusive `open('x')`; there is no overwrite of an existing plan.
The runner validator also checks distinct, contained result paths that cannot
replace reserved observer receipts. The selector creates the plan only and
prints the eventual command for separate execution.

## Independent finite verification

Independently reran `check_load_selector.py` using the retained ordinary consumer
binaries and the original generator. All 236 controls passed with process exit
0. The C=2 and R=123 values are synthetic control inputs, not a proposed campaign
calibration. The result is `selector-controls-independent-01.json`; its four
original/derived pairs are in `selector-controls-independent-01/`.

Controls cover both providers and both lane kinds, exact fixture preservation,
the three-source/two-measured distinction, duration/rate/concurrency/queue
bounds, strict JSON keys/numbers, identities and executable aliasing, command
counts/order/roles, missing/extra argv, per-cohort mismatch, database/tool paths,
wrong input hash or source commit, and refusal to overwrite a plan or an output
directory. Original/derived plan hashes are retained and unchanged. All eight
`*-never-executed` result directories remain absent.

The record has `workloadProcessesStarted=0`. It supplies no throughput, latency,
CPU, RSS, allocation, GC or long-run acceptance measurement. No source or product
test run is inferred from successful plan derivation.
