# Perf-01 epoch-002: native close regression

**The two new native tests fail before the repair and pass with the selected
polling repair.** The selected source completed formatting, strict Clippy,
**23/23 Debug tests**, **23/23 Release tests**, and the Release native-library
build. All five selected commands exited 0 and retired. These are native
correctness results, not performance measurements or complete Perf-01 acceptance.

## Source and execution identities

| Role | Source commit | Parent | Git tree | Execution SHA-256 |
|---|---|---|---|---|
| Before repair, tests added | `f5acae7096d6ffa832c63e1a73f52fa39406a20d` | `ccff42c0df4141984ef9de497af7cd768753704a` | `9982e94d6b4697b4c62aa0610fe4616790bf90f9` | `8f6bb4b33ef39b3ec47b2877b3aab39f9b34e4d109b8af441a94f45d18fbc7ba` |
| Selected polling repair plus tests | `cad8acabfdb11dda9e365701cebceb8d12578f36` | `483c3b8c80c1d2bfbbf8d1130eaef48239b9c853` | `7f803d4f9e57fef1d8cfdef69c505d67f84614c9` | `edd5e70c606e57573dc2df34d52f16512c013321400d139dd8664b596b630c9f` |
| Earlier Notify variant, not selected | `d7131381b6b33da8bd8abaea305af7263c647ff0` | `f5acae7096d6ffa832c63e1a73f52fa39406a20d` | `4463245df94e89b4285f899f8673dabdd1ce4949` | `7ed15d92f94cac961f39c5b388e3aa3f6eb052bfe735b712eeb4211b74fb9a3c` |

The selected repair was introduced at `fa93f328f964ac04729f3c99cf060e14602e43c2`
and formatted at `483c3b8c80c1d2bfbbf8d1130eaef48239b9c853`. Commit `cad8acab...`
adds the deterministic test gate and test cases. Its exact tested tree was
published as [`2f40348c3db80a4fbee7a99e721b374a597b16df`](https://github.com/IzuSharp/NativeWeave/commit/2f40348c3db80a4fbee7a99e721b374a597b16df);
both changed files were fetched back from that exact commit and matched the
tested bytes. After network tasks join, the
repair continues polling the native runtime until admitted requests are retired
and their live operations finish. It does not wait for escaped payload budgets
or the Close operation itself.

The earlier Notify implementation also completed Debug and Release 23/23, but
those results belong to its own source identity. They are retained as an
exploratory result and are not substituted for the selected implementation's
separate execution.

## Failure reproduced before the repair

The two tests are:

- `actual_network_empty_body_finish_survives_close_after_network_join`
- `actual_network_fixed_body_finish_survives_close_after_network_join`

They use actual HTTP/1.1 sockets and validate the response with Content-Length
**0** or **4**. A `cfg(test)` gate holds the native worker immediately after its
network tasks join. The test submits Finish through the real ABI before
releasing that gate. The unrepaired runtime exits without delivering the
accepted operation's terminal callback.

Both tests recorded `observed_terminal=0`, expected `NW_OK + 1 = 1`, and
`worker_exited=true`. The filtered run reported **0 passed, 2 failed, 21 filtered
out**, exited **101**, and retired with no remaining owned processes or owner
children. The failed assertion is at `native/server/host/src/tests.rs:577`.

Before asserting, the failure path records the missing terminal, confirms that
the worker has exited, and performs **test-only cleanup** by completing that
otherwise stranded operation with cancellation. It then retires the operation,
request and host. This cleanup does not make the test pass and is not product
behavior. The final failure uses the original saved terminal observation.
Successful cleanup assertions precede the failure; this is source-order evidence,
not a separately printed owner-budget time series.

## Selected actual results

| Command | Actual UTC start | Actual UTC end | Result |
|---|---|---|---|
| Formatting | `2026-11-21T04:20:50.548115+00:00` | `2026-11-21T04:20:50.757505+00:00` | Exit 0, retired |
| Strict Clippy | `2026-11-21T04:20:50.837605+00:00` | `2026-11-21T04:20:55.021772+00:00` | Exit 0, retired |
| Debug native suite | `2026-11-21T04:20:55.144171+00:00` | `2026-11-21T04:21:23.985879+00:00` | 23 passed, 0 failed; exit 0, retired |
| Release native suite | `2026-11-21T04:21:24.134014+00:00` | `2026-11-21T04:23:50.672503+00:00` | 23 passed, 0 failed; exit 0, retired |
| Release native library | `2026-11-21T04:23:50.832291+00:00` | `2026-11-21T04:23:51.041579+00:00` | Exit 0, retired |

Both suites also reported zero documentation tests. Their printed test-harness
durations are not performance evidence. The selected Release library artifact
`libnativeweave_server.so` has SHA-256
`83b57ab59a43975c2396d069d782aeafe86c0ba2d0c94468fdf11800840f3388`.
This is a built-artifact identity, not a claim that an assembled C# application
or a domain package has loaded it.

## Preserved patch and reproduction

[native-close-test-only-f5acae7.patch](native-close-test-only-f5acae7.patch) is a
byte-for-byte copy of the preserved pre-repair test patch. Its SHA-256 is
`74a0eff457c378aa5c37f7a806d95462bee5b9c8610f56dcb8367c934d4255b6`.
It changes only `native/server/host/src/engine.rs` and
`native/server/host/src/tests.rs`. Applying its hunks in memory to the exact ccff
parent reconstructs the two files at f5acae7 byte-for-byte. The source adds only
test-gated synchronization and the regression cases; production host shutdown
is unchanged in that before-repair test commit.

Use the repository-pinned toolchain and existing finite owner. The preserved
command recipes, timeouts, source hashes and all receipt/stdout/stderr hashes
are in [checklist.json](checklist.json). From the corresponding exact source
checkout, the key commands are:

```sh
# Before repair: expected failure of the two new cases.
cargo test --locked --offline -p nativeweave-server finish_survives_close_after_network_join -- --test-threads=1 --nocapture
# Selected repair: complete native suites.
cargo test --locked --offline -p nativeweave-server -- --test-threads=1
cargo test --locked --offline --release -p nativeweave-server -- --test-threads=1
```

These results establish the native regression and its correction for the tested
ordering. They do not alone establish the cause of the original sporadic
16-request B20 failure or replace final assembled application/package checks.
The preceding controlled C# observations remain in
[server-close-tail-diagnostic-001](../server-close-tail-diagnostic-001/README.md).
No workload was run to prepare this record; no performance or 30-minute
acceptance credit is added. Raw logs and operational maps remain in their named
preserved bundles; this public record contains project-relative locations and
hashes only.
