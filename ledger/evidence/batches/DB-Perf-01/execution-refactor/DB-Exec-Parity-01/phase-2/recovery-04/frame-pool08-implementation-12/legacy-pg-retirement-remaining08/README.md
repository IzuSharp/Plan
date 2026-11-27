# Remaining legacy fixtures for affected frame08 builds

**Prepared only: no directory has been removed by this adapter.** This scope is for the affected Binding/Relations correctness AOT builds, two actual provider package consumers and new short-test evidence. All long measurements remain cancelled; there is no invented long-run reserve target.

The original 13-cluster proposal remains byte-identical at SHA256 `94774111435daad96a9ecdd3f0e97b3f0f6a717aea6d2f52cfa606ab1a83b030`. Two previously completed retirements are excluded and their successful exact receipt is bound. Current read-only inventories of the remaining eleven total 723,210,240 allocated bytes. The sampled-small03 cluster remains excluded because its parent contains 16 trace/analysis directories and bytecode; its 69,656,576 bytes are not counted in this proposed operation. The four original pg_ctl-only exclusions remain outside the gate.

## Exact proposed ten directories

| Task-relative directory | Current allocated bytes | Bound commands | Layout |
| --- | ---: | ---: | --- |
| `experiments/relations-recovery-04/runner-review/proc-tree-visibility-01/postgres-data` | 47,931,392 | 1 | adapter ef2afa93 |
| `experiments/relations-recovery-04/runner-review/proc-cpu-transfer-01/postgres-data` | 47,935,488 | 3 | adapter 7dea271b |
| `experiments/recovery/combined-screen-05/postgresql-01/postgres-data` | 69,918,720 | 67 | original observer |
| `experiments/recovery/early-stop-risk-05/run-01/postgres-data` | 69,730,304 | 11 | adapter 3fc76ff7 |
| `experiments/codec-recovery-03/host-allocation-ab/postgres-data` | 69,656,576 | 25 | original observer |
| `experiments/ordinary-ab-recovery-03-attempt-02/codec-postgresql/postgres-data` | 69,656,576 | 37 | original observer |
| `experiments/ordinary-ab-recovery-03-attempt-02/relations-postgresql/postgres-data` | 69,656,576 | 9 | original observer |
| `experiments/ordinary-ab-recovery-03-attempt-02/workerd-postgresql/postgres-data` | 69,754,880 | 49 | original observer |
| `experiments/ordinary-risk-recovery-03/relations-postgresql-union/postgres-data` | 69,656,576 | 9 | original observer |
| `experiments/ordinary-risk-recovery-03/codec-postgresql-small/postgres-data` | 69,656,576 | 17 | original observer |

The ten total **653,553,664 allocated bytes**, with **13,194 inventory entries**, **228 successful bound command receipts**, **983 retained raw files / 25,607,223 bytes**, and 60 configuration files to copy and read back before any deletion. Allocation uses the current `st_blocks` values from the exact inventories; it is not a projected free-space guarantee when other work runs. Preparation checks all raw bytes against exact published expanded members, all owner/plan/runner/command/config SHA identities, and inventories the ten data directories twice. Physical database file contents are not read or hashed.

## Small adaptation from reviewed subset07

`adapter-from-subset07.diff` is the complete source difference. The original helper and wrapper files are unchanged. Eight functions, including the direct-owner wait4 validation, inventory/path checks, recheck and descriptor-relative removal, are byte-identical to the independently reviewed subset07 source. The lock, persistent-blocker requirement, all-target preflight, six-config copy/readback, intent, per-directory receipt and fail-stop logic remain in the new source.

Seven targets use the original flat observer layout. Three use an explicit new allowlist for the existing local observation adapter. The runner still binds original `run.py` SHA 296e6b80. For these three, runner metadata, plan adapter SHA and adapter-retirement metadata must agree; completion/source-unchanged/passed must all be true, and the adapter server PID/start-ticks must equal the direct owner. The direct owner exit 0 and three wait4 lifetime fields remain mandatory for every target and each planned command must finish inside that lifetime. An adapter `passed` flag alone never proves process exit. The last sampled client identity is not treated as all command identities.

The first probe keeps historical adapter SHA af306cb5 from its archived `adapter.source.py`; the second probe and early-stop run keep SHA d7db0a60. The current adapter path string is not mistaken for the old source bytes. No process-name or absent-PID heuristic provides the positive exit proof. The nested sampled-small03 parent is not allowed by the flat-layout gate and is not selected.

## Published raw binding and historical receipt recovery

Five retained expanded manifests were matched by exact Git blob SHA to pinned metadata in archives01/02/03. The command readbacks used `GIT_NO_LAZY_FETCH=1` and downloaded no payload; `publication-bindings.json` binds all three published subtree identities and source manifests. Current raw files were then hashed against those manifests.

The filename `observations/recovery/archive04-published.json` had been reused for later archive04 publication. Its old archive01 receipt was recovered independently from the exact 5,505-byte member in archive03's 47,096-byte publication-cleanup05 package. The full small package passed the unchanged reviewed stream verifier, the member matched its published expanded SHA, and only that receipt was materialized under `historical-publication-proof`. The current receipt was not overwritten or used as proof of the older commit. The original b54054bd publication and current ded73d7 publication remain distinct.

## Review and execution boundary

The 27 increment controls passed: eight reviewed core functions compare byte-for-byte, all three actual small adapter proof objects validate, and negative metadata/identity/completion/owner-failure cases reject. No real fixture was traversed or removed by the controls; the read-only prepare performed the separately recorded real inventories. The old 22 physical-path/removal controls retain their original identity and were not needlessly rerun.

Final new source SHA256: `9afe149faf79b130bfc5106c6f8a3659e61ce1cc85c27f6a42fc008189c3d900`. Prepared manifest SHA256: `7b8873a36f271f635c0ae6b055dbc3aeb255ba452c8f1875709e0220f2c4d5d0`. `prepare-01.json` records exit 0 / deleted false; `source-freeze-01.json` binds the new source, full diff, controls and exact prepared manifest. The earlier read-only inspector failed safely on archive03 map schema (`sha`, not `gitBlobSha`) before visiting any fixture; its source and failure record remain alongside the corrected inspection.

**Independent review and root's final execution confirmation are still pending.** The concrete command, only after those gates, is:

```sh
python3 retire_remaining.py --execute --expected-manifest-sha 7b8873a36f271f635c0ae6b055dbc3aeb255ba452c8f1875709e0220f2c4d5d0
```

The operation is per directory, not a transaction across ten directories. Any partial failure retains intent and completed-directory receipts and blocks blind retry. Cooperation on the shared lock is assumed; no claim is made against unrelated concurrent filesystem mutation. Atomic replace/readback does not imply a complete power-loss durability guarantee. Only the exact physical data directories may be removed; every surrounding raw, failed record, source, actual artifact and copied configuration remains.
