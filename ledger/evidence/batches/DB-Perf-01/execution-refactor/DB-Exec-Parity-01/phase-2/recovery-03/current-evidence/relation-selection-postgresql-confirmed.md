# PostgreSQL second-layer confirmation · recovery 03

Supplement to `selection-for-root.md` SHA-256 `23809697f700aafcca145a76a514072d6297d79e278931e16d516c939bcda7d9`. No product candidate changed at this point.

The second-layer PostgreSQL run has completed with the same source `4376c54`, same original native bytes, true Release Native AOT, 32 warmups and 128 measured operations. All controls/scopes, 128 successes, zero business/oracle errors, exactly 53 rows/digest, 1 SQL, 4 protocol submissions and final owners zero passed.

Measured per-business Clone31 = 120,776 B; CloneCopy31 = 54,932 copied bytes; Combine31 = 181,760 B; metadata31 = 11,160 B; append31 = 17,152 B. Tape growth98 copies 63,488 prior capacity bytes and allocates 126,976 new capacity bytes; other tape copies542 move 51,008 payload bytes. Each value is identical to SQLite across all 128 measured operations. PostgreSQL whole-process allocation mean is 685,904 B/business. All receipts remain attribution-only and not eligible for timing comparison.

This confirms the selected clone hypothesis in both providers. SQLite matching-symbol machine-code evidence maps QueryBinding.SnapshotAndImport, QueryCommand clone constructor, Clone, command SnapshotAndImport and SelectParent to the actual generated AOT code and source. Calls are annotated from the matching `.dbg` address table. This proves code identity and actual call targets; no perf sampling, instruction cost or scheduling claim is added.

The independent correctness fixture built from unmodified main passes native.query (one test) and the existing native dependency graph verifier; it is a correctness-only build and not an ordinary native baseline.

| Evidence path | SHA-256 |
|---|---|
| `experiments/relations-recovery-03/second-layer/postgresql/run/analysis.json` | `88492fb743bac2d86d23a9d4e276c7fac6be45c2ae48af46be8de7c39d8d622a` |
| `experiments/relations-recovery-03/second-layer/postgresql/run/receipt.json` | `eee19cf93c9eb2f5b5bb45ec9376e3153cf1fb38be8b1243683cd702a115ba1c` |
| `experiments/relations-recovery-03/second-layer/postgresql/run/receipt.json.relation-scopes.csv` | `9711ae5892bed1d94740993f0291f55e9141c3bd23f01bfb057b182e49ef52f1` |
| `experiments/relations-recovery-03/second-layer/postgresql/run/receipt.json.relation-status.json` | `edbc4377849dc21c8303321d58533b98aecbd38832cc7df683ffa5584b3dd241` |
| `experiments/relations-recovery-03/second-layer/postgresql/consumer/out/DbPerf.Korda` | `4dde9cbc040c73fec330aec304b2706c7a68c387f0b968a3bafb2732ae81d0c4` |
| `experiments/relations-recovery-03/second-layer/postgresql/consumer/out/DbPerf.Korda.dbg` | `690e22f8f5f4c09cc8d90d915e9ba2e51cbb0b542824eaeab1f76a36ce518c67` |
| `experiments/relations-recovery-03/second-layer/postgresql/package/build-receipt.json` | `17e512d2cbad5edaa7f424ec9399124d49fe0f5275729aebee23c11ff7b6954b` |
| `experiments/relations-recovery-03/second-layer/sqlite/machine-code/identity.json` | `df40c50845288a2d467ee06854046bcc082ab1b5530f9461d3f039b972b933de` |
| `experiments/relations-recovery-03/fixture/identity.json` | `c1f2cacf05907fb323c2b38417e94de8ebea2dd50af0bf5647be6eb8c375c8d5` |
