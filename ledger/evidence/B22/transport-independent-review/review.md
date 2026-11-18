# B22 transport controller independent review

Reviewer: `/root/b21_service`; not an author of the reviewed transport controller.

Final reviewed commit: `8736c72e07c009db89763215c5f67234045dd946`. Actual network/data executions: `9f4e1429f4f4d5fd51bfceafb0b02b9341858b31`.

**Verdict: all three concrete findings closed.** No remaining blocker was found within the requested transport cases and their directly used helper scope.

## Closure

- **B22-TRANSPORT-T1** — 9f4e142 reads/parses socket frames during hold without acknowledging DATA, limits cumulative flow-controlled bytes including padding to 4096, and rejects end/reset. All four actual rows retain 4096 bytes before/after >2.2s holds and exact full delivery afterward.
- **B22-TRANSPORT-T2** — 9f4e142 checks canonical operation UUID, responseVersion1, same item, deterministic SHA256, length and version2, plus independent SQL replay tuple (1,200,actual returned body). All four actual rows pass.
- **B22-TRANSPORT-T3** — 9f4e142 adds exact named cases, exit0 and unchanged artifacts. 8736c72 removes the intermediate Evidence.close publication and performs one atomic final save after strict predicates. Nine in-memory policy variants and a publication-failure path pass. Existing four actual successful rows meet all predicates.

## Actual retained observations

| Row | Assertions | Held flow-controlled bytes | Hold seconds | Status |
| --- | ---: | ---: | ---: | --- |
| sqlite-jit | 22 | 4096 | 2.206541 | passed |
| sqlite-aot | 22 | 4096 | 2.206392 | passed |
| postgresql-jit | 22 | 4096 | 2.203535 | passed |
| postgresql-aot | 22 | 4096 | 2.206923 | passed |

The four rows contain the exact three required cases and 88 passed assertions. Artifact hashes were independently re-read and remain identical. Each row has the expected actual JIT/AOT witness. The exact executable, controller, receipt and timeline hashes are retained in `review.json`.

The final receipt-only correction does not change any transport case or process-snapshot AST. Existing successful rows meet every current strict finalization predicate. They remain attributed to their actual executed controller; no application or network cases were rerun and no old binaries were relabelled.

The small policy check extracts the actual current `main.finally` AST and exercises in-memory completion, partial, empty, artifact-change/unverified, failed, interrupted, order-mismatch and publication-failure records. It verifies one final publication and timeline closure. This is controller policy evidence only.

## Limits

This review does not establish aggregate managed-root/native-owner accounting, all B22 fault correctness, performance, or any 30-minute/24-hour/72-hour duration. Those claims remain explicitly absent. It does not re-audit the full inherited fault corpus.

## Reviewed file hashes

| File | SHA-256 |
| --- | --- |
| `tests/Verification.EndToEnd/transport_faults.py` | `e31f376fefb8ec9001afc130c864a426e74288771dcd5d6b9f968c9ea6b8846f` |
| `tests/Verification.EndToEnd/transport-faults.md` | `9ddb0e637d0a42d34f23ea9e50afedfd88e0e6c0d0fa7fc64d45d74fac741349` |
| `tests/Verification.EndToEnd/harness.py` | `24e90f84dfb2e4981e6277733ec6da76ef14bf49b4f314c00d67949c87834725` |
| `tests/Verification.EndToEnd/faults.py` | `e1f093269a9cee95cc96889b468e8396acc68486717ded3bc20fad8480239b54` |
| `tests/Reference.TaskService/run.py` | `e805319b5129e1a84963720c4366c17b26b96e97e838e2cb96d74adc5f951dd2` |
