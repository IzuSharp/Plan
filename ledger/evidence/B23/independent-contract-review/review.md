# B23 controller/comparator contract review

Reviewer: `/root/b21_service`. The reviewer authored the standalone comparators and did not author the reviewed controller, HTTP adapter, profile or report.

Baseline reviewed commit: `e85bc13c78b6983860ca36b9688d3535395ac88e`. Corrected reviewed commit: `92f9e6b5672ea4cd813b769ed7aaff60044763d8`.

Comparator input: `be0bf7f00892f0f2f8ac041a55f79ab146ac8ac9`, manifest SHA-256 `e789eb77430c7284e98135ab083fbff78a3ecb79e8dce35e042f3706d58ba2d8`.

**Verdict: both concrete findings are closed.** No remaining comparator-contract blocker was found within the requested scope.

## Findings and closure

- **B23-CONTRACT-C1** — Actual TLS certificate/key and PostgreSQL server/client/lifecycle binaries were not included in the calibration fingerprint or per-cell immutable file checks. Same-path replacements could retain a matching calibration fingerprint. 92f9e6b adds both TLS files and postgres/psql/initdb/pg_ctl to external_input_sha256 and self.files before fingerprinting. Every target checks these files and A21 receives them as immutable artifacts. All six current hashes equal the recorded hashes in the successful targeted nine-cell cohort.
- **B23-CONTRACT-C2** — Attachment success did not assert returned responseVersion/contentHash/contentLength. Equality between stored and HTTP response bytes alone could accept the same wrong DTO persisted and returned. 92f9e6b requires v1 responseVersion, version2, exact deterministic contentHash and contentLength before recording the attachment mutation. Exact operation/item identity and independent SQL/blob checks remain. All nine actual targeted streaming cells pass.

## Actual correction evidence

The retained `functional-review-003` cohort completed all nine targeted cells: the three routes each ran SQLite HTTP/2 TLS, PostgreSQL HTTP/1 TLS and PostgreSQL HTTP/2 TLS streams. Each cell confirmed two requests after one warmup, six durable operations/outbox records, three items and attachments, one immutable content hash, exact HTTP version and HTTPS readiness. Managed routes emitted their actual NativeAOT witness. The independent review rechecked immutable artifact and external-input hashes, target/receipt identity, private configuration hashes and successful A21 observations.

This is functional evidence. The earlier66-cell cohort remains attributed to its original source and is not relabelled. No app, build, network or timed workload was run by this review.

## Contract and scope checks

- SQLite/PG provider selection, fresh isolated database/blob root, finite pool/admission/size settings and disabled worker policy match the selected comparator profile.
- Actual READY scheme, strict trusted TLS verification, observed HTTP/1.1 or HTTP/2, and managed NativeAOT witnesses are required.
- Executable/native/lock/source identity from the comparator manifest is retained and checked; accepted product artifacts are separate immutable inputs.
- Managed and Rust manifests declare the same 64KiB H2 stream/connection window,32KiB frame/header aggregate,32streams,200HTTP1headers; these are finite transport settings, not a global byte-credit equivalence claim.
- Missing comparator DI/diagnostics/overload/resource-owner variants are explicitly product_only and excluded from cross-route comparisons.
- Scope is foreground durable outbox publication with workers disabled; external consumer throughput is not claimed.
- The list cell selects the first100 rows from128 deterministic ordered fixtures; it does not measure an after-cursor seek operation.
- Runtime/pool/migration-ledger/query-route differences and cold OS-cache limitations remain disclosed. No universal backend or host substitution is introduced.

Statistical/calibration validity and complete B23/B22 acceptance are outside this review and remain assigned to their owners.

## Reviewed source SHA-256

| File | Corrected SHA-256 |
| --- | --- |
| `src/Benchmarks.Domain/run.py` | `8def96f86dce7119665140e72ddf59214ae621d8a0962775e55f697a3496fc07` |
| `src/Benchmarks.Domain/http_target.py` | `167149d43f8fdf1f94e3de2404bad2f445270b8e25032516b5d1b3e9d06bf494` |
| `src/Benchmarks.Domain/common.py` | `f4eebb84835ffba8f6826065197740e1234ee8f3c4f7c6a51af5b2debb9c3135` |
| `src/Benchmarks.Domain/profile-v1.json` | `760180de5a89760837e43a77676a6328fc792e0dfede1893558ae8c244332012` |
| `src/Benchmarks.Domain/README.md` | `ea37b3fab3a213df90ec5205601e65168effc8be2569145f08670936a17c4448` |
| `docs/guides/benchmarks-domain.md` | `56df8edb03fa900929cff50c3d1dd1a46f5e7b52e0ca15e6869adbfc93f7dbfc` |

Baseline hashes, exact per-cell receipts, observation hashes and external input hashes are in `baseline-review.json` and `review.json`. No credential or private-key content is included.
