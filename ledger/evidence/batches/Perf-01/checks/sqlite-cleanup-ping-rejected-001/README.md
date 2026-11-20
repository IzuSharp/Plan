# Perf-01 SQLite cleanup Ping ablation — rejected

**Decision: do not retain or advance this candidate.** All correctness and
retirement checks passed, but both frozen A21 mean comparisons were
`inconclusive`. CPU per completed unit increased in both probes, and scalar
mean process p99 increased. The prespecified advance screen therefore failed.
The isolated runtime change was not integrated. No repeat or full-business
follow-up was run to seek a different classification.

This diagnostic compares current product **A = `0715ffb6`** against the isolated
candidate **B = `58132a4`**. It does not replace Perf-01's original main baseline
or the separate full application before/after matrix. It provides **zero formal
comparison credit and zero long-duration credit**.

## What was tested

The SQLite query cleanup path removes its progress handler, awaits SQLx
`clear_cached_statements()`, then checks connection state. In locked SQLx 0.9.0,
ClearCache acknowledges after clearing statements and updating the cache
count; Ping only acknowledges. The candidate removes one post-ClearCache Ping
and retains the exclusive handle barrier plus transaction-depth/autocommit
check. Control and recovery paths retain their complete Ping-based probe.
Cache clearing, cancellation recovery, quarantine and ownership retirement
remain unchanged.

