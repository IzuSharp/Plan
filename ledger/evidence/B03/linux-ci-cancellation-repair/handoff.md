# B03 CI cancellation-fixture correction

Owned commit: `c9d5400f8371d3501696caf126c6b4496ea7e5d2` on
`task/Task-02-B03-linux`. Worktree:
`ROOT/.worktree/Task-02-B03-linux/NativeWeave`.

Only `native/database/sqlite/tests/support/scenarios.rs` and the provider guide
changed. The provider implementation, managed API, shared manifests and dependency
locks remain byte-identical to accepted B03 `c1d249b`. Root owns integration,
publication and the next normal PR CI run.

## Original failure and decision

PR #13 head `b6728f7bcde1a79f90797a517efb2f54fc5190dc`, tested merge
`846c0d321d0a49503f2e70de8ac15eb95a395b3e`, failed
[CI 43837773614](https://github.com/IzuSharp/NativeWeave/actions/runs/43837773614)
in build job `133198594379`. Workspace Release test
`actual_sqlite_provider_and_transaction_composition` returned
`cancel result missing` after scenarios 1–4.

The test treated actor `active_operations` as evidence of SQLite worker execution.
The actor publishes that counter before dispatch. Cancellation can therefore win
before a fetch, close the row stream without a SQLx error and publish a valid
`stopped=true` retirement receipt. That behavior already follows the component
contract and is consumed by B06. No provider change is needed.

The original failed log and read-only diagnosis remain under `original-ci/` with
their source/blob identities. No original failure or accepted receipt was edited.

## Corrected proof

1. A full one-row adapter channel prevents the next fetch. Cancellation must yield
   exactly its retained first row followed by EOF, with `stopped`, `stop_requested`,
   actual worker retirement, handler removal and `Usable` disposition. The row peak
   is exactly one; all reservations drain and the same physical marker remains.
2. A test-only SQLx public collation callback observes the actual SQLite worker
   inside the recursive query. Its first comparison signals the test and waits
   on a bounded release channel. The test cancels while the worker is held, then
   explicitly releases it and requires **exactly Interrupted**. A callback timeout
   cannot count as success; disconnect/timeout also cannot strand the worker.
   Comparison returns ordinary `left.cmp(right)` and cannot panic through native
   code. The production progress callback remains unchanged and reads only
   native atomic state.
3. After the old token requests cancellation again, a fresh-token 1..5000 recursive
   aggregate must return exactly 12,502,500. It exceeds the configured 1000-op
   progress interval, unlike the previous constant SELECT. Same-session marker,
   old-token reuse rejection, pre-canceled rejection, zero active/queued commands,
   zero retained input bytes and final SQLx shutdown acknowledgement remain.

## Source-bound validation

`formal-001/result.json` SHA-256:
`17e98b67a7def2e98088a535e8e3bb94b5a9b03484d547a6d0d8110f957869c7`.

- 11 scoped commands passed from clean committed source: both native formatting
  and Clippy paths, focused Release test, fixture build, locked managed restore,
  managed build and actual JIT/Native AOT execution.
- All 102 source inputs remained unchanged during the run. Only the two intended
  test/documentation files differ from the previous accepted B03 source receipt.
- The focused Release test executed its existing 12 scenario groups. Each actual
  JIT/AOT fixture suite executed 14 groups and 36 managed assertions; all three new
  cancellation observations appear in both logs.
- Existing last-parent shutdown barriers and the maximum two-row handoff checks
  passed as part of those consumer suites. No other module's suite was rerun.
- The unchanged Native AOT executable from accepted `attempt-003` was verified by
  its original SHA and actually executed with the newly built native fixture.
  It was not recompiled. The unchanged product native module also matches its
  original accepted SHA. Four artifact and 22 log hashes are recorded/audited.

The original formal receipt has a metadata-only environment recording defect:
the runner appended a shared dictionary, then changed its test-root value for AOT.
The actual JIT subprocess received a fresh environment copy with `jit-data`, but
the later serialized record says `aot-data`. **Read
`formal-001/receipt-erratum.json` with the immutable receipt.** The addendum records
the actual separate JIT/AOT paths, shared-dictionary cause and original receipt
hash. Runtime results, source and artifact identities are unaffected; no test was
rerun to correct this metadata. The as-run runner remains unchanged.

Independent reviewer `/root/b07_codecs` inspected the phase proof, required the
fresh recursive stale-generation check and identified the receipt erratum. Its
separate final review binds this commit, receipt and addendum.

The earlier development run is retained separately; its exact uncommitted
scenario source can be reconstructed using `development-source.patch` against
this commit, with equality to the original recorded SHA verified. It is not
mislabelled as the final committed run.

## Handoff

Integrate this two-file commit, retain the original CI failure and corrected
source-bound receipt plus independent review, then run the existing final PR CI.
This test repair does not itself establish that the integrated PR or post-merge
CI/release has succeeded. Linux remains the only executed platform; existing
HelloWorld preview publication scope is unchanged.
