# Already-released final-close experiment

The current measured candidate remains public
`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree
`bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. Its new 18 ordinary query-phase
observations and six paired single-case comparisons passed the unchanged
arithmetic/identity checks. A one-row partial batch already carries observed
EOF; there is no extra empty fetch to delete. The single-row read-complete
phase includes batch release, admission/cancellation checks and final close.
The phase timer does not separately attribute the cost of each queue.

Select one isolated candidate from that exact source in task-labelled
`DB-Exec-10-close-quiet`: skip `controls.post` only if the existing closed
admission, no-running-fetch, completed fetch fence and completed cursor-cleanup
resource snapshot already proves released. Reuse the complete CloseWorker
receipt/error/notification path without waiting. Keep its original queued
fallback whenever any proof is incomplete. The independent callback tail and
Source lifetime proof remain separate. No prefetch, batch-limit, parameter,
provider protocol or public API change is authorized by this narrow experiment.

| Layer | Disposition | Evidence required |
| --- | --- | --- |
| EOF/batch knowledge | Reuse | Existing partial-final-batch propagation and exact-boundary EOF-pull tests |
| Cursor cleanup and fetch fence | Reuse | Real completion/resource proof, never merely fetch ready |
| Already-released control dispatch | Conditionally rewrite | Early ready-before-return, exact receipt and single notification |
| Incomplete proof | Reuse unchanged queue | Blocked fetch tail, cleanup, stop and error fallback assertions |
| Managed final-close controller | Reuse | Setup/control/callback accesses delay publication until safe |

Implement and review source during the current calibration without compiling or
running another workload. At the next measurement gap, run the affected finite
native/managed correctness checks, then paired ordinary single-row and DTO
measurements with independent package/native identities. No current `17da`
measurement receives credit for this source change. Reject the candidate if
correctness fails or no measurable benefit appears. Only an accepted successor
may replace the final four-run freeze; the old source/results remain intact.

This is a prospective experiment, with no completed test or performance claim.

## Prospective ordinary selection rule (before paired measurements)

Compare public `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` with isolated
public `92b923075952bac347619ee7817c372ee6e415cb`, using each independently
built provider package and its ordinary Release Native AOT consumer. Run two
serial rounds per provider, each at 256 iterations and three windows per route
for 1, 100 and 1,000 rows. Reverse the two Korda command positions in the
second round; keep Dapper after its matching candidate SQL receipt. Record
both rounds, without selecting a best window.

The narrow hypothesis is final-close dispatch cost. Accept only if the
prepared single-row read-complete p50 improves by at least 10% in each
provider in both rounds. Also require no more than 5% regression in pooled
prepared per-operation total p50 for any provider/row-count pair, all result
contracts equal, all commands successful and all eight candidate owners
drained. Per-operation total is the sum of that sample's construction,
submit-to-first-row, read-complete and release ticks, not a sum of separate
percentiles. Report tails, CPU and bytes without treating them as independent
proof of the queue's exact cost. Failure of a guard or selection rule retains
17da; no automatic extra retries or threshold change. This short selection
does not earn the final four-run acceptance.

## Observed decision

The two-round arithmetic reports contain 36/36 eligible ordinary observations,
equal recorded query/result contracts, no command/observer failures and all
eight Korda owners zero. The prospectively selected experiment is **rejected**.
PostgreSQL single-row prepared read-complete p50 changes 34.972 -> 50.580 us in
round 1, but 65.898 -> 39.909 us in round 2; it does not satisfy the required
consistent improvement. SQLite 1,000-row pooled per-sample total p50 changes
1,755.582 -> 1,874.589 us (+6.78%), exceeding the predeclared 5% non-regression
bound. SQLite single-row read-complete does improve in both rounds, but cannot
independently select a shared provider path. No additional best-of retries or
threshold adjustments are made.

The final product remains `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`.
Experimental public `92b923075952bac347619ee7817c372ee6e415cb` stays on its
separate branch, outside PR #37. Public `0aa0697d683d8402e26d5c0c7309c6a5f9e4eff9`
was superseded after successful independent package builds and was never timed.
Both build attempts, finite correctness evidence, source review and all paired
raw observations remain evidence, with no final-candidate performance credit.
