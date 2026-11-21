# Epoch-002 original control inventory

Status: source inspection and unexecuted build/B18 caller preparation only.
EA5 is the actual prospective before product; the common application harness is
`2e3995df8d86583ee9443348276ca8d918056bfc`. The final corrected product commit is
not selected by this document. No previous binary, timing, noise or long-test
acceptance is transferred. Current long completion is **0 before + 0 final**.

The prospective freeze is
`recovery/epoch-002/freeze.json`, SHA-256
`a1cc0cfb0d354335a90c61f64941353bba899fbc9916c716ad839cc7e6402cd5`.
Its inherited policy, CPU split, fixed rates, resource limits, data and
durability settings are unchanged. Fresh toolchain, artifact, TLS and noise
identities are still required. The old private TLS key was lost; no byte
recovery is implied.

## Public source that survives

NativeWeave paths below are at the common 2e commit. Plan paths are relative to
`ledger/evidence/batches/Perf-01`. Exact inspected source hashes are recorded in
the adjacent `control-source-index.json`.

| Purpose | Actual original entry point | Reuse boundary |
|---|---|---|
| Build and bind | `diagnostics/recovery-build-001/build.py::plan/completed`; `bindings.py::role/common` | Eight role producers, three common producers; native, full B24, A17 codec and shared packages are checked separately |
| Finite owner | `diagnostics/recovery-build-001/owner.py::command` | Retain the existing owner; no replacement timer, process supervisor or load generator |
| B18 native tests | Native `native/protocols/grpc/verify-native.py` | Run on each clean selected product source; actual crate tests, host tests, Clippy, exports and upstream-source checks |
| B18 assembled/package tests | Native `tests/Protocols.Grpc/verify.py` and `package_probe.py` | Bind actual selected Server asset and component receipt; original JIT/AOT and ordinary edited consumer proofs |
| Database application | Native `tests/Perf01.Database/run.py::prepare/execute_cell`, `target.py` | Original strong typed application, fresh DB context, independent persistence, overload classifications and observers |
| Database comparison | `database_compare.py::read_cell/extract` | Original per-call observations, whole/cycle/page metrics, resource and persistence checks; A21 comparison |
| Database noise | `database_freeze_anchor_noise.py::main` | Original band is max(1000 ns, range of three before-only process means), relative band zero; its historical document/parent admission cannot simply be relabelled |
| Database capacity | `database_observer_calibrate.py` | Original finite ladder/refinement/confirmation algorithm; keep deferred GC and threaded resource observer |
| HTTP/gRPC application | Native `tests/Perf01.Protocols/run.py prepare/run`, `adapter.py` | Actual TLS sockets, independent common client, original profile, response/content/protobuf/cancellation and drain checks |
| Protocol cohorts/noise/comparison | `protocol_cohorts.py --stage noise/compare`; `protocol_compare.py freeze/compare` | Six ordinary partitions; three independent before-only processes per scene, then three per role with the same common client/TLS |
| Protocol capacity | `protocol_calibrate.py` | Original policy-4 ladder and three fresh 60-second confirmations; source validates actual complete/eligible producers |
| Codec application | Native `tests/Perf01.Codec/driver.py measure` | Frozen corpus, both APIs/actions, real native/direct/managed routes, separate raw payload and encoded counts |
| Codec noise/comparison | `codec_compare.py freeze/compare` | Same original before-only noise rule and A21; per-case/action/interface measurements remain separate |
| Codec capacity | `codec_calibrate.py` | Original finite capacity procedure with actual build/corpus identity |
| Long acceptance | Native `tests/Perf01/verify_long.py --group GROUP --output CELL --receipt NEW` | Independent streamed verification of each actual completed cell; effective duration must reach 1800 seconds |
| A21 arithmetic | Native `src/Benchmarks.Harness/nativeweave_bench.py::percentile/noise_comparison` | Preserve original quantiles and seeded 2000-bootstrap confidence interval; do not manufacture a new noise band |

The surviving weak-experiment `protocol_compare.py` differs from the main
reader only in its hardcoded before commit. Its curated 18 fixed-load and 28
capacity processes explain the rejected weak-cache candidate; they are not
fresh EA5/final results. The original main EA5 reader is the appropriate source
for new main-pair admission, subject to the required schema review.

## Concrete remaining control work

The new `diagnostics/recovery-measure-002/run.py` covers only build, common
producer binding and B18 functional support. It delegates original producers
and finite ownership rather than reconstructing the missing private wrappers.
Its input keeps the after source unset until an explicit selected final SHA is
supplied, permitting the fresh before build to proceed first.

Before any new timing caller is admitted, bind the real role manifests,
actual loaded native assets and B18 receipts, complete restored toolchain and
Python bundle, the new common TLS identity and the exact current source index.
Review original readers against actual terminal/invalid and eligibility
schemas. Preserve failed rows, generator saturation and incomplete retirement;
an exit code alone does not confer acceptance.

Historical database anchor/noise/long wrappers include old frozen parent
documents and execution-path admission. Reuse their underlying workload and
statistical functions with a newly identified epoch-002 admission record; do
not fill those old records with new paths or hashes and call them recovered.
Protocol/codec original CLIs are already parameterized by actual builds,
profiles, TLS, corpus and new output. Root remains the only execution owner.

The ten required long segments use the inherited five group configurations on
each product version: PostgreSQL 144/s, SQLite 40/s, HTTP 500/s, gRPC 115/s and
codec 192/s, each scheduled for 1802 seconds plus its separate warmup, recovery
and idle phases. A schedule is not proof of 1800 effective seconds. The
original verifier requires successful-load coverage and correctness, resource,
error and retirement checks; none has run in epoch-002 at this checkpoint.

Next dependencies are specific: complete toolchain/Python manifests, root's
selected clean final commit, actual completed build/B18 receipts and a fresh
shared TLS pair. No new workload implementation or independent benchmark
algorithm is needed for this preparation.
