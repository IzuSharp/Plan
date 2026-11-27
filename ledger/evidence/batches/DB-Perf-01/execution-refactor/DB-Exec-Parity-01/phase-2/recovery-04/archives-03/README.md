# Archives-03: sealed Recovery05 evidence

This increment preserves completed early-stop controls, zero-cost and pressure measurements, runner/fixture controls and reviews, CI-timeout evidence, publication receipts and the authorized local archive-duplicate cleanup. It contains **942 members in three packages**, with **42,987,361 expanded bytes**. No active tail06 source, build or measurement is selected. Creating this archive grants no new correctness, performance, parity or long-acceptance credit.

## Packages and dependencies

| Package | Members | Compressed bytes | Contents |
|---|---:|---:|---|
| mixed-zero-pressure05 | 770 | 1,022,000 | All12 zero-cost and16 pressure cells: raw results, commands/resources, original validations, controller plans/receipts/logs, source snapshots, complete35-case ledgers, final analyses and independent reviews. Pressure includes35-class successful shares and per-second rejection bins. |
| closed-controls05 | 151 | 238,192 | Completed early-stop-risk05, CI timeout evidence, wrapper v1/v2 controls/static/abort/independent reviews, fixture retirement helper/controls/reviews and actual14 retirement receipt, local runner and checked repository observer/campaign/contract sources. |
| publication-cleanup05 | 21 | 47,096 | Pinned archive01/02 publication/readbacks, continuation06 and related publication mappings, cleanup intent/receipt/script/df, current local recovery note and exact prior path→blob maps. |

The increment relies on existing actual consumers and runtime artifacts, not new copies:

- `archives-01` in `IzuSharp/Plan` commit `b54054bd1f3befe94e1817cc29f494bd782854b9`: baseline/Dapper consumers, PostgreSQL runtime, original tooling and earlier diagnostic artifacts; preserve its historical Stage1 dependencies as documented there.
- `archives-02` in commit `27e0f35709036b0737ed101ba6472ce1461c0538`: integrated04/05 actual ELF/debug/native/nupkg/generated artifacts and earlier closed controls.

Both directories are under `ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/`. Their root-agent readback receipts are themselves preserved in this increment. Source base, dependency identities, failed verdicts and local-built versus connector-published mappings are not relabelled.

## Scope and evidence limits

The exact member paths, sizes, hashes, modes and exclusions are in `raw-archives/index.json` and the expanded-file manifests. Physical PostgreSQL clusters and SQLite database/WAL/SHM fixtures are excluded. Retired database directories are not reconstructed. Original raw/configuration and fixture-retirement evidence remain. Compiler/cache directories are excluded while retained generated assets/response/source evidence follows the existing selection rules.

The zero-cost evidence is12 short ordinary cells and the pressure evidence16 short ordinary cells. Neither is a30-minute final-acceptance cell. The pressure reports preserve non-monotonic transient refusals, candidate continuing rejection and final10-second observations; they do not claim exact Dapper capacity. Client CPU includes the arrival producer/harness, native allocation and framework-only allocation remain unknown, and successful business mix can change under rejection. PostgreSQL sampled endpoints and wait4 lifetime remain separately scoped.

The first SQLite zero-cost cell retains its wrapper-v1 provenance and is reused exactly once by the later controller. Later closed cells use the recorded wrapper-v2 hash `c0478eb0eb6b444e1923a4e694052b335933ae05aa98f4f403840e2b99c1007d`. Failed controls, partial/aborted attempts and their original scope are preserved.

## Verification and restore

The self-contained `streaming_archive.py` is the independently reviewed, corrected implementation with SHA256 `b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c`. The earlier uncorrected writer-v4 is not the active restore path. Python3 with standard-library `lzma` support is sufficient.

After downloading this directory, including its ordered parts:

```sh
python3 streaming_archive.py verify --index raw-archives/index.json
```

For restoration into a new destination:

```sh
python3 streaming_archive.py restore --index raw-archives/index.json --extract /path/to/restored-workspace
```

Restore required archive01/02 dependencies first for full workspace recovery, then apply this later increment explicitly if a differing earlier member exists:

```sh
python3 streaming_archive.py restore --index raw-archives/index.json --extract /path/to/restored-workspace --replace-existing
```

Verification streams parts directly through XZ/tar and checks every part, both complete streams including tar padding, and every member hash/size/mode. It creates no complete compressed/tar/roundtrip copy. Extraction commits one verified member at a time and assumes no concurrent mutation of the destination; it is not an atomic transaction over the whole archive. Parent containment is checked before directory creation and afterwards. Original workspace-relative paths are restored; absolute paths inside immutable receipts remain historical provenance.

The builder used CPU8, nice19 and single-thread liblzma preset3/CRC64 outside measurement quiet windows. `records/source-identity.json` pins the builder and engine. Source selection uses explicit cooperative sealing plus per-file stat/read checks, not a simultaneous filesystem snapshot.

## Local availability and publication

The prior local archive01/02 compressed duplicates were removed after exact SHA verification and confirmed remote readback. The selected original raw/ELF/package/source artifacts were retained. Full restoration of those older compressed archives therefore requires retrieving parts from the pinned published commits, as described in `LOCAL-RECOVERY-AFTER-CLEANUP-05.md` inside the publication-cleanup package. Do not mistake old uploader snapshots for current local file availability.

This increment's uploader creates only Git blobs. Its manifest supplies exact target paths, SHA256 and Git blob SHA; receipts are atomically saved per blob. Root-agent tree/ref publication and subsequent readback are separate operations. Until that happens, `remotePublication=false` is intentional. No CI workload, benchmark, profiler, calibration or stress test is introduced by this archival work.
