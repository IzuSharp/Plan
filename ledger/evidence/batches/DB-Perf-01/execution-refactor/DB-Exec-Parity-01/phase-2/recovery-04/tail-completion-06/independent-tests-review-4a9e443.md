# tail06 targeted regressions — independent source review

Reviewer: `/root/candidate_contract_review`. Author: `/root/worker_boundary_review`.

Reviewed commit `4a9e4435ea5c836be44fb00dc4219301567072c6`, tree `a7065978ba432dfba71f177435232090cf154d34`, against product commit `39d9b27c27e891b5a48b6541b629a43de3d1036d`. This commit changes NativeHost test code; product bytes remain the previously reviewed candidate source.

**Result: no blocking test-design defect found. Proceed to the actual Native AOT correctness run.** No test pass or benchmark result is claimed here.

The twelve ready-scheduling scenarios preserve the meaningful native/setup/rejected-offer barriers and add:

- Actual first-generation consumption while its controlled managed executor remains on the stack; generation 2 receives its own offer and completes before the old continuation is released.
- The real held captured Post remains held until generation 2 fully finishes. After release, both recorded executions must finish without an obsolete queue offer or changed generation state. The old implementation-specific block is explicitly replaced, not silently removed.
- ExecutionContext success and exception paths distinguish registration, caller and publisher values. The continuation mutates both logical and synchronization contexts, and the executor checks restoration after either return or the exact propagated exception. This avoids mistaking Task.Run's own inherited context for MRVTS restoration.
- Registration after actual completion uses a thread-local OnCompleted dynamic marker to reject synchronous delivery on that registration stack. It permits a legitimately queued callback to run on another thread before registration returns.
- Captured Post failure before dispatch, Post consumption of g1 followed by creation of g2 and failure, and an ordinary inline continuation doing the same. Exact exception identity, one Post/callback invocation, one next-generation admission and the next real provider result are asserted.
- Four already-consumed publisher frames remain held concurrently without callback reservations. After all are released, generation 5 must still execute correctly and final owner counters drain.

The controlled scheduler's thread-static scope and held-stack checks establish execution within that managed work item's dynamic interval, not merely reuse of an operating-system thread ID. This is appropriately narrower than a precise setter-entry/return diagnostic, which remains a separate mechanism gate.

The new `--pull-publication-failure-only` entry point is suitable for a baseline negative because it checks the post-sentinel exception boundary without demanding the candidate's optional inline policy. It executes SQLite first. If unchanged baseline product fails there, the PostgreSQL call is not reached: that receipt must report the actual failing provider and skipped coverage rather than claim a two-provider negative result.

These source checks supplement the existing unreserved/held-Stop, original setup-versus-stop failure ordering, native Run/borrow retirement, held-reader, cancellation and cold-close suites. Subsequent receipts must identify the actual built source, Native AOT ELF, original native bytes, commands, complete assertions and native-owner retirement. This review cannot substitute for those executions.
