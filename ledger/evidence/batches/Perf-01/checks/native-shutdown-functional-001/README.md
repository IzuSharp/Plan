# Perf-01 native shutdown correctness correction

The final Linux x64 source `ada13b865ec5d19876745498f6f51d8ad2367399` distinguishes successful acceptor completion
after a requested stop from a host fault. Unexpected completion and task failure
still fault the host. The selected completion and final drain use the same policy.
Independent source review covered both sites and the real Tokio outcome tests.

The four fresh affected gates completed between 2026-11-20T04:25:42.585799+00:00 and
2026-11-20T04:35:14.372133+00:00. All four outer commands returned 0.

| Gate | JIT assertions | Native AOT assertions | Additional observed evidence |
| --- | ---: | ---: | --- |
| B17 | 85 | 85 | 19 native tests passed, including four ordered outcome cases and 64 real network start/stop iterations. |
| B19 | 291 | 291 | 180 AOT managed retirement observations; fresh independent package gate passed. |
| B15 | 85 | 85 | Fresh independent package gate passed. |
| B18 | 662 | 663 | 71 API symbols, five negative compilation fixtures; fresh package JIT/AOT over HTTP/2 and TLS. |

B18 reuses the accepted native gRPC leaf evidence for 11 unchanged source files;
its actual product native asset and independent package are newly checked by the
fresh gate. The recorded release native identity is shared by B17, B15 and B18.
B19 records a separate debug native identity. These are harness-recorded binary
identities; this projection did not read or rehash native binaries or packages.

## Preserved failures and diagnostic limits

Both earlier B19 attempts remain failed: the outer verifier returned 1 and the
actual AOT child returned -6. The first attempt only records a native-completion
assertion failure; it contains no observed host state. The second records state
5, zero active requests, one retiring request, and zero native/managed bytes.
These different observations are retained separately.

The earlier 64-iteration network diagnostic passed on the old engine. It did
**not** reproduce the race. The ordered diagnostic extracted the original
unconditional selected-join fault policy and used real Tokio task results: it
returned 101 with observed state 5 versus expected 4. That is a deterministic
policy failure, not a claim that the complete network scheduling race was
reproduced. The final native suite passed the ordered four-case test and the
real network lifecycle tests.

B16 and A23 are reused only within their previously passed component scopes.
All 75 B16 and 82 A23 recorded source inputs were independently compared
with the final committed source and matched. Their tests were not rerun for this
Host-only change; neither component owns the changed HTTP/TLS Host supervisor.

## Evidence boundary

`public-summary.json` contains only fixed roles, enums, numbers, booleans, UTC
timestamps and hashes. Its inputs are the actual completed receipts and bounded
text logs; their bytes were hashed during this projection. Full receipts, command
arguments, host paths and raw logs remain local. `projection-execution.json`
records this separate offline projection, not a new test execution.

This checkpoint establishes scoped correctness evidence only. It grants no
performance improvement, formal comparison, long-run duration, other-platform,
pristine-machine or public-package release acceptance. Failed attempts were not
modified or replaced.