This was a source-supported opportunity to remove one worker round trip, not
proof that the round trip caused a measured application bottleneck. The actual
SQLx source inspected was
[`worker.rs`](https://github.com/launchbadge/sqlx/blob/75bc0487eb661da811bb7a3c5d158f1bd463fef4/sqlx-sqlite/src/connection/worker.rs)
at `75bc0487eb661da811bb7a3c5d158f1bd463fef4`. No upstream code or dependency
change was introduced.

The accompanying regression deliberately executes an untracked `BEGIN
DEFERRED` in a fresh database. It requires engine/tracked transaction-state
mismatch to quarantine the connection, reject subsequent work, retire native
operations, release the physical lease and leave the checked budgets empty.
The complete native B03 suite also retains its cancellation, stale-generation,
bounded-row, savepoint, BUSY and pool/worker retirement scenarios.

## Results and prospective decision

Each comparison uses three independent A processes and three independent B
processes. Aggregate tails below are **means of process p99s**, not pooled tails.
Percentages are descriptive `100 × (B / A − 1)`. The original summary and noise
bytes are preserved in [summary.json](summary.json) and [noise.json](noise.json).

| Probe | A mean ms | B mean ms | Mean Δ % | A p99 ms | B p99 ms | p99 Δ % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Scalar | 3.093788 | 4.820880 | +55.8245 | 25.214567 | 28.461467 | +12.8771 |
| Ordered 100-row page | 7.221050 | 8.318016 | +15.1912 | 28.955773 | 27.772494 | −4.0865 |

| Probe | A CPU ms/unit | B CPU ms/unit | CPU Δ % | A managed bytes/unit | B managed bytes/unit | Allocation Δ % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Scalar | 0.558212 | 0.627416 | +12.3974 | 17,354.768 | 17,354.491 | −0.001598 |
| Ordered 100-row page | 1.879391 | 2.078029 | +10.5693 | 63,863.517 | 63,857.843 | −0.008886 |

CPU and managed allocation are process counter deltas around each measured
loop, divided by completed units. Scalar counters include its existing
retirement observer; page counters include the public query, DTO/list
materialization, cleanup and exact row verification. RSS was not collected by
these unchanged probes. Native allocation/copy totals and pending-retirement
counts were not directly measured. Per-process GC collection deltas are
retained in [evidence.json](evidence.json).

| Probe | Frozen noise band ms | B−A mean effect ms | Original bootstrap 95% interval ms | A21 decision |
| --- | ---: | ---: | --- | --- |
| Scalar | 0.996333 | +1.727093 | [0.154809, 3.299376] | inconclusive |
| Ordered 100-row page | 2.233680 | +1.096966 | [−0.001908, 2.299658] | inconclusive |

The unchanged A21 function uses 2,000 independent-process bootstrap resamples,
seed `20261120`. Each diagnostic noise band was frozen before any B process as
`max(1,000 ns, max(A noise process means) − min(A noise process means))`, with
relative noise zero. The initial noise processes are not comparison replicates.
No band was recalibrated from the comparison.

The frozen screen requires all correctness/release checks, at least one mean
classified as improvement, neither mean classified as regression, and no
increase in either probe's mean process p99 or CPU per completed unit. It only
permits full-business testing; it does not itself retain a change. This run
failed that screen. The descriptive increases above are **not relabelled as
statistically proven regressions**. The page tail decrease and tiny allocation
differences do not override the frozen rule.

There is no directly comparable Rust scalar/page probe for these exact paths,
so no Rust gap is computed here. The previously measured whole-business Rust
comparison remains a different workload. This serial diagnostic is not a
capacity test or the required persistent concurrent business-cycle acceptance.

## Exact versions and loaded identities

| Identity | A — current product | B — rejected candidate |
| --- | --- | --- |
| Source commit | `0715ffb6376b1ae08259ad7e2cb30ff0320d83e7` | `58132a44f1d2a9d338fe75f54f1504ee6d93f588` |
| Source tree | `cd0a6022e0115c22f133aedf6c801d9244640523` | `089b2abc559ceb35b0e40c7dfeb9808cde7aa17b` |
| Measured package version | `0.1.0-perf01.after.3` | `0.1.0-perf01.sqlite-ablation.1` |
| Actually loaded SQLite SHA-256 | `7254f8e490f19637701d92523c2ba08e0cbdfdbe4c5f28173d4215b5f303da8d` | `ea4b8727ea1dff30725eb0d09b39e0fa4ca9736d411fb5361d00ddf7ddf12169` |
| Scalar AOT executable SHA-256 | `e2008eca2b3474f0d45b3914ceb0977bd1bdaa014a2f8380c8e14564bcdc77e1` | `d737372eefaa1725446de9357577507b82483afc0bef9841b545192e4a4909eb` |
| Page AOT executable SHA-256 | `29f647e7247e193ce1bac64018ec496d2ab8a8ace4ec0bcce94eb5c9c38cbe71` | `a25881949024355f3e0d2f58a3ef38e842ba644bf5cedd376574b9c11a4a9c32` |
| SQLite facade package SHA-256 | `20a65cebd726399992f79a2d327882af1bc81e888c9bd7d98c9194f4455b4ca6` | `a202e7374c49576e485d5c28c0b19a157777461a0af34f4a32a54f20219a3251` |
| SQLite native package SHA-256 | `9e74c4de46df6cf21a31f4a91d93777cebf172ca98bfb4978e70ea0bdf6497cc` | `ed44e68956ac57f0ae3142705653c11ef76790655550f6be90e524d9cdc6ac85` |

Every process observed only `libnw_database_sqlite.so` among NativeWeave native
modules, with its correct A/B hash. Full produced native identities, AOT
artifacts, sidecars, twelve actually resolved NativeWeave packages per consumer,
and the separately labelled seventeen-package feed inventory are in
`evidence.json`. Feed membership is not presented as proof of use. PostgreSQL
and server artifacts were produced by the unchanged package recipe but receive
no measurement credit from this SQLite experiment.

Both roles use the locked Linux x64 Release native recipe, Rust/Cargo 1.100.0,
.NET 11.0.100, GCC 14.2.0 and GNU Binutils 2.44. Tool binary hashes and the
unchanged Cargo.lock hash are retained. Native Rust flags remain empty; native
builds use three Cargo jobs and separate target directories. Package consumers
are Native AOT with `IlcInstructionSet=x86-64-v2`. Both probe sources and their
builder sources match exactly. The compiled facade embeds its native hash, so
B was rebuilt through the supported native/package/AOT producers.

## Completed build and process record

The candidate build ran **2026-11-20 10:21:45.096480–10:29:52.606222 UTC**.
All seven commands completed with exit 0 and retired process groups. The native
test step spent about 1 minute 54 seconds compiling; its three tests containing
all fourteen B03 scenarios completed in 0.35 seconds. The new quarantine marker
occurred exactly once. No legacy managed B03 profile wrapper is claimed as a
current-source pass.

| Build step | Start UTC | End UTC | Elapsed seconds | Exit |
| --- | --- | --- | ---: | ---: |
| fmt | 10:21:45.112298 | 10:21:45.579038 | 0.465961 | 0 |
| clippy | 10:21:45.594054 | 10:22:14.801361 | 29.206322 | 0 |
| native-tests | 10:22:14.822484 | 10:24:09.630132 | 114.806968 | 0 |
| native-stable | 10:24:09.650460 | 10:27:18.383481 | 188.732362 | 0 |
| packages | 10:27:18.398309 | 10:29:13.779037 | 115.380132 | 0 |
| shared-retirement | 10:29:13.815587 | 10:29:35.953947 | 22.137415 | 0 |
| shared-page | 10:29:35.969730 | 10:29:52.578202 | 16.607378 | 0 |

The complete diagnostic stage ran **2026-11-20
10:30:32.735593–10:32:24.858082 UTC**. The controller used CPU 8; each fresh
process used CPUs 2–3 under the exclusive timing lock. Each process used a new
SQLite file, twenty warmup units and 1,000 measured units, with one outstanding
public call. The scalar probe checks `SELECT CAST(1 AS BIGINT)` and 4,000 native
retirement observations per process. The page probe verifies ordered 100-row
DTOs with unchanged WAL/FULL settings, one-connection pool, 128-row batch cap
and 65,536-byte bound. Its seed read is a new logical session in the same
process, not an independent external persistence oracle.

The order was six A noise processes (three scalar, three page), then scalar
`A B B A A B`, then page `A B B A A B`. All eighteen completed with exit 0,
correct values, passed available release checks, and retired process groups.
There were zero unexpected process errors, process timeouts, controller
signals, correctness failures or failed retirement checks. No dedicated
cancellation load was run by these probes; cancellation regressions belong to
the separately completed native B03 gate.

| Sequence / process | Mean ms | p99 ms | CPU ms/unit | Managed bytes/unit | Exit / release |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 / `scalar-noise-a-0` | 5.822398 | 30.383100 | 0.648747 | 17353.552 | 0 / passed |
| 2 / `scalar-noise-a-1` | 4.826065 | 30.667800 | 0.539256 | 17358.736 | 0 / passed |
| 3 / `scalar-noise-a-2` | 5.091596 | 31.003000 | 0.611418 | 17359.552 | 0 / passed |
| 4 / `page-noise-a-0` | 7.371374 | 28.768205 | 1.984238 | 63860.592 | 0 / passed |
| 5 / `page-noise-a-1` | 5.137695 | 23.076287 | 1.831274 | 63862.416 | 0 / passed |
| 6 / `page-noise-a-2` | 7.188856 | 28.709314 | 1.974219 | 63862.416 | 0 / passed |
| 7 / `scalar-compare-0-a` | 1.832757 | 20.539700 | 0.409470 | 17348.424 | 0 / passed |
| 8 / `scalar-compare-1-b` | 3.896875 | 26.216500 | 0.600079 | 17356.984 | 0 / passed |
| 9 / `scalar-compare-2-b` | 4.239110 | 28.484800 | 0.610561 | 17352.256 | 0 / passed |
| 10 / `scalar-compare-3-a` | 3.328778 | 30.860700 | 0.600716 | 17360.352 | 0 / passed |
| 11 / `scalar-compare-4-a` | 4.119828 | 24.243300 | 0.664450 | 17355.528 | 0 / passed |
| 12 / `scalar-compare-5-b` | 6.326655 | 30.683100 | 0.671607 | 17354.232 | 0 / passed |
| 13 / `page-compare-0-a` | 7.374734 | 29.323612 | 1.951966 | 63861.312 | 0 / passed |
| 14 / `page-compare-1-b` | 8.817354 | 30.879490 | 2.159097 | 63857.088 | 0 / passed |
| 15 / `page-compare-2-b` | 7.772433 | 28.726362 | 2.076916 | 63856.504 | 0 / passed |
| 16 / `page-compare-3-a` | 6.018358 | 26.704122 | 1.811349 | 63865.008 | 0 / passed |
| 17 / `page-compare-4-a` | 8.270059 | 30.839586 | 1.874857 | 63864.232 | 0 / passed |
| 18 / `page-compare-5-b` | 8.364261 | 23.711629 | 1.998074 | 63859.936 | 0 / passed |

Totals include **9,000 measured scalar calls**, **36,000 checked scalar native
retirement observations**, **9,000 measured pages / 900,000 verified rows**, and
360 warmup units. This includes noise and comparison processes. It is not
thirty minutes of continuous load and contributes no long-test acceptance.

## Reproducing the isolated source and method

[candidate.patch](candidate.patch) is the complete two-file difference from A
to B: 47 insertions and 2 deletions, including the new regression. Its SHA-256
is `ec29044217414e595f4387b5ee32e3db6c25a9fb1a718c701bb8d30845d5e48f`.
The patch was reverse-checked against the clean measured candidate; all changed
file SHA-256 values and both complete Git trees are in `evidence.json`.

Start a separate checkout at A, apply the patch, stage its two files and use
`git write-tree` to verify `089b2abc559ceb35b0e40c7dfeb9808cde7aa17b`. Commit the
source before using builders that require a clean checkout. A newly created
commit can have different Git metadata while reproducing that exact source
tree; the recorded measured commit remains B above.

Use the repository's locked toolchain and the recorded resource/flag settings.
For B, with `PERF01_B_BUILD` set to a new absolute output directory, the actual
build recipe was:

```sh
taskset -c 2,3 cargo fmt -p nativeweave-data-sqlite -- --check
taskset -c 2,3 cargo clippy -p nativeweave-data-sqlite --all-targets --locked -- -D warnings
taskset -c 2,3 cargo test -p nativeweave-data-sqlite --release --locked -- --nocapture
taskset -c 2,3 python3 eng/task07_native.py --output "$PERF01_B_BUILD/native-stable"
taskset -c 2,3 python3 src/Packaging.Domain/prepare.py \
  --output "$PERF01_B_BUILD/packages" \
  --previous-version 0.1.0-perf01.sqlite-ablation.1 \
  --candidate-version 0.1.0-perf01.sqlite-ablation.2 \
  --native-manifest "$PERF01_B_BUILD/native-stable/manifest.json"
taskset -c 2,3 python3 tests/Perf01.Shared/prepare.py \
  --feed "$PERF01_B_BUILD/packages/previous/feed" \
  --version 0.1.0-perf01.sqlite-ablation.1 --output "$PERF01_B_BUILD/shared-retirement"
taskset -c 2,3 python3 tests/Perf01.Shared/prepare.py --probe page \
  --feed "$PERF01_B_BUILD/packages/previous/feed" \
  --version 0.1.0-perf01.sqlite-ablation.1 --output "$PERF01_B_BUILD/shared-page"
```

The `.2` package closure is the B24 producer's upgrade exercise and was not the
measured feed. A reuses the actual `0715` consumers at version
`0.1.0-perf01.after.3`; rebuild A from its exact tree with the same producers
when reproducing elsewhere. The public JSON records all measured package,
consumer-source, binary and loaded-native identities.

For each process, select its A/B build directory and the corresponding
executable below. Pass a unique absolute new database path and result path:

```sh
taskset -c 2,3 "$PERF01_ROLE_BUILD/shared-retirement/aot/NativeWeave.Data.NativeHost.Tests" \
  sqlite "$PERF01_RESULTS/UNIQUE.db" 1000 "$PERF01_RESULTS/UNIQUE.json"
taskset -c 2,3 "$PERF01_ROLE_BUILD/shared-page/aot/NativeWeave.Perf01.PageProbe" \
  sqlite "$PERF01_RESULTS/UNIQUE.db" 1000 "$PERF01_RESULTS/UNIQUE.json"
```

Follow the exact eighteen-process order above, freeze the two noise bands
before the first B process, and use the unchanged A21 source hash recorded in
`evidence.json`. Preserve every attempt and apply the same advance rule. These
commands document reproducibility; this completed experiment remains rejected.

## Evidence delivery and separate preparation history

This directory contains the readable report, exact original summary/noise,
curated per-process correctness/resource/identity evidence, complete numeric
latency samples and the small source patch. `manifest.json` records every
stored SHA-256 and the decoded numeric sample SHA-256. Decode samples with:

```sh
gzip -dc timing-samples.json.gz > timing-samples.json
sha256sum timing-samples.json
```

The decoded sample hash is
`5aefc0839cfd97c52c9cbfaa0ce3f5c8f7fdd26b510d1554df5c73e814ada1c3`.
The numbers preserve the original units and values: scalar milliseconds and
page stopwatch ticks with their frequency. These are synthetic numerical
records, not the private operational bundle, package archives or databases.
Original receipt hashes and workspace evidence locations are in `evidence.json`.
The curated files are retained in Plan Git for as long as repository history
is retained; private workspace paths are not claimed as public downloads.

Preparation history remains distinct from these eighteen successful process
runs. The initial source formatter check requested one assertion line wrap,
which was fixed before candidate B. Command-owner review found an interruption
gap before any workload; the corrected owner passed two source-bound finite
Python checks. The separately prepared gRPC adopted-child guard initially
failed because this runtime lacked `/proc/.../children`; that failure is
preserved under its own source/receipt and was followed by a separately
authorized ownership fix. None is discarded, relabelled as a SQLite workload
sample, or included in this experiment's performance counts. All receive zero
formal and long-duration credit.
