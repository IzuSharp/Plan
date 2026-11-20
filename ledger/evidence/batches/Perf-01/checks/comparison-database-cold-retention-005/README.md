# Perf-01 final database numerical retention

After all 48 final-002 database processes and both comparison readers completed,
the full numerical projection validated every process, including C1/C4/C8. Its
45 service-eligible and three ineligible classifications are unchanged.

The actual storage pass ran from **2026-11-20 08:42:31.487817 UTC to
08:43:25.578844 UTC**. It retained **208 files, 3,149,431,218 original bytes**, in
**96,507,923 gzip bytes**. For every file, it hashed the original, decoded and
hashed the complete gzip output, reread the still-open original, and made the
verification receipt durable before replacing the original with its compressed
copy. No archive was accepted from a requested or estimated size.

The [numerical hash inventory](public-summary.json) records all 208 original and
compressed byte counts and SHA-256 values without operational paths. The local
complete manifest SHA-256 is
`6294f7d3a5e58e8e4516202d9c0ea906e28652f43d0fc230d238ca1c75117065`.
Free space changed from 8,354,332,672 to 11,406,159,872 bytes.

The source SHA-256 is
`4f0b446210fa6103f379d6d112f26ddd091cf4c0d4f17777d84aff1e07526d35`;
the exact selected metadata SHA-256 is
`768cec9e8706f6b0802e26fa23ab6fe8c109081179f2b572dee37d99e7477518`.
Independent review confirmed the storage/hash/restore mechanisms are unchanged
from the prior verified retention pass. The updated gates bind the actual
completed 50-command execution, full 48-process projection, terminal owner
cleanup, stopped PostgreSQL instances and unchanged original classifications.

Selected files are completed synthetic numerical journals. Small controls,
database snapshots, sources, packages, native libraries, application binaries,
other domains and all long-run evidence remain outside this selection. The
local archive contains the complete file map and fresh-directory restore
instructions. This storage pass grants no correctness, performance or duration
credit. Public numbers and hashes have repository-history retention; no remote
full-raw archive is claimed.
