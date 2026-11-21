# Perf-01 epoch-002: independent retirement repair review

**Verdict: ACCEPT for the scoped native repair and recorded native functional executions.** This review grants no performance, application or long-duration acceptance.

The actual tested repair is `7bc9ea574729ad5cb0184d95f675b2bb9da0089f`. Its Git tree is `aa7b4d25886e64e71dbf57c75f9592af7b46d37a`, independently identical in local Git objects to publication commit `ccff42c0df4141984ef9de497af7cd768753704a`. Test binaries retain their actual local source identity. Remote publication/readback is a separate integration-owner observation.

## Source and ownership

The repair retries the existing idempotent metadata cleanup inside the retirement predicate, after the request is retired, its body has ended and live operations have reached zero. The original final budget and escaped-metadata ownership predicates still govern removal. Dropping internal metadata references does not release credits held by escaped headers, frames or native buffers. No change to the public API, admission, cancellation, callback gate, status or resource limits was identified. Repeated retirement attempts can add locking cost; its performance is not established here.

## Actual execution

| Observation | Unchanged runtime plus tests | Repair |
|---|---|---|
| Actual source | `a607fc723807f777a51a8efff1838ebbf6efe228` on runtime `4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4` | `7bc9ea574729ad5cb0184d95f675b2bb9da0089f` |
| UTC start | 2026-11-21 01:28:45.347256 | 2026-11-21 01:33:34.473760 |
| UTC end | 2026-11-21 01:31:08.431874 | 2026-11-21 01:35:30.904860 |
| Test scope | Two new filtered tests | Complete native Server suite |
| Result | 0 passed, 2 failed, 19 filtered; exit 101 | 21 passed, 0 failed, 0 filtered; exit 0 |
| Finite owner | Failed producer; successfully retired | Completed and retired |
| Remaining owned processes / children | None | None |

Both runs used Release, locked Cargo dependencies, one test thread and CPUs 2–3. Input recipes, actual owner receipts, logs and preserved test binaries were independently inspected and hashed. The paired JSON records the exact hashes. The native toolchain checkpoint was sufficient for these Rust tests; its then incomplete full environment is not relabeled as accepted.

The original runtime failed with `reaper retained initial metadata` and `last input cleanup retained initial metadata`. Each test captured the observation before explicit teardown and asserted it only after teardown had proved zero retained requests and budget. The second test preserved metadata while input cleanup remained live. Its initial-metadata assertion failed afterward. Later assertions were not reached in the original run and receive no separate actual credit.

The repaired complete suite includes the two new regressions, escaped header/frame ownership, cancellation, deadline and terminal-status handling, input cleanup, MCP admission, callbacks and host fault/shutdown tests. Two stderr messages reading `deliberate acceptor panic` are expected within the passing acceptor fault-semantics test. The repaired test phase took 0.39 seconds; owner spans include compilation and are not performance comparisons.

## Limits

These tests construct a missed-cleanup state deterministically. They establish that the reaper can repair that state while preserving the live-operation and escaped-owner gates. They do not establish the cause of the earlier ON network failure. Managed B18, Native AOT, TLS application behavior, measured cost and final selection remain separate obligations. Main 30-minute segments credited by this review: **0**.
