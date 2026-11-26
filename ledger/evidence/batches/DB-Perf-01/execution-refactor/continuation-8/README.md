# DB-Exec-11 continuation: execute the frozen final campaign

## Recovery identity and current status

The owner resumed the interrupted full C# Fluent to C++ database execution-path
refactor on 2026-11-26 (Asia/Shanghai). This continues the existing Korda #37,
Korda-Design #20 and Plan #34; it does not restart implementation or change the
frozen candidate. The latest public heads observed on recovery were Korda
`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, Design
`ca1933e93678039b492f10a8b47045b11827f1a4`, and Plan
`9e4aad4c04c68dd30ab3bcad68a977000b4717e2`. The remote Git trees were read and
matched the existing local publication receipts. Existing CI succeeded for all
three heads; [the exact observations](remote-checkpoint-and-ci-01.json) retain
run URLs and source identities.

The original freeze remains SHA-256
`fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a`.
All 373 frozen files were rehashed successfully before launch; both original
producer worktrees remain clean at exact public17da/treebc9087d. See
[frozen-input-rehash-before-01.json](frozen-input-rehash-before-01.json).
The new [host observation](host-before-final-recovery-01.json) records the same
Linux node, kernel, architecture and affinity as the preceding campaign.
It does not establish exclusive physical hardware or invisible cgroup quotas.

The unmodified SQLite final plan started at **2026-11-26 08:38:19.924859 UTC
(16:38:19 Asia/Shanghai)**. The fixture completed with exit0 and no observer
errors. At this publication checkpoint the first1800-second Korda interval is
still running; **accepted final credit remains0/4**. No completed run is inferred
from resource samples. The supervisor starts PostgreSQL only after the entire
SQLite runner succeeds, and stops on a provider runner failure.

## Exact sequence and resumption

| Order | Provider | Cohort | Concurrency | Offered rate | Measured interval |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | SQLite | Korda17da | 4 | 3000/s | 1800s |
| 2 | SQLite | matched Dapper.AOT | 4 | 3000/s | 1800s |
| 3 | PostgreSQL | Korda17da | 8 | 3600/s | 1800s |
| 4 | PostgreSQL | matched Dapper.AOT | 8 | 3600/s | 1800s |

Each cell also records15 seconds of post-disposal idle. The exact plans and
commands are unchanged in the [published freeze checkpoint](../continuation-7/current-measurements/campaign-17da/README.md).
The completed120-second before/current supplement remains separate.

Local measurements remain under
`/workspace/scratch/fd78534029f7/measurements/{sqlite,postgresql}-final-01`.
The live supervisor receipt is
`/workspace/scratch/166b48a091b9/recovery/campaign-supervisor-01.json`.
The original product/Design/Plan worktrees remain under
`/workspace/scratch/fd78534029f7/worktrees`; this continuation reuses the
existing task worktrees and changes only Plan handoff/review records during
measurement. Frozen scripts, plans, products, consumers and packages are unchanged.

After an interruption, inspect actual command receipts, output directories,
supervisor status and process/session availability before starting anything.
Do not rerun a completed cell, overwrite partial evidence, shorten an interval,
relabel another source, or start another local workload alongside an active one.
If an underlying failed run requires a new output directory, preserve its
failure, derive a fresh plan and make a new freeze before the new measurement.

## Independent review and remaining work

- [Implementation and ownership review](review-implementation-01.md): formal
  entry routing, Find snapshots/mapper identity, command completion, PostgreSQL
  commit proof, package receipts and two distinct whole-process GC scopes.
- [Design, upstream, history and CI review](review-design-ci-01.md): source pins,
  real generated consumers, historical guarantees mapped to maintained C++ tests,
  exact CI selection and existing main publication conditions.
- [Freeze and measurement review](review-freeze-01.md): calibration, comparable
  baseline, SQL placeholder/text boundaries, invocation order and final gates.

No new correctness blocker was found. These source/receipt reviews do not accept
unfinished measurements or future publication. The specific review-label error
(30-second offered GC examples initially called120 seconds) is explicitly corrected
in the implementation review; original evidence was not edited.

The requested impact command was run again on the exact source-equivalent
product tree. [Receipt](impact-current-01.receipt.json) and
[plan](impact-current-01.json) select interop, linux, postgresql and sqlite only.
There is no benchmark execution action. Performance remains local; no workflow,
job, button, schedule or hidden test load is added.

After all four actual intervals, use the unchanged arithmetic analyzer and
identity/owner supplement, review raw business counts and all eight candidate
owners, preserve failures and refusals, archive and read back evidence, and update
current navigation/PR descriptions. Normal reviewed merges and observation of
existing main CI, independently selected versions, NuGet readback and actual
public Native AOT consumption remain authorized and pending.

Framework-only managed allocation0B and exhaustion of all possible optimization
opportunities are not established. Final reporting must preserve the actual
measured gaps and the rejected quiet-close experiment. The old eight-cell history
and all frozen verifier inputs stay unchanged.
