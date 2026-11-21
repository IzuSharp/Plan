# Independent review of the actual layered profile projection

Status: accepted within the stated evidence-projection scope. This note records
the independent review delivered by the Perf-01 gRPC review agent to the
integration owner on 2026-11-21 UTC. It is not a GitHub approval by another
account, a new fixture execution, or formal performance acceptance.

Reviewed Markdown SHA-256:
`cdb00cb2a5ba172e0db1671b20382bbc7b3ac27f8cf15c67916ae761fc56f321`.

Reviewed numeric JSON SHA-256:
`ec4064caf2bfbfa0f903c9b9a8c9a9ab79fadbb22649046121bfe333cc1ddea6`.

The reviewer read both complete projections and necessary small reader/driver
source. The ledger reconciles 26 profile invocations and 44 finite child
receipts: 42 zero exits and two invalid PostgreSQL cycle producer exits.
The two failures remain outside performance deltas; all recorded children
retired with no remaining owned processes.

The reviewer checked 89 descriptive deltas and the associated denominators:
Inspect batches, page/retirement calls, PostgreSQL observation windows,
protocol measurement windows and approximate partial GC snapshot brackets.
No sign or denominator mismatch was found. Single-process percentiles,
whole-profile resources, unavailable direct-Rust/codec results and zero
formal/long credit are correctly distinguished. SQL durations and sampled
wait states are not subtracted from concurrent application wall time.

The public files contain no operational path maps, command argv, environment
values, raw PID maps, proxy values or TLS material. Review was limited to the
projections and small source files on CPU 8; the reviewer did not read active
noise data or original payloads, hash binaries, import a target module, run a
build/workload, or independently repeat the experiment. No blocking issue was
identified within that scope.
