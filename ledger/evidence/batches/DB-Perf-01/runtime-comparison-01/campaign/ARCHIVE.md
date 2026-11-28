# Offline raw-record archive

`archive_completed.py` is an offline archival utility outside the frozen matrix.
It does not build or run a client, access a database, change a benchmark result,
invoke a subprocess, or send a network request. Preparation consists of source
and static checks only; no archive was executed while formal cells were running.

## When to run

Run only after all eight cells have terminal `passed` or `failed` status and the
campaign writer has released `campaign.lock`. The utility opens the existing
lock read-only and requires `LOCK_SH | LOCK_NB`; an active writer causes an
immediate failure. It retains the shared lock through inventory, copying,
decompression verification and final manifest publication.

All eight `cell-status.json` records must name the expected cell and contain a
valid `resultSha256` and a nonempty `finishedUtc`. A failed benchmark is an accepted terminal state for
archival. Its status and failures remain in the manifest. The original
`02-dapper-postgresql` must still be `failed` with `failures=["released_idle"]`
and result SHA-256:

```text
61f45dae1a6a687298e87e81bdae689fa26a9aae88cd25a60d62e8368de6a50c
```

This explicit pin prevents a later result from silently replacing the original
02 evidence. Missing mandatory raw records, missing result hashes, nonterminal
states, contradictory statuses or changed original records cause archival to
fail. The utility does not synthesize absent records.

## Command

The output must be an entirely new direct child of this evidence directory's
`raw/` directory. An existing output directory is never reused or overwritten.
The utility also pins itself to CPU 8 by default; the outer `taskset` keeps
Python startup and imports on that CPU too.

```bash
taskset -c 8 python3 \
  /workspace/scratch/4a4a6f01f129/DB-Runtime-Compare-01/worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/campaign/archive_completed.py \
  --campaign /workspace/scratch/4a4a6f01f129/DB-Runtime-Compare-01/long-runs/campaign-01 \
  --output /workspace/scratch/4a4a6f01f129/DB-Runtime-Compare-01/worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/raw/long-campaign-01 \
  --cpu 8
```

Do not run this command during an active formal cell. `--cpu` exists for an
explicitly chosen CPU on a later host; this campaign reserves CPU 8 for offline
support work.

## Explicit input inventory

No recursive file discovery, wildcard selection or symlink following is used.
All paths come from the constants in the source. The inventory has **103
mandatory original files**, split into **nine archives**.

| Cell | Required files | Archive |
| --- | --- | --- |
| `01-dapper-sqlite` | 8 base files | `01-dapper-sqlite.tar.gz` |
| `02-dapper-postgresql` | 8 base + 7 PG files | `02-dapper-postgresql.tar.gz` |
| `03-ef-workstation-sqlite` | 8 base files | `03-ef-workstation-sqlite.tar.gz` |
| `04-ef-workstation-postgresql` | 8 base + 7 PG files | `04-ef-workstation-postgresql.tar.gz` |
| `05-ef-satori-sqlite` | 8 base files | `05-ef-satori-sqlite.tar.gz` |
| `06-ef-satori-postgresql` | 8 base + 7 PG files | `06-ef-satori-postgresql.tar.gz` |
| `07-java-native-sqlite` | 8 base files | `07-java-native-sqlite.tar.gz` |
| `08-java-native-postgresql` | 8 base + 7 PG files | `08-java-native-postgresql.tar.gz` |
| Campaign metadata | 11 files | `campaign-metadata.tar.gz` |

Each cell's base files are:

- `result.json`
- `cell-status.json`
- `plan.json`
- `fixture-before.json`
- `fixture-after.json`
- `<cell>.command.json`
- `<cell>.resources.jsonl`
- `<cell>.stdout.log`

Each PostgreSQL cell additionally requires:

- `postgres-owner.json`
- `postgres-stats-before.json`
- `postgres-stats-after.json`
- `postgres-init.log`
- `postgres.log`
- `postgres-settings.txt`
- `fixture.sql`

The campaign metadata archive contains:

- `host.json`
- `events.jsonl`
- `invocations.jsonl`
- `current.json`
- `execution-session.json`
- `continuation-03-session.json` through `continuation-08-session.json`, each
  explicitly listed in the source and mandatory

`campaign.lock` is used for coordination and is not archived. SQLite database
files, WAL/SHM files, `pgdata`, ELF/shared-library/executable images, and `target`
are excluded. A file with an ELF or SQLite header under a whitelisted record
name is also rejected. `fixture.sql` is retained as the textual PG fixture.

## Byte preservation and determinism

Original files are opened read-only. Every directory component and every file
is opened with `O_NOFOLLOW`; symbolic links and nonregular record files are
rejected. Device, inode, size, modification time, change time and mode are
checked around reading, and again before the archive is finalized. The source
campaign directory identity must remain unchanged. Before publication and at
completion, the evidence and reported output directories are reopened with
`O_NOFOLLOW` and their device/inode identity must match the held descriptors.
The existing runner lock is
never created, truncated or replaced by this tool.

Each archive uses the fixed explicit path order, USTAR regular-file members,
relative member paths, UID/GID 0, empty owner names, mode `0644`, and tar mtime 0.
Gzip uses level 9, mtime 0 and an empty filename header. These normalized archive
metadata fields do not modify the originals. Given identical input bytes and
the same Python/zlib implementation, the compressed bytes are deterministic;
Python and zlib versions are recorded in the manifest.

Each cell archive keeps the `<cell>/` prefix. Campaign metadata keeps its
original relative names. No absolute paths, parent traversal, links or extra
members are allowed in the tar payload.

## Manifests and full readback

The output contains:

- Nine `.tar.gz` archives.
- `manifest.json`: independent SHA-256 and byte count for **every original
  record** and **every compressed archive**, recorded terminal outcomes,
  original status/result hash associations, and the compression identity.
- `verification.json`: the length and SHA-256 obtained by fully decompressing
  **every member**, with a per-member match against the original bytes.
- `SHA256SUMS`: standard checksums of the nine archives, manifest and
  verification document.

Verification streams the uncompressed member bytes; it never extracts files
onto the filesystem. It checks exact member identity, no duplicates, normalized
headers, exact length and hash, complete expected membership, gzip CRC/trailer,
and the compressed archive's length/hash after readback. The copied `result.json`
hash must equal the original terminal status's `resultSha256`; the status bytes
must still equal those read at the terminal-state gate.

The manifest's `recordedCellOutcomes` is the source of benchmark outcome status.
`archiveVerificationStatus=verified` describes byte preservation. The original
02 remains a failed benchmark even when its archive verifies successfully.

After completion, compressed artifacts and the two manifest documents can be
checked from the new output directory with:

```bash
sha256sum --check --strict SHA256SUMS
```

That checksum command reads the archives, so keep it outside formal cells too.

## Failure and restart

`INCOMPLETE` is created in the new output directory before copying and removed
only after all archive readbacks, original identity checks, and manifest writes
succeed. If the operation fails, the tool returns a nonzero exit, leaves partial
output isolated in that new directory, restores `INCOMPLETE` if a late failure
occurred after its removal, and attempts to write `failure.json`. If a filesystem
error prevents marker creation, the nonzero exit still disqualifies the output.
Original bytes are never altered or removed. After investigating, choose a new
output directory for a subsequent attempt; the tool never resumes into or
replaces an existing directory.

A completed archive requires exit code 0, absent `INCOMPLETE` and `failure.json`,
successful `verification.json`, and matching `SHA256SUMS`. The preparation-time static
checks are not evidence that a later archive has already been produced or
verified.
