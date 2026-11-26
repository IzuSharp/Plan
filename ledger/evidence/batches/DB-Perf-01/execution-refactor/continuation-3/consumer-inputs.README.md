# Twelve ordinary consumer source snapshots

[consumer-inputs.tar.gz](consumer-inputs.tar.gz) contains the exact completed
ordinary external consumer input files for before/candidate/Dapper.AOT ×
SQLite/PostgreSQL × query-phases/mixed-workload. It is a source and provenance
recovery archive. It grants no query-execution, performance or long-test credit.

The archive contains 703 original files (11,683,494 bytes), plus an internal
`consumer-inputs/MANIFEST.sha256` covering those files. The gzip archive is
945,331 bytes with SHA-256:

`61d6718cb6dca23c087c9498b2134d6b5ec40c870a2064e1ff69b0b4ea91f82f`

The [external manifest](consumer-inputs.manifest.json) lists each path, size and
SHA-256 and includes per-consumer source/actual-generated-source summaries.
Each original build receipt, successful publish log, root C# source/project,
SDK/configuration file, available asset graph and actual `generated/` source
file is retained. `packages.lock.json` was absent from these ordinary consumer
roots; their available complete `project.assets.json` graphs are retained.
The Korda and Dapper consumer builder source files are also retained under
`consumer-inputs/build-tools/`.

The archive uses sorted regular-file entries, mode0644, uid/gid0, empty owner
names, tar/gzip mtime0 and an empty gzip filename. Rebuilding the archive twice
gave identical bytes. A temporary unpack then verified every file's hash and
size against the source snapshot before the Plan worktree's untracked expanded
copies were removed. All original `/workspace/scratch/4a65d70f0fe1/consumers/`
directories remain untouched.

To inspect the source snapshot locally:

```sh
mkdir consumer-inputs-inspection
tar -xzf consumer-inputs.tar.gz -C consumer-inputs-inspection
cd consumer-inputs-inspection
sha256sum -c consumer-inputs/MANIFEST.sha256
```

The internal root is `consumer-inputs/`; the checksum paths are relative to the
directory containing that root. Read each build receipt before restoring its
exact dependencies. Absolute original paths in receipts/configuration remain
unchanged evidence. A relocated recovery must document new paths and rebuild
with the frozen source/toolchain/package identities; an archive extraction is
not a substitute for a successful restore/publish record.

No binary executable, native `.so`, `.nupkg`, restore cache, `bin/obj` tree,
PostgreSQL data or private certificate is included. Binary/package identities
remain in the original receipts. The actual generated Dapper command factories
and row readers can therefore be reviewed without reconstructing their bytes
from a hash or regenerating them with a different SDK/package version.
