# Perf-01 final-freeze proposal review

Status: **proposal only**. The independent audit branch starts at Plan
`3715d8eb2a4e5d98f51ed6994dbeefb497d55c53`. The proposed bindings remain in
[frozen-execution-draft.json](frozen-execution-draft.json); this work deliberately
does not create `frozen-execution.json`. Root retains integration, scheduling,
final review and publication ownership. No runtime change or long measurement
was performed or authorized by this proposal.

## What the proposal resolves

The [codec proposal](codec-final-freeze-proposal.md) binds actual W1 and W2-r241
noise receipts, preserving the failed 268/s process and prior 384/s capacity and
307/s proposal as history. W2 is now 241/s for 67 seconds, and its predeclared
paired long rate is 192/s. W1 stays 134/s for 120 seconds. The before producer,
A21, codec driver, corpus, limits, ownership and all service standards are
unchanged. The author only inspected and copied small existing metadata; W1
already had its receipt, so no conditional extraction was needed. The
[metadata audit](checks/final-freeze-proposal-001/metadata-audit.json) gives exact
copy provenance and explains that raw ledgers and binaries were not rescanned.

The existing protocol noise index remains
`af9b4a68014c231fbc8c6b3e651a310045e155d83bd06d1bd9cbf4fe3b5bed20`.
Its 6 partitions cover HTTP/1.1 and HTTP/2 lightweight requests and completed
1 MiB/8 MiB transfers, two unary sizes, and all three gRPC streaming directions.
The optional descriptive partition concurrency grid is explicitly skipped.
Existing and required mixed capacity ladders plus paired C64 long groups retain
high-load, cancellation/deadline, recovery and drain coverage. This decision
adds no new workload and does not waive the actual fresh comparisons, after/
direct ladders or ten valid long segments. C4 noise never applies to a different
load or concurrency.

Database timing still uses checkout
`ce2a3c75cbd535490897d062b6cbb7c095408307` with reader SHA-256
`8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4`.
The distinct post-run verifier is
`3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82`.
No identity is retroactively substituted into a calibrated timing process.

## Exact global command order

The draft now has explicit `long_acceptance.before_global_command_order` IDs.
Resolve each ID through its named command document and selector. The global
order governs; do not iterate the database document's historical SQLite-first
local `execution_order` as a global queue.

| Group | Command selectors in execution order | Proposed paired load |
| --- | --- | ---: |
| HTTP | protocol group `http`: `prepare`, `measure`, `verify-after-processes-stop` | 500/s, C64 |
| gRPC | protocol group `grpc`: `prepare`, `measure`, `verify-after-processes-stop` | 128/s, C64 |
| PostgreSQL | `database-before-postgresql-long-001`, `database-before-postgresql-verify-001` | 144/s, C16 |
| SQLite | `database-before-sqlite-long-001`, `database-before-sqlite-verify-001` | 40/s, C16 |
| Codec | `codec-before-r241-long-001`, `codec-before-r241-long-verify-001` | 192/s, 2 workers |

Each verify command runs only after its load stops and all owned processes have
been accounted for. Repeat the same group order for the actual after version
using separate immutable producer/run receipts. The actual binaries, conditions
and run identities remain required; this table contains no execution receipt.

## Root integration and finalization steps

1. Integrate actual recovery receipt commit
   `411bd7757cfe2972eee51d146012685bd90c9771`, archiver commit
   `226f9289296dc5b773594197a9834dce18131868`, and this proposal into the shared
   Perf-01 branch. Preserve all original failed/partial evidence. This proposal
   does not change the shared branch or push any commit.
2. For `pack_evidence.py` and `archive-evidence-linux.md`, replace the explicit
   pending draft bindings with the actual integrated bytes and lengths. The
   desired packer SHA-256 is
   `057e33d857e362a3e890b72b785c006df6f53a9234518ea93b29ef0bfd7724f8`.
   The archiver branch's source, 19-test execution and independent review are
   recorded at `checks/archive-protocol-projection-002`. Its change streams
   oversized protocol control metadata during post-run publication; it changes
   no timed driver or verifier and creates no need to recalibrate a workload.
3. Review all final source/producer/noise/config references and the explicit
   global command order. Check again that no runtime edits predate the intended
   freeze. Create a distinct immutable `frozen-execution.json` from the reviewed
   integrated proposal, marking only its actual root-finalized state. Commit
   and push it and the actual before noise bindings before any runtime edit or
   formal long execution; record its Git commit and SHA separately.
4. Record actual after source/build/package/native identities later in distinct
   immutable manifests referencing the final freeze SHA. Do not rewrite the
   final freeze, before manifests or noise receipts to insert future hashes.
5. Keep actual complete raw publication, retention and readback fields pending
   until publication has succeeded and bytes have been retrieved and checked.
   Small metadata in Plan is not full raw retention, and local scratch has no
   durability guarantee. Root is separately preparing the real publication.

No completed before/after long segment is claimed. The final acceptance still
requires 10 distinct valid segments, each with at least 1800 seconds of actual
qualified load, totalling at least 5 hours; all current accepted seconds are
zero. Future performance and maximum-throughput conclusions depend on the
remaining equivalent fresh comparisons, regressions and valid long segments.
