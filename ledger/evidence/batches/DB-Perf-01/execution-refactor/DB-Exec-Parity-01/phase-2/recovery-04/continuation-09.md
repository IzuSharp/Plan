# Continuation09 — tail06 closed; short-only pull scheduling experiment

This checkpoint supersedes Continuation07's pending tail mechanism and ordinary
measurements. All long measurements and matched-before long supplements remain
cancelled under [Scope08](short-only-scope-08.md). No long cell was started. The
previous 0/4 is historical, not an outstanding acceptance gate.

## Product selection

**Keep integrated05 and do not integrate tail06.** The root accepts the independent
review's recommendation after the closed 114-process ordinary screen and the
final 12-cell short mixed gate. This is a benefit/risk decision, not a correctness
failure or a claim that tail06 is slower in every workload. Do not layer another
candidate on tail06 or add a provider-specific switch to rescue this experiment.

The selected provisional product remains Korda `2ea67ce1902f330679c3ebff4d6d5733be20f69c`,
tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`. Its actual integrated05 consumer
source is `867c869a7e51949122b3dd13e4c7c6df2a914ec7`, the same tree. Tail06's separate
ordinary source `4a9e4435ea5c836be44fb00dc4219301567072c6`, generated code, actual
packages, ELF/debug/native images, diagnostics, controls and raw results remain
rejected-candidate evidence. They are not relabeled as integrated05.

## Completed evidence — do not rerun

| Work | Actual scope | Result and limit |
| --- | --- | --- |
| Tail correctness | Both real databases, Release Native AOT; final B04 438 assertions/36 managed retirements; independent 1,489 checks | Passed, final owners zero. The old-code negative control fails the new exact-Post assertion on SQLite; PG was not reached, so it is not a two-provider baseline pass. |
| Tail mechanism | Four separate diagnostic PackageReference AOT processes; 16 measured text1000 businesses/provider/variant | 512 measured pull requests and 528 coordinator offers/executes per cell. Tail inline delivery is directly proved for 474 SQLite and 512 PG eligible requests. One SQLite-before overlap remains unknown. Independent 2,589 checks passed. |
| Tail ordinary screen | 114 serial ordinary processes, 233,472 successful businesses; two reversed rounds, C1, 2,048 measured operations/case | Zero business errors/retries/oracle failures, zero final owners. Independent 5,487 checks and 1,244 distinct file hashes. CPU decreases in both rounds for 12/19 cases; p99 increases in both for 7/19. This does not establish universal benefit. |
| Final tail short mixed | 12 serial 30-second cells, rate500, queue64, SQLite C4/PG C8, 35 business kinds; warmup separate, 5-second released-idle observation | 180,000 successes/4,392,804 rows, zero refusals/errors/retries. Independent 4,963 checks and 806 distinct hashes. Actual client and PG-owner lifetime intervals do not overlap across cells. |

The mechanism proves a changed completion boundary, not a timing benefit. Its
528 offers count all turns in the 16 measured cursor lifetimes; they are not a
timestamp-clipped CPU window. Native prepare/run/take counts, SQL work and batch
size remain unchanged. The diagnostic logging/trampoline is intrusive and gets
no ordinary CPU, allocation, latency or frequency credit.

### Final mixed differences, tail06 relative to integrated05

Each entry is round1 / reversed round2. Negative CPU and latency values are lower.

| Provider | Client CPU/success | Service p99 | Scheduled p99 | Released-idle RSS difference |
| --- | ---: | ---: | ---: | ---: |
| SQLite | -5.30% / +1.92% | +3.16% / +1.85% | -3.90% / +4.52% | +0.129 / +0.020 MiB |
| PostgreSQL | -3.85% / -2.25% | -3.01% / -23.68% | -18.01% / -26.69% | +2.230 / +1.039 MiB |

PG's repeated CPU and tail-latency improvement is retained as positive evidence.
SQLite did not repeat a net mixed benefit. The mixed workload mostly uses rows32,
so it does not erase SQLite text1000 CPU -15.59%/+8.38% or early-stop p99
+5.14%/+113.85% from the earlier screen. Small percentage differences are not
individually labeled statistically significant. There is no reason to extend the
tail experiment or seek a favorable extra round.

The tail/Dapper service p99 remains 4.53/4.37 times for SQLite and 2.48/3.46 times
for PG. Managed bytes/success remain about 2.74–2.83 times Dapper. Mixed process
CPU ratios of about 1.21–1.27 do not show query-execution parity: the identical
arrival producer spins when its remaining interval is at most2ms, and rate500
targets exactly2ms. Its measured CPU share is unknown; do not subtract a
theoretical producer budget. C1 query-specific results still expose much larger
CPU gaps. No framework-only zero-allocation or ordinary native-allocation claim
is made. PG live+reaped sampled CPU, non-atomic inner/outer observations, and owner
wait4 lifetime costs remain separate. A five-second idle snapshot is not a leak
diagnosis or a sustained-memory guarantee.

The complete closed review is retained at
`experiments/tail-completion-06/independent-mixed-gate-review-01`:
README SHA256 `46ea9554983481e30b7c643713ee5fbbf3ffa512970154da0a06bc73b7b8adb1`,
summary `90f5e5b30e81b88209bdd6492d360a6c75f25dd0926f8a1a947319da53f0a4f6`,
checks `6613a13c806020b2dfab8b0f53a5c1a1019367cc56eadfe726282044014de523`,
receipt `88a6d5ea36f05870f90499bc58cfef41ddee7445bb1747bbebb1759725351b26`.
Readable metrics and selected original summaries accompany this checkpoint in
`tail06-closed-09`; complete raw records and actual artifacts belong to the
append-only supplement04 archive, whose publication must be checked separately.

## Next measured hypothesis

Select only the isolated [HostPull local-queue experiment](pull-local-07-hypothesis.md),
on integrated05. The measured repeated coordinator turns and actual forced
nonlocal queue parameter justify this small falsifiable test. They do not prove
exclusive queue CPU, OS wakeups, cache misses or an explanation for all remaining
RhSpinWait. Record Design before editing the product; actual default-scheduler
progress and ownership checks must pass before ordinary short measurement.

## Recovery and delivery

Continue at `/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01`. The primary three
task branches remain `task/DB-Exec-Parity-01-linux`; Korda PR40, Design PR21 and
Plan PR36 are still unmerged. Design scope08 and Plan scope08/continuation07 CI
have succeeded. Product PR40 CI on integrated05 succeeded. None of those PR
results is a public release or public NuGet consumption receipt.

Six passed zero-cost-06 PostgreSQL physical fixtures were retired only after the
unchanged reviewed helper verified raw identities, positive owner exit/wait4,
complete client lifetimes, retained configuration readback and unchanged
inventory. Raw measurements and six configuration files per fixture remain.
Aggregate `experiments/recovery/tail06-fixture-retirement-01.json` SHA256
`2ef1eb2b81525159ffff717f5841e2b72dd54312894fd1818061a2fd3023ac51` records this.
This makes space for evidence archiving; it is unrelated to any long campaign.
The older13-fixture proposal remains paused and the four pg_ctl-only fixtures
remain untouched.

Supplement04 is being assembled and blob-uploaded. Blob upload is not durable
branch publication: the root must publish and read back its tree/commit first.
Do not delete original evidence on the strength of an incomplete upload. Keep
Go drafts Korda39 and Plan35 unchanged. After the final short-supported selection,
complete independent review, normal merges, unchanged existing CI, rule-selected
release and actual public-package AOT verification. All measurement stays local;
no CI performance action is added or triggered.
