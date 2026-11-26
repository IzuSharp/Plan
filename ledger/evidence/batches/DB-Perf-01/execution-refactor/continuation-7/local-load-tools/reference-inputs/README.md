# Verified reference inputs for the current continuation

[reusable-inputs-01.json](reusable-inputs-01.json) rereads the six ordinary
reference consumers from the root reuse record, the two refreshed before phase
consumers and the two successful Dapper allocation overlays. All 369 bound input
files passed hash checks before and after collection. No build or workload ran.

The copied consumer sources and allocation builder/observer match the reference
source at `05fdd6b507bbfa9e971caa739784cf42dfb7199c`. This establishes byte
compatibility with that committed source, not a new build date or a guessed
original harness commit. The unchanged before workload and refreshed before
phase packages identify product source
`f0078da720e07031bc56464995af6791c41aaae8`. The older phase harness mismatch
record remains explicitly retained alongside its refreshed replacements.

## Reusable allocation overlays

| Provider | Directory under the old workspace `consumers/` | Allocation receipt SHA-256 | Native AOT executable SHA-256 |
| --- | --- | --- | --- |
| SQLite | `allocation-dapper-sqlite-05` | `f86651d51402ce91aec58148ab59a82657497e623f820dd459be074bc63f602a` | `07797f177fdc89da4721c7cad52596167b6e63bd80b102311b698960cab0111e` |
| PostgreSQL | `allocation-dapper-postgresql` | `62e2d1228337a3bdd048a629816a83538b0843f0458d2a1ccc1d964ab4617746` | `8985f08ca835c1f3027d486b8eac79e4309692db723d66cbd304ca9f0658ba00` |

Both have successful `generate` and `publish` commands, a copied successful
ordinary phase receipt, an unchanged original restore graph, actual locked
package bytes, 21 generated source files and exactly one instrumented Dapper
mapper method. The generated instrumentation was independently reconstructed
with the source-bound builder's pure mapper transformation and matched the
captured instrumented source. The published ELF is Linux x64 Native AOT.

The allocation builder hash is
`9697deb087e2a0d036dee4698e1c9bb7bfe6454c79585ee2b2eac77abc534932`;
the allocation observer hash is
`3cd87e22b476fac01bb3933b0c1949174d4c5816640189e76faf772e88a5923b`.
Both match the current committed reference source. NuGet archive SHA-256 and
NuGet contentHash are checked against their separate original records; they
are not treated as interchangeable hashes.

`nativeImages={}` is expected for these Dapper overlays. SQLite's driver loads
the explicitly selected external image:

```text
/workspace/scratch/4a65d70f0fe1/consumers/direct-native/libsqlite3.so
sha256: 2f693e43707c8174c862283185610abca5c671bbf17b6b1af7866bfbcd290282
```

Its historical 1/100/1000-row receipts all bind that image. Npgsql has no
corresponding loaded native image. New SQLite allocation invocations must pass
this exact `--native-library`; both providers must bind the **new ordinary
candidate receipt for the corresponding row count** through `--korda-receipt`.
Do not copy the old plan's historical candidate receipt path into a new run.

The successful builder receipt says `built-not-run` because that builder does
not execute the app. Separate historical allocation observations did execute
these images; they remain historical. These inputs are allocation-only and
always have `timingCredit=false`. Their instrumented latency/CPU is not an
ordinary comparison, and no new candidate or final credit follows from reuse.

## Retained failures and boundaries

SQLite attempt 03 failed before compilation because its old builder compared
the restored raw archive with the wrong asset-graph hash interpretation.
Attempt 04 retained a failed generate command. Both original failed receipts
and the existing generate log are hash-bound in this index and preserved in the
source archive; neither was overwritten or relabeled as successful.

The input archive preserves original receipts, logs, copied and generated
source, project/asset/lock metadata, source compatibility records, the two
failed attempts and the verification tools. ELF and nupkg bytes are excluded
with their exact hashes and original locations. It does not purport to contain
a complete runnable binary bundle. A new build with a different hash is a new
identity.

The [source archive](reference-inputs-01.tar.gz) has 350 members and is 580,862
bytes; SHA-256 is
`bfa2d39e3315fc7056070243c950b0b6a15d199167555ee051de5c383403b00c`.
Its [external manifest](reference-inputs-01.manifest.json) records every member
and 31 binary/package exclusions. Two encodings matched exactly, all members
passed readback, and original hashes were rechecked after collection. This
overview's archive-result paragraph was added after that snapshot; the archive
retains the exact earlier overview bytes listed in its manifest.

The verifier is reproducible without running products:

```bash
python3 verify_reference_reuse.py \
  --root /workspace/scratch/4a65d70f0fe1 \
  --session /workspace/scratch/fd78534029f7 \
  --output /a/fresh/reference-index.json
```

The final mixed-load identity/owner gate remains separate; neither ordinary
reference reuse nor allocation diagnostics supplies any 1800-second credit.
