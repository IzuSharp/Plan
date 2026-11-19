# Perf-01 A21 compact-observation candidate

This is a **measurement-tool change**, with no C#/Rust runtime, package,
application, database, arrival-rate or acceptance-threshold change. The source
candidate is NativeWeave `2804fe42e77dba61093be94380daceb1a06ccf3e`.
The optional post-run Oracle census immediately before it is `2ae897c`.

## Evidence and scope

The exclusive baseline diagnostic at
`ROOT/perf01-evidence/profiling/before/db-generator-001/` used the before package,
PostgreSQL, 171 logical operations/s, a 120-second mixed schedule, service CPUs
2,3 and generator CPUs 0,1. All 20,522 operations completed correctly, but the
original dispatch-lag rule invalidated the cell. It has no formal performance
or long-duration credit.

Its actual `a21-generator-profile.json` records four generation-2 collections
during `measurement-events`, with durations **68.557009, 189.579873, 127.447295
and 175.429638 ms**. Every one collected zero objects; three exceeded the
unchanged 100 ms generator-lag bound. The callback intervals are actual diagnostic
observations. They support removing unnecessary retained graphs from the
scheduler, while hook overhead prevents treating their durations as uninstrumented
product latency or claiming that every earlier stall had the same cause.

Source analysis identified two retained graphs. `Oracle` parsed a fresh 100-row
page expectation for every identical page input, and `RunState.event` retained
each validated completion's normalized value plus 19 counter observations until
the cell ended. The raw event log already preserved the exact accepted and
rejected wire bytes. The first graph exists before target startup; the second
grows with completed operations. See `a21-retention-regression-gates.md` and
`postgresql-generator-lag-analysis.md` for the original source and timing review.

## Minimal implementation

`--compact-observation` is an explicit Perf-01 DB option, passed through the
existing supervised B23 cell worker. It is recorded in target metadata, plan
features and frozen inputs. The two new A21 options default to false. Existing
direct `RunState` callers, including the protocol harness, retain full payload
behavior unless they explicitly opt in; the protocol driver does not opt in.

Before startup/timing, an ephemeral cache shares identical read-only JSON
expected values. It permits at most 1024 unique keys and 4 MiB of key bytes,
64 KiB per key, 4096 traversal nodes and depth 64. Unsupported or oversized
values keep their original objects. The dataset bytes/hash, input tokens,
value types and oracle comparison remain unchanged. The dataset still has to
be parsed in full; this is a retained-graph reduction, not streaming input.

During timing, event parsing, ID/admission/deadline/order checks, exact oracle
comparison, counter validation, success/error counts and last-counter snapshot
remain live. Compact state retains the original scalar row fields plus one
byte flag and one int64 raw-line ordinal per scheduled operation. Per-record
counter/value objects and full late-event payloads are reconstructed after
target/reader/sampler drain and after the original observation endpoint is fixed.

Replay streams bounded raw lines, matches accepted ID, observer timestamp and
raw-line ordinal, and restores original row fields and complete late metadata.
The ordinal prevents a same-timestamp duplicate from replacing an accepted
completion. An incremental SHA-256 of the exact live-written UTF-8 raw log is
verified during replay and retained as its evidence digest. Thus valid JSON
changes to counters, failed values or late statuses cannot pass merely by
preserving event identity. Malformed/unaccepted events are skipped, but every
accepted completion must be recovered. Missing payloads, digest disagreement
or I/O failure fail the cell. Replay is one-shot even after partial restoration;
a failed attempt cannot be retried as a fresh state.

No GC policy is disabled, forced or retuned. Replay/hash validation and full
result serialization have post-window CPU/RSS costs; the complete final object
graph still exists outside the timed load. Those costs must not be relabeled as
application CPU or hidden inside a business operation's latency. The diagnostic
wrapper forwards the option and labels replay `post-window-completion-replay`.

## Review and next execution gate

The independent codec-domain reviewer passed the final source review of
`2804fe4`, including default compatibility, exact live validation, bounded
canonicalization, ordinal/digest replay, late events, one-shot failure and
profiler forwarding. Reviewer and author performed no syntax/test/build/load
execution for this candidate before handing it to the integration owner.

The candidate adds nine deterministic tests using identical old/new event
sequences and timestamps, and one finite compact subprocess gate to the 19
existing A21 tests. They cover every outcome, late admission/completion,
timeout-before-poller order, malformed/duplicate events, exact raw bytes,
counter/failed-value/late-status corruption, missing/oversized raw records,
failed replay retry, Oracle type/hash equality and cache bounds. The existing
default tests remain intact.

In the integration owner's non-timing window:

```sh
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
cd "$PERF01_ROOT/.worktree/Perf-01-linux/NativeWeave"
taskset -c 8 "$PERF01_PYTHON" -m unittest discover -s tests/Benchmarks.Harness -v
taskset -c 8 "$PERF01_PYTHON" tests/Perf01.Database/test_affinity.py
```

Then repeat the existing `profile-a21-generator.md` diagnostic command with
the **same 171/s, 120-second workload and flags**, adding
`--compact-observation` and selecting a fresh output such as
`ROOT/perf01-evidence/profiling/before/db-generator-compact-001`. This is a
diagnostic comparison, not a product improvement or a replacement for fresh
formal calibration. Root owns all execution and records the actual receipts.

The shared A21 file hash changes even for callers whose behavior stays at the
default. Fresh final before/final-after driver manifests must bind the selected
bytes. Existing calibration/producer manifests remain immutable and retain
their original validity; they cannot be edited to bypass a source check.
Recalibrate DB before freezing the new cohort, and use the same mode, driver
bytes and evidence rules for before/after/direct/managed measurements.
