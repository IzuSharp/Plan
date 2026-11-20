# Perf-01 independent recovery host audit

## Verdict and scope

The five accepted historical before-long runs remain valid historical evidence. **None is currently admitted for pairing with a newly executed after-long run in the restored environment.** The original boot-identity gate fails, the original workspace is absent, and the original machine/resource and actual artifact closure has not been re-established. This is an environment and provenance boundary, not a retrospective product failure.

Root has selected a fresh measurement epoch: retain the fixed `ea5fa528035d025bd7a28698ee7c71194432236c` baseline source and frozen workload semantics, collect fresh before and after measurements on the current host, and transfer neither old noise bands nor old long credit into the new pairs. The current retained product source is `2e3995df8d86583ee9443348276ca8d918056bfc`. The new freeze and portable execution owner require their own source review. This audit supplies no build, functional, performance, capacity, retention-decision or long acceptance.

This record was prepared from Plan `0d2ed1b460ca194978cd595417739bce99adc224`, source/small public controls and read-only current host metadata on CPU8. No workload, test, build, raw operation replay, large-payload hash or restoration was performed. The companion [review.json](review.json) contains the exact field comparisons, historical counters and source digests.

## Boot identity and matching observations

The public `protocol_calibrate.py` function `unchanged()` hashes `Path("/proc/sys/kernel/random/boot_id").read_bytes().strip()`. The newline is removed before SHA-256; the raw-file digest is not the comparable value.

| Identity | SHA-256 |
| --- | --- |
| Historical frozen boot, stripped bytes | `d19b8f888214efe7966ce4acd9313f5a8536f876c1e35f78201081604986df45` |
| Current boot, stripped bytes | `da43a0d2a2e133779956f40af91ffa7da7dd18f0f49065a5756faa29361bff32` |
| Current raw boot-file bytes, including newline | `fab4c6b647b597723c31a077dddfe6e4fe590c6b3b4d2eb026bd98403ae5467b` |

These observations establish a **different boot instance**. They do not by themselves prove a different physical machine. The old frozen gate must not be made to pass by silently replacing its boot pin.

Linux, x86_64, kernel release `6.18.57`, Python version `3.12.14`, nine logical CPUs, and all six recorded CPU identity/flags fields match. The model name is `AMD EPYC 9V74 80-Core Processor`; vendor, family, model, stepping and flags match exactly. The clock metadata reports `time.monotonic_ns` with a `1e-9` second resolution. These are observed descriptors, not proof of identical executable bytes or physical hardware.

Both snapshots have unavailable power-governor information and unavailable `cpu.max`, `memory.max` and `memory.high`. Matching unavailable fields do not establish equal quotas, memory limits, power policy or unlimited resources. Physical-host identity, effective scheduling entitlement/interference, physical frequency controls, and storage/database I/O equivalence remain unknown.

This audit's affinity is CPU8. No measured process was launched. The historical service/database allocation remains CPUs2,3 and generator allocation CPUs0,1; their actual masks must be observed again when the new epoch is admitted. The original workspace was directly observed absent. The original toolchain executable bytes, tested binaries, package/native archives and full raw evidence have not been recovered by this audit.

## Historical long evidence and current pairing boundary

The public five-group checklist binds the original baseline source and reports:

| Domain | Accepted effective load seconds | Unexpected errors | Admitted as a new-host paired baseline now? |
| --- | ---: | ---: | --- |
| http | 1802.091185499 | 0 | No |
| grpc | 1802.101046909 | 0 | No |
| codec | 1802.104068505 | 0 | No |
| postgresql | 1802.212239616 | 0 | No |
| sqlite | 1802.209932916 | 0 | No |
| **Total** | **9010.718473445** | **0** | — |

Keep all five acceptances and their original verifier digests. There are still **zero accepted final after groups**. The public checklist explicitly has `full_raw_evidence_published=false` and makes no remote-retention claim for complete raw records. Published digests and numerical summaries preserve identity and conclusions; they do not prove that the corresponding original bytes can now be retrieved.

Recovering matching source files or version strings alone is insufficient for cross-environment pairing. With the fresh-epoch decision, all five before and five after long groups must be collected in the newly frozen environment. Historical values remain separate reference evidence and are never relabeled as current-epoch measurements.

## Completed and interrupted short cohorts

The public final003 protocol projection records 54 validated and service-eligible processes. Preserve that completed historical protocol cohort; it is not the complete domain matrix and grants no new-environment or long credit. The numerical projection itself does not contain a host snapshot. Its historical environment attribution comes from the frozen configuration and handoff, not from an invented field in the projection.

The completed six-process ON weak-writer noise is also a separate historical cohort. Its ranges do not apply to fresh OFF measurements here.

The interrupted 18-process ON/OFF comparison has an **unknown terminal outcome**. The last direct observations preserved in the handoff are:

| Original command identifier | Exit | Observed completion UTC on 2026-11-20 |
| --- | ---: | --- |
| `grpc-unary-0-before-prepare` | 0 | 18:41:12.330894 |
| `grpc-unary-0-before-run` | 0 | 18:41:46.688447 |
| `grpc-unary-0-after-prepare` | 0 | 18:41:48.468662 |

These diagnostic roles mean retained ON2e versus OFF963, not the original Perf-01 baseline. No OFF runtime, later process, reader, final screen or complete-cohort terminal proof was observed at the checkpoint. The absence of the old workspace or processes here cannot supply that proof. Preserve the original receipt state; do not infer success, application failure, retirement or an unobserved termination signal from environment loss.

## Source and control bindings

The following project-relative files were read at Plan `0d2ed1b460ca194978cd595417739bce99adc224`. SHA-256 values are for source or small public control bytes. The public protocol manifest separately binds its numerical projection; this audit did not rerun its reader or revalidate operation journals.

| Source/control path | SHA-256 |
| --- | --- |
| `ledger/evidence/batches/Perf-01/prospective-policy.json` | `0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc` |
| `ledger/evidence/batches/Perf-01/frozen-execution.json` | `85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3` |
| `ledger/evidence/batches/Perf-01/protocol_calibrate.py` | `32db840b1ec8374d66086b298e53055aed9ee9c9e71d2e5f54c6295ae8d039b7` |
| `ledger/evidence/batches/Perf-01/handoff-linux.md` | `54638939df72a1c81aae29c31aa83eb6696ba2ef2487467ab0034d7f0057712d` |
| `ledger/evidence/batches/Perf-01/checks/before-long-five-001/public-checklist.json` | `53ce793e17f04ffff2a0d6420eb26c3e81dcb3609843527b82e97712aaa3b1c6` |
| `ledger/evidence/batches/Perf-01/checks/final-003-protocol-results-001/README.md` | `81bd6f4397ae05e8f68ce7d8dad9b79c45e773c90f749f28120c717888dd760c` |
| `ledger/evidence/batches/Perf-01/checks/final-003-protocol-results-001/manifest.json` | `e88212c178e2ade9ff3651a8b8bb5f6fc2b23fbfaa633761ac81ae20473b9aa6` |

The JSON also records exact Git blob identities and byte sizes. No raw environment, raw boot ID, hostname, host path or process identifier is published. Root owns integration and subsequent execution; this independent audit does not impersonate an external GitHub approval.
