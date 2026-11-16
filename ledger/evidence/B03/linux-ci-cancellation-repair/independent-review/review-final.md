# Independent review: B03 cancellation CI repair

**Accepted** at `c9d5400f8371d3501696caf126c6b4496ea7e5d2`, with no open findings. This is a focused Linux x64 test-oracle and guide correction. Product native and managed source, public API, dependency manifests and the cancellation implementation remain unchanged.

## Original failure

NativeWeave PR13 head `b6728f7bcde1a79f90797a517efb2f54fc5190dc`, tested through merge `846c0d321d0a49503f2e70de8ac15eb95a395b3e`, failed normal CI run `43837773614`, build job `133198594379`. The B03 composition test returned `cancel result missing`. The exact job log and source identities are preserved in the parent directory.

The earlier test treated actor admission as proof that SQLite execution had started and required a SQLx error item. The bounded producer can instead observe stop before its next fetch, close the row channel, and report `stopped=true` through its separately joined retirement receipt. That legal branch explains the timing-dependent failure.

## Why the repair is accepted

The new fixture creates two controlled cases. First, one retained row occupies the adapter's sole row slot without a consumer. Cancellation then requires actual retirement, progress-handler removal and a usable connection, followed by exactly the retained row and EOF. No SQLx error is invented for that path.

Second, the test registers a comparison callback on the actual physical SQLite connection through SQLx's public API. The first comparison signals native worker entry and waits for an explicit test-only release. The test requests cancellation only after that native observation. It then releases the callback and requires exact `Interrupted`. The callback has a bounded receive and records successful explicit release, so timeout or channel disconnect cannot be counted as a successful interruption. It returns stable comparison semantics and has no panic-through-FFI path.

Both cases keep the independent retirement/progress-removal and same-connection marker checks. The old canceled generation is followed by a fresh finite 1..5000 recursive aggregate with exact result 12,502,500, which exceeds the 1000-instruction progress interval. Old-token reuse and pre-canceled rejection remain. Final active/queued command, retained input-byte and active-operation counters must be zero.

## Actual evidence reviewed

The author's immutable `formal-001/result.json` passed 11 commands on the clean repair commit. The selected Release test exercised 12 native scenario groups. The rebuilt native fixture was then executed by JIT and the unchanged, previously published Native AOT executable: each ran all 14 native groups and 36 managed assertions, including all three new cancellation markers. The existing final-parent retirement barrier and the two-row handoff bound also passed.

I independently recomputed 102 source hashes, 22 log hashes and 4 artifact hashes; all matched. The product native asset and reused AOT executable match their prior accepted hashes. The AOT executable was actually reexecuted with the rebuilt fixture; it was not republished or represented as newly compiled.

I found one metadata-only receipt issue: the runner retained a reference to the JIT environment dictionary and later changed it for AOT, mislabeling the recorded JIT data root. The executed environments were independent copies. The author preserved the original receipt and runner and added `receipt-erratum.json` with the exact actual roots and original hashes. I read and accepted that explicit correction; no test rerun was needed.

This review does not claim a later normal CI or merge outcome. Those remain with the batch coordinator. The reviewer did not modify product/Plan files or rerun tests.
