# A07 independent Linux review

Reviewer: Task-04 root, independent of the callbacks/async author. Final source
9db03cf55f2d494993da36ccccf3e255740299df; exact formal receipt is indexed in
[acceptance-linux.json](acceptance-linux.json).

Reviewed D06 create/register/start outcomes, synchronous registration/terminal races,
setup sentinels, cancellation registration drain, counted internal control authority,
single terminal latch and release publication, typed one-time result take, retained
input ownership, native WorkLease/callback quiet and external coordinator reclaim.
The native operation stores the prepared result before publication and permits take
after native retirement, without exposing Rust Future or a generic result ABI.
Task publication and native/managed reclamation stay separate; cancellation requests
never replace a committed native outcome. No public plumbing was added.

## Findings and closure

- A07-R1: a cleanup exception entered quarantine but could leave engine admission
  unpoisoned with no later wake. The bad-retire/no-later-signal regression failed
  against the preceding source. SchedulingFault now invokes trusted nonthrowing
  poison once outside the lock and retains uncertain owners. Actual JIT/AOT
  isolated quarantine regressions pass; retained ownership is not labelled cleanup.
- A07-R2: a post-copy binding failure discarded already-copied native diagnostics.
  The exact DomainError regression failed before repair. Final exception construction
  preserves domain 17, code -71 and correlation 123 outside the UCO frame and records
  the original terminal status separately. Native outcome is not rewritten.

Both findings are resolved; no open blocking issue remains for Linux A07. The
committed-source runner passed native state/export checks, JIT 355 / Native AOT 356
assertions, 59 normal-path owners reclaimed, finite native worker/cancel/GC races,
examples and exact UCO/API/XML/reference checks. Existing A02/A05 exception signatures
were compiled unchanged. Before failures and all quarantined cases remain in the
raw evidence. This is independent technical review, not GitHub approval, executor,
pristine-consumer, Windows, unbounded-load or performance certification.
