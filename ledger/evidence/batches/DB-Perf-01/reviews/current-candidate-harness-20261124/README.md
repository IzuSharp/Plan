# Current candidate and harness: independent review checkpoint

This checkpoint preserves the exact independent review records for the current
ordinary CI candidate and the frozen active 35-case harness. It adds no new
runtime, long-test or public-package acceptance.

## Actual candidate bytes

[candidate-byte-review.md](candidate-byte-review.md) and
[candidate-byte-review.json](candidate-byte-review.json) cover both provider
artifacts from [successful ordinary CI 45438460386](https://github.com/IzuSharp/Korda/actions/runs/45438460386).
The actual package producer is `3d5ba3f9884308caa691718f73a74aa42be19d94`,
tree `74a76bc5d00671a48221d0ed19002a3ffffd319f`, which equals the observed
`cf7c080aeef01e3b012d0564e6f930b77e9c697f` CI head tree. Both packages are
unsigned `0.1.0-ci.1` candidates.

Both downloaded archives, the nupkg files, all 81 unsigned package members,
native ELF payloads, producer metadata and twelve existing AOT command logs
were independently rehashed. The artifacts do not contain the six AOT consumer
ELF bodies, so the review does not claim a fresh byte check of those executables.
No consumer was rebuilt or executed in this review. Actual signed public NuGet
readback and fresh public-package Native AOT consumption remain separate work.

## Current oracle and server CPU implementation

[harness-review.md](harness-review.md),
[harness-input-hashes.json](harness-input-hashes.json) and
[harness-summary.json](harness-summary.json) bind the read-only source review to
`d665c0c9629922cfff0e48fa535d6f21393f8162`. Public commit-pinned source URLs and
Git/SHA-256 identities are recorded; implementation files are not copied here.
The reviewed source already implements sticky correctness-oracle failure
rejection, primary/cleanup failure preservation, and a task-owned pre-exec
PostgreSQL cgroup with cumulative CPU and fail-closed retirement checks.

[historical-cgroup-observation.json](historical-cgroup-observation.json) is an
offline recomputation of one existing prior-run sample from artifact
`14952080637`, ZIP SHA-256
`bc4f1195eba7fcd518120e8e3c61b0e1f6304f8a76dd1992ba7d3da4ebc1cb39`.
It observes a positive-CPU backend disappearing from the live process tree while
the same cgroup's cumulative counters remain available. It is historical
preflight evidence, not current-run qualification or a completed long segment.

The original reviews retain local recovery paths and references to an older,
unapplied prototype. Those references describe review history; they do not
publish that prototype or transfer its local test results to the current code.
The original `historical-cgroup-sample/observation.json` reference in the review
maps to `historical-cgroup-observation.json` in this checkpoint. The corresponding
original local source directories are intentionally represented by public
commit-pinned references. No rejected historical source archive is included.

## Reproduction and observation boundary

[manifest.json](manifest.json) binds each exact retained review file by length
and SHA-256. Retrieve the two CI artifacts identified in the candidate JSON,
verify the ZIP SHA-256, then verify the nupkg and each listed member. Fetch the
source files from the public fixed commit URLs in the source index and verify
both their Git blob identities and SHA-256 values.

At the 2026-11-24 19:03 UTC live observation,
[campaign 45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267)
was still in VM admission/calibration and all eight long steps were pending.
Accepted long credit remained **0/8, 0 effective seconds**. This timestamped
observation is not a prediction of later results; re-read the live run and raw
checkpoints before continuing.
