# Independent source review: ready-row-C

Reviewed candidate `bd9c307434d1d901752fd4353758041e38510ef1` against baseline `7ff7b57b907b689defb880b8af62d83679608603`. Read the full Enumerator, transport/lease interactions and exact diff. Separately read the retained dotnet/dotnet VMR `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f` AsyncMethodBuilderCore, AsyncValueTaskMethodBuilderT and PoolingAsyncValueTaskMethodBuilderT sources. Their exact remote blob/source identities are retained at `diagnostics/runtime-source-297acf/ready-row-builders-identity.json`.

## Result

No source-level blocker found for entering the required actual correctness and causal experiments.

The small state contains its owner and ValueTask result. Public AsyncValueTaskMethodBuilder<bool>.Create returns default and Start delegates directly to AsyncMethodBuilderCore.Start. The source confirms this saves/restores both ExecutionContext and SynchronizationContext around MoveNext. The guard never reads its Task or calls SetResult on success; allocation and actual machine-code improvement still need execution evidence.

The public admission lock and direct closed/concurrent-use exceptions remain unchanged. Finished/no-transport/no-batch routes retain original MoveAsync. The ready path checks token, batch liveness/row bound and closing in the original order, then calls the unchanged quota/materialization/row-advance branch. Lease generations, dynamic field checks and borrowed memory ownership are not bypassed.

DisposeAfterMoveAsync waits for the active move's join before calling CleanupAsync. Thus CompleteCleanupAsync clearing `_batch` does not introduce a concurrent null race in the new ready branch. Reentrant mapper disposal sets closed, signals stop and waits on the same move fence; it does not free the admitted borrow before materialization exits.

FailReadyMoveAsync starts inside the guard's catch, while the mapper's modified context is still current. Cleanup's synchronous entry therefore sees that context, and its asynchronous continuation is captured through the ordinary async builder. The outer guard restores caller context only after the helper starts. The original exception object/token and cleanup annotation are retained; EDI preserves the original throw rather than creating a replacement exception. Stack-frame presentation can contain the new helper, as expected for an internal refactor.

`_moving` remains held until successful completion or the failure helper's cleanup/finally completes. FinishMove is the original finally body, extracted without changing its locking or asynchronous join continuation policy. Exceptions from that finally are caught only by the outer result-wrapper boundary and do not trigger mapper cleanup again. Its normal builder SetException preserves OperationCanceledException cancellation classification. The no-suspension guard's SetStateMachine is unreachable from the used Start-only path.

The exhausted/inactive fallback performs an additional token/eligibility check before calling original MoveAsync. This is explicitly documented and must not be described as identical operation counts. Concurrent cancellation can always arrive between checks; stable entry error ordering is retained. Ordinary boundary/early-stop measurements and cancellation regression coverage must decide whether the extra checks are acceptable in the final candidate.

## Required next evidence

Run the planned genuine-ready-second-row AsyncLocal and SynchronizationContext controls, suppressed-flow case, mapper-context-at-cleanup observation, fault/OCE status and original-token checks, delayed cleanup plus overlapping Dispose, and existing lifetime/GC/reentrancy checks. Preserve the direct synchronous mapper negative control. Verify both independent provider packages and ordinary AOT consumers before adoption. Code size, eliminated wrapper initialization and 968 possible ready entries per 1000-row query are hypotheses/counts, not measured CPU or endpoint gains.

This review did not build or run the candidate and grants no correctness or performance execution credit.
