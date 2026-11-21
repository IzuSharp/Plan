# Retained-owner diagnostic and regression source review

**Verdict: ACCEPT for the exact formatted source below.** This is a source review,
not a test result, causal reproduction, repair acceptance or performance claim.
Reviewed at `2026-11-21T01:34:41.425697+00:00`. No builds, tests, services, target imports or timing loads
were executed by this reviewer.

## Diagnostic-only source

Commit `04dd3380da9f2f9203fc0baa223c4fd96b524754` is based on ON `2e3995df8d86583ee9443348276ca8d918056bfc`.

| Source | SHA-256 |
| --- | --- |
| `native/protocols/grpc/src/call.rs` | `c9c918190661536f137f1b37c7d69d444bd239e2e22737ccb42632e6f5500586` |
| `native/server/host/src/engine.rs` | `c7ee8325ad5d8354f4d5792217ba69edad028a2301137c9719ba0722cb77d008` |

The counter increments only after receiver, initial metadata, terminal metadata
and frame credit have all been cleared. Release/Acquire observations distinguish
completed clear passes. Busy locks are explicitly unavailable, never empty. Credit
sharing and the combined metadata-release predicate have separate labels. Rows
are collected before releasing the request-registry guard; stderr I/O occurs after
that guard and all Call guards have been dropped.

No admission, cancellation or cleanup predicate changes. The snapshot exposes
ownership scalars and synthetic route identifiers, not header/payload values.
It remains non-atomic: equal counter samples do not exclude an in-progress clear
or publication, and a zero count does not prove the helper was never entered.
Only host state 2 attempts a snapshot, and a busy registry may omit per-request
rows. The intended diagnostic caller stops after idle. The extra counter means
this is an instrumented binary with **zero formal performance credit**.

## Deterministic regression premises

Test-only commit `a607fc723807f777a51a8efff1838ebbf6efe228` is based on OFF `4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4`.
Its sole changed file is `native/protocols/grpc/host_tests.rs`, SHA-256
`a2bfbeb9ff341d10d520473a9b45122cd012570be3364ac33f286c8008c0747b`. Product runtime code is unchanged in that commit.

Both tests create actual initial and terminal metadata, use the real dispatch and
retirement entry points, and explicitly construct the postcondition of a missed
completion notification. They save whether metadata cleared and the registry
entry disappeared **before** explicit fixture teardown. Teardown releases the
raw/Arc owners and checks zero quota and zero retiring count; it cannot turn a
captured failed postcondition into a passing assertion.

The second test first passes retirement while the body is incomplete, then holds
a real `InputDiscard` guard and its live-operation count. It verifies that reaping
preserves metadata while the guard is live. Guard drop uses the actual existing
reap path, after which the test captures the cleanup postcondition. This makes
the live-operation guard meaningful rather than testing only an unretired request.

The unchanged implementation is expected from source to retain metadata in the
constructed completed state. That expectation is not an observed execution.
These tests do not reproduce the scheduling event or identify the request behind
the historical 92,096-byte observation. Actual owner receipts, test outcomes and
any later repair remain separate evidence. Existing escaped-header ownership
regressions continue to protect the final sharing/budget conditions.
