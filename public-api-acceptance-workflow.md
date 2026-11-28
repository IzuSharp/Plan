# Public API planning and acceptance

Define the intended API and its ownership, errors, cancellation, concurrency,
versioning and AOT constraints in Korda-Design before implementation. Link the
relevant task and contract revisions from the plan. Record source/PR identities
and final review conclusions in ordinary documents.

The implementing task owns XML documentation, generated reference output,
minimal and advanced examples, and applicable compatibility/consumer validation.
A design review does not claim compilation or runtime success. Product checks
must establish those results at the actual tested source and platform.

Update affected task dependencies and record unresolved findings. Do not change a
status merely to satisfy CI. Submit documents in Git/PRs; keep temporary outputs
and recovery state on the execution machine. Do not upload them as Actions artifacts.

Current documentation validation is described in [the CI guide](eng/ci/README.md).
It checks shape and references, without frozen-commit or receipt-hash replays.
