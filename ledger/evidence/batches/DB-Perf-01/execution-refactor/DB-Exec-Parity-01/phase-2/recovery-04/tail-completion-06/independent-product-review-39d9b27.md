# tail06 initial product diff — independent source review

Reviewer: `/root/candidate_contract_review`; implementation author: `/root/worker_boundary_review`.

Reviewed exact candidate `39d9b27c27e891b5a48b6541b629a43de3d1036d`, tree `01cab0a5c6adbb9c6d9609980dc4d7b32174b1d4`, against integrated05 `2ea67ce1902f330679c3ebff4d6d5733be20f69c` / `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`. Worktree: `worktrees/Korda-tail-completion06`, branch `task/DB-Exec-Parity-01-tail-completion06`.

## Finding

No blocking issue was found in this **source-only initial product diff**. It implements the proposed final-publication separation and is suitable for the targeted correctness stage. This does not credit a build, new regression, diagnostic mechanism, allocation result or ordinary benefit. Tests are being added under subsequent identities and must be reviewed separately.

The committed diff is eight files, 74 added lines and 17 removed lines: seven product/internal-verification files plus one mechanical `WakeProbe` signature adaptation in Interop.Async tests. C++, SQL, public APIs, runtime pins, consumers and generated readers are unchanged by this commit.

## Actual boundary checks

| Actual code | Review result |
| --- | --- |
| `CallbackPublication` | Readonly struct contains publisher, full generation, MRVTS version, result reference and exception. It is an invocation local, with no shared pending slot. Its `Publish` only forwards those local fields. |
| `CoordinatedCallback.Execute` | Processing/catch, dirty/scheduled bookkeeping and any needed `Signal` all precede the final local `Publish`. There is no later state access or enclosing `SchedulingFault` handling around that publication. |
| `HostPullController.Process` | Existing native execution, registration/control/callback drain, one-time take, original failure precedence, root/slot release and Published observers retain their order. Generation/version are captured under the existing gate; chosen result/error are stored only after observer exceptions and failed-batch compensation finish. Local publication assignment is the method's final action. |
| Explicit `ICallbackPublisher.Publish` | Checks generation, MRVTS version and published state under the controller gate, exits the gate, then performs exactly one chosen setter. It does not read/write controller, batch, native/callback/stop or scheduling state afterward. |
| Pull `Resume` | Unreserved setup-failure processing owns its own local publication, with final publication outside its processing catch. |
| Command and close `Resume` | Mechanical local-publication adaptations only. Their `Process` methods never assign the local value, so their existing completion policy remains in place. |
| Other derived processors | AsyncOperation, CallbackRegistration, MailboxProbe and WakeProbe accept the by-reference local without adopting inline completion. A source scan found no remaining old `Process()` override/call among these coordinator subclasses. |

`ExecutePrepared`, native Run/Abandon and borrow lifetimes, ready callback bookkeeping, `GetResult`, `Closed`, `ForceCloseAsync` and registration-drain behavior are unchanged by the diff. In particular, Worker-D's outer execution control still remains charged until its complete native call and borrowed owner return. It is not replaced by the weaker fact that the managed ready callback has left.

The MRVTS flag change is confined to HostPull: its default value permits the locked runtime's eligible inline path. Captured scheduler and registration-after-completion behavior remains delegated to the same runtime implementation. The setter is outside the new library failure translation boundary; a managed dispatch exception is allowed to follow the executor/runtime's ordinary exception semantics. There is no new swallow, second setter or FailFast policy.

## Remaining concrete checks

- Add and independently inspect the meaningful publication tests before considering correctness passed: actual inline interval, ExecutionContext restoration, late registration, captured Post before-dispatch failure, g1 consumption/g2 creation followed by Post failure, delayed old/empty turns, and repeated held publisher frames.
- Keep the real native callback-tail barrier and existing unreserved/held-Stop/rejected-scheduler tests. In the latter, the original setup failure and separate final-close Stop failure must remain the exact two respective exception objects.
- Keep the old held-Post test's barrier and expressly change the old implementation-specific expectation. g2 must now be able to finish while the retired g1 publisher remains held; releasing g1 afterward must not change g2.
- The readonly value introduces no explicit Task/delegate/heap allocation in source, but it is not “free.” Additional value initialization/copy/dispatch and changed stack liveness must be assessed in actual Native AOT output and ordinary small-query/close controls. No allocation or stack-size number is inferred from this source review.
- Releasing processing ownership before invoking arbitrary user code permits multiple already-retired publisher stacks to coexist. Source comments correctly avoid claiming that arbitrary user blocking is resource-bounded. Fairness and peak/released RSS remain measurement gates.

The source decision is conditional on these executed checks and the new diagnostic/ordinary comparison. The old Common-A performance rejection is not changed by this review.
