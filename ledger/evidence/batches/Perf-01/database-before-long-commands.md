# Exact before database long commands

Status: **source preparation only**. No long-load or verification command in
this document has been executed. The companion
[JSON command arrays](database-before-long-commands.json) contain exactly two
existing `run.py` invocations and two existing `verify_long.py` invocations.
There is no new controller. Root records actual execution and must finish the
global freeze before starting these cells.

## Fixed before loads

The final v5 before selections froze SQLite at 40 logical operations/s and
PostgreSQL at 144/s for the paired long groups: 80% of their confirmed 50/s and
180/s short anchors. Both run the mixed durable-cycle/typed-page workload at
C16, seed 20261119, with 16 warmup operations, 32 same-process recovery cycles
and 60 seconds idle. Both use `--stage soak --seconds 1802`, explicit compact
observation, continued classified overload, zero unexpected errors, a 500 ms
arrival-p99 limit and a 256 MiB sampled application-RSS limit.

The immutable driver's unchanged formula is:

```text
period_ns = round(1e9 / rate)
requests = ceil((1802 + 0.25) * 1e9 / period_ns) + 1
```

The existing 250 ms soak guard remains in addition to the prospectively chosen
1802 seconds. It is not removed or counted as successful acceptance in advance.

| Group | Rate (/s) | Period (ns) | Planned measurement operations | Cycle / page operations | Planned first-to-last scheduled span | Complete target outcomes including warmup |
|---|---:|---:|---:|---|---:|---:|
| SQLite | 40 | 25000000 | 72091 | 36046 / 36045 | 1802.250000000 s | 72107 |
| PostgreSQL | 144 | 6944444 | 259526 | 129763 / 129763 | 1802.256829100 s | 259542 |

These counts are source arithmetic, not observations. The 32 recovery cycles
have their own receipt and are excluded from the measurement count, outcome
journal above and effective duration. Warmup and idle likewise earn no duration
credit. A cycle contains durable create, replay and recovery lookup; a page is
one typed 100-row response. Latencies describe the whole real HTTP/1 application
path, not isolated database execution.

## Exact inputs and orchestration

Source `/workspace/scratch/01c249676f47/perf01-toolchain/env.sh` before executing
the arrays. They invoke the pinned Python 3.12.14 interpreter explicitly.

| Input | Identity |
|---|---|
| Immutable timing checkout | `ROOT/.worktree/Perf-01-frozen-drivers-linux/NativeWeave`, clean `ce2a3c75cbd535490897d062b6cbb7c095408307` |
| Unchanged A21 | `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53` |
| Timing reader | `8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4` |
| Before source | clean `ea5fa528035d025bd7a28698ee7c71194432236c` |
| B24 package application | `ROOT/perf01-build/before/reference-002`, progress SHA `36991e0498764aff50c62e259f3a8fb5a403e8d07b4bb7d89a128b643476b327` |
| Identical exception observer | `ROOT/perf01-build/before/db-observer/manifest.json`, SHA `0aeb5121fa7cc4f9ff4b86b4c24bdc4ce80991f83d1a07b45a849b68de271f62` |
| Prospective policy 4 | `0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc` |
| Separate final verifier | main `tests/Perf01/verify_long.py`, SHA `3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82` |

The JSON pins every timing helper, source configuration, supplied producer
metadata and both completed selection/controller pairs. It carries the existing
package closure and executable/native hashes from the producer records. During
this preparation, only source files and small metadata were hashed; binaries,
packages and raw operation ledgers were not rescanned. The existing driver
checks actual artifacts and loaded executable/native identities before timing.
The after builds must supply their own producer and loaded-artifact identities.

Each DB measurement array begins with:

```text
/usr/bin/flock --nonblock ROOT/perf01-evidence/timing.lock taskset -c 2,3 ...
```

`ROOT` is expanded to the exact absolute workspace path in the JSON. The
existing `/usr/bin/flock` was observed as a regular executable and the exact
shared lock file exists; no lock was acquired by this source review. This is
an orchestration guard outside the application. A busy lock prevents the
measurement from starting; it is not an application failure. Use the same guard
for paired after DB cells. The protocol driver already holds this same lock
internally, so it must not receive a second outer lock.

The application and local PostgreSQL service inherit CPUs 2,3 before the
controller switches generator roles to CPUs 0,1. The existing affinity helper
verifies these identities and masks. PostgreSQL explicitly uses
`ROOT/perf01-toolchain/postgres18/bin`; its fresh cluster and full durability
remain supplied by the existing driver. SQLite retains its separately frozen
WAL/FULL initial state. No connection, pool, schema or durability settings are
changed by these command arrays.

## Outputs and post-run proof

| Group | New measurement directory | New verification receipt |
|---|---|---|
| SQLite | `ROOT/perf01-evidence/long/before/sqlite-001` | `ROOT/perf01-evidence/long/before/sqlite-001-verification.json` |
| PostgreSQL | `ROOT/perf01-evidence/long/before/postgresql-001` | `ROOT/perf01-evidence/long/before/postgresql-001-verification.json` |

The JSON lists each measurement followed by its separate CPU 8 verification.
Run one measurement at a time and run the verifier with no active measurement.
Record actual argv, start/end, exit code and full evidence. On failure or
interruption, preserve the partial directory and verify cleanup of known owned
processes before another load. Do not overwrite an existing cell or verifier
receipt.

A driver exit of zero is necessary but insufficient: require the service
standard, independent durable SQL checks, exact complete operation counts,
valid generation, successful low-rate recovery and owner/drain receipts. The
final verifier must return `accepted: true` and establish a conservative
ordinary-success span **D−C≥1800 seconds**, plus the original dispatch-span
check, resource limits and all correctness gates. C is the first successful
ordinary completion observed by the controller; D is the last successful
ordinary dispatch-start. D−A remains diagnostic only. No constant CPU-busy
interval is asserted, and the scheduled guard never guarantees acceptance.

Both group records currently have zero long-duration credit. The after paths
are explicitly future placeholders outside the runnable command arrays. Root
will bind actual after package/observer metadata in the global freeze while
keeping the same driver, load, counts, limits and CPU layout.

## Independent source review

The codec reviewer checked the exact four argv arrays, ce2 CLI and soak-count
formula, all 19 source/small-metadata hashes and four final-selection/controller
hashes, the shared lock and the separate timing/post-run reader identities.
The bounded review passed. It did not execute a long command, verifier, test,
build or workload and did not rescan binaries or raw operation ledgers. The JSON
records the reviewed snapshot SHA; later changes only clarify prose spacing and
record the review.
