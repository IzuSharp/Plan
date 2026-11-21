# Perf-01 epoch-002: retired gRPC metadata regression

The two new deterministic regressions fail against unchanged native runtime code and pass with the minimal reaper repair. The complete repaired native Server suite passes **21/21**. See the [independent source and actual-execution review](../retirement-repair-review.md) and its [exact numerical proof](../retirement-repair-review.json).

This regression comparison uses test-only source `a607fc723807f777a51a8efff1838ebbf6efe228` on runtime `4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4`, then actual repaired source `7bc9ea574729ad5cb0184d95f675b2bb9da0089f`. It is **not** the main EA5/selected-final performance comparison. The published repair is `ccff42c0df4141984ef9de497af7cd768753704a`; its tree is exactly the tested tree. Three file contents/blob IDs and the public branch were read back. The actual test binaries retain their original tested source identity.

The repair retries the existing metadata clear only after retirement, body completion and zero live operations. Existing budget and escaped-owner predicates remain. The tests cover the constructed missed-cleanup state and a live input-cleanup guard; existing escaped trailer/header ownership tests also pass. They do not establish that this state caused the earlier ON 240/s network failure. Assembled B18/AOT/TLS, measured overhead, final selection and main long-load acceptance remain separate.

## Preserved records

- `before-observation.json` preserves exit 101 and both expected failures, with clean finite-owner retirement.
- `after-observation.json` preserves the complete 21-test success and clean finite-owner retirement.
- `source-publication.json` records actual source publication/readback and tree equivalence.
- `archive-readback.json` records a 6,055,091-byte archive containing both actual test binaries and both observations. SHA-256: `2c8b48d57e3658565c6404a47e7e31396b301c5d7972c6e3cadd2ecb99772950`. The saved archive was materialized again and its archive hash plus all four member hashes matched. It is available to the requesting user as `NativeWeave-Perf-01-epoch002-native-regression-binaries-001.tar.gz` in the conversation's delivered files and remains available until removed. No public full-raw/control archive is claimed.

The source, tests and curated observations are retained while repository Git history is retained. Compiler/test owner intervals include compilation and must not be interpreted as performance improvements. Main continuous 30-minute credit from this checkpoint: **0/10**.
