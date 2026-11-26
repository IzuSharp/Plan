# DB-Exec-07: detached completion for one database command

Status: interface agreed in local ABI-only checkpoint
`d497dd23098a252d81ca9bf06c4e2efb36ddf02a`; implementation and package
validation remain pending. It does not replace the accepted Design text. The reviewed native
base is public [`933d16bf673dff5310db37cc444ba5019842d81d`][base]
(local `12ac0e6ebd7503fa106106c26278ec98f4e115d9`). The measured consumer is
public `31693e3883f1192a34fcb9e9c49acdcca4ad321c`; these identities must remain
separate. The subsequent command-cleanup error repair is in the reviewed base.

## Evidence that selects this work

[Strict single-case analysis 02](analysis-single-row-02.md) reconciles twelve
ordinary C1 observations and six separate ABI diagnostics. The ordinary and
diagnostic processes share the same actual ordinary package/native images,
manifest and business oracle. Diagnostic timings receive no credit. Analysis 01
is retained: its only structural failure was the analyzer incorrectly expecting
`FindAsync` to use mutation pull. Its actual implementation builds
`From(...).SelectAll().SingleOrDefaultAsync`, hence three ordinary query pulls
per transaction case. No consumer was rerun for that correction.

| Provider/case | Ordinary Korda p99, µs | Korda CPU, µs/business operation | Separate diagnostic generic starts | Conditional transaction closes | `try_retire` Pending / calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| SQLite rollback | 24,510.464 | 2,364.371 | 6,483 = 3 × 2,065 + 288 | 288 | 1,438 / 7,921 |
| SQLite commit | 31,064.064 | 2,394.867 | 7,331 = 4 × 1,820 + 51 | 51 | 1,416 / 8,747 |
| PostgreSQL rollback | 26,607.616 | 2,397.881 | 8,935 = 3 × 2,681 + 892 | 892 | 1,197 / 10,132 |
| PostgreSQL commit | 28,311.552 | 2,587.524 | 9,362 = 4 × 2,214 + 506 | 506 | 1,142 / 10,504 |

Numeric query diagnostics record zero generic operations on both providers.
The transaction cases require begin, nonreturning update(s), finish, and
conditionally a separate transaction close. Their row queries already use
pull/final-close readiness. Whole-process transaction allocation remains about
63–67 KB/business operation; no framework-only allocation claim is justified.

The existing [generic completion][host] invokes the terminal callback while its
`Operation` callback/work leases still exist. `DbOperation::run` additionally
retains the local moved `action` until after `complete` returns. Managed
`DataSource.Complete` awaits `AsyncOperation.Retirement`; a Pending retirement
sets the coordinator retry flag and may await the existing 10 ms tick without a
later native notification. Pending is an attempt count: it can occur before
terminal delivery and is not a count of unique operations or 10 ms delays.
The combined ordinary observations, counts and source path select a structural
completion change. They do not quantify the fraction of total CPU attributable
to that layer.

## Reuse boundary

Reuse the existing provider SQL/parameter path, `capture_execution`,
`capture_mutation`, admission gates, creation-time deadlines, transaction and
savepoint business functions, `Value` alternatives, and rich error/snapshot
payloads. Replace the generic `Operation<Value>`/terminal/retirement protocol
only for the listed formal entry points. No new command tape, SQL replay,
parameter encoding or provider protocol is introduced. The frozen 42 exports,
their records and their quiet proof keep their existing meaning.

| Request kind | Target/input/payload/action | Existing execution to reuse | Result |
| ---: | --- | --- | --- |
| 1: execute | Session; SQL/native plan; existing argument bytes; action 0 | `capture_execution`; count/nonquery helper | `100`: signed count |
| 2: mutation | Session; model; existing mutation payload; existing mutation kind | `capture_mutation`, remaining deadline, affected-row validation and existing insert bulk-error enrichment | `100`: signed count |
| 3: begin | Session; null input; existing transaction options; action 0 | Existing option validation, `admit(true)`, `Transaction::begin` | `3`: transaction owner |
| 4: finish | Transaction; null input; empty payload; existing commit/rollback action | `Transaction::finish` | `101`: existing owned snapshot buffer |
| 5: savepoint | Transaction; null input; empty payload; action 0 | `Transaction::create_savepoint` | `4`: savepoint owner |
| 6: savepoint action | Savepoint; null input; empty payload; existing action | Existing savepoint action and snapshot | `101`: existing owned buffer |
| 7: close | Session, Transaction or Savepoint; null input; empty payload; action 0 | Existing request-close/join/snapshot or savepoint disposal | `101`: existing owned buffer |

Kind 1 rejects a row-returning plan before acceptance. Kind 2 excludes returning
mutation kind 1, which already uses lazy pull. The first implementation excludes
Source open/close, administrative admission, cursor fetch and cursor close.
These retain their existing path. In particular Source close must not execute
inside a worker whose own Source reservation/fence it would wait for.

The versioned upstream references remain [Npgsql 11.0.0][npgsql],
[Dapper.AOT 1.1.0][dapper] and the provider pins already recorded in Design.
This proposal is Korda's C#/C++ ownership adaptation, not a claim that those
projects have this ABI. Npgsql reader completion and normal EOF cleanup remain
a separate possible measurement after the command completion result is known.

## Proposed private C ABI

On Linux x64, the request is 48 bytes and the result is 32 bytes. All unused
fields must be zero. Pointer/size/alignment, exact kind and allowed target types
are checked before accepting work. Views are captured into the existing owned
execution representation during the request; no caller-owned span is retained.

```c
typedef struct nw_db_command_request_args_v1 {
    uint32_t struct_size;       /* 0: 48 */
    uint32_t kind;              /* 4: table above */
    nw_db_ref target;           /* 8 */
    nw_db_ref input;            /* 16 */
    nw_bytes_view_v1 payload;   /* 24: pointer + uint64 length */
    uint32_t action;            /* 40 */
    uint32_t reserved;          /* 44: zero */
} nw_db_command_request_args_v1;

typedef struct nw_db_command_result_v1 {
    uint32_t struct_size;       /* 0: 32 */
    uint32_t kind;              /* 4: existing 3/4/100/101 */
    int64_t count;              /* 8: only for 100 */
    nw_db_ref owner;            /* 16: only for 3/4 */
    nw_db_buffer* buffer;       /* 24: only for 101 */
} nw_db_command_result_v1;

nw_status NW_CDECL nw_db_command_request_v1(
    const nw_db_command_request_args_v1* args,
    const nw_db_cursor_callbacks_v1* callbacks,
    nw_db_ref* request, nw_error_info_v1* error);
nw_status NW_CDECL nw_db_command_take_v1(
    nw_db_ref request, uint32_t expected_kind,
    nw_db_command_result_v1* result, nw_error_info_v1* error);
nw_status NW_CDECL nw_db_command_take_error_v1(
    nw_db_ref request, nw_db_buffer** error_payload, nw_error_info_v1* error);
nw_status NW_CDECL nw_db_command_cancel_v1(nw_db_ref request);
```

Reuse the 24-byte ready-only callback record with generation 0. Reuse existing
`nw_db_owner_release_v1` for the request and returned owners, and existing
buffer release for snapshots/errors. Four new exports are sufficient if a new
internal `CommandCompletion` alternative is stored in `OwnerData`.

That internal owner also gets a branch in existing close/snapshot handling for
cold fallback. This extends which internal objects can be inspected; it does
not weaken quietness or modify old owner behavior. The frozen extension is
`db.command.completion.v1`, capability bit 28, recorded in the new private
`command-completion-v1.json` and header. The old 42 declarations are unchanged.

`take` returns Pending before ready without consuming anything. Wrong expected
kind does not consume. A successful take transfers exactly one count or owned
result; all irrelevant output fields remain zero. A failed business result
retains its rich error for one `take_error` using the existing provider,
correlation, cleanup and bulk format. A failed native/managed output handoff
must compensate any received owner without resubmitting SQL. Duplicate or
missing results are errors, not fabricated success.

## Acceptance, publication and proof

1. Synchronously validate and capture existing input semantics. Allocate the
   independent result state, worker and queued closure before acceptance.
   Acquire Source admission/reservation before adding notification tickets. For
   close controls, `reserve_operation(true) == false` is rejection with no
   callback, never permission to append a ticket after `admission_stop`.
2. Publish the request handle into the caller's stable output slot before
   accepting and dispatching. Every non-OK request return must leave output
   null and create no callback obligation. Every accepted request returns OK
   and produces exactly one ready, including queue-post failure. A callback may
   arrive before the request call returns; managed setup must account for it.
3. Execute the original business function. **Both** the ABI request stack and
   worker must relinquish captured Session/plan/gate/action/provider references
   before readiness. Merely clearing a Worker member is insufficient if its
   request caller or `run` local `action` still owns the same capture.
   A worker start gate is permitted to protect the local queue submission:
   `WorkerPool::post` can begin work before its caller has returned from the
   Source-owned pool method. The submitter releases temporary input borrows,
   then publishes the independent gate as its last relevant action. The worker
   acquires that gate before execution. Queue failure must not leave a queued
   worker waiting forever on a gate that will never open. This gate is local
   ownership handoff, not an extra database/protocol reply.
4. Preserve the primary Error before any cleanup attempt. Contain cleanup
   failure, retain existing cleanup/bulk/provider/correlation fields, and poison
   or discard where retirement is unconfirmed. Detach the cancellation hook and
   drain any active native cancel accessor; drop the action and gate; return the
   Source reservation; release all worker input accessors. The owned result may
   legitimately retain its returned Transaction/Savepoint or Buffer.
5. Freeze the result/error in a separate `ReadyState`, clear its callback
   record, drop the worker's state accessor, and invoke ready. After notification
   only independent per-request and Source notification tickets may be touched.
   No application continuation executes inline in that native callback.

Use a new Source `command_workers` fence or an equivalently separate ledger.
Source joins it after its pending/admission stop transition and before stopping
worker pools. A per-request fence covers notification return. Public request
join/snapshot includes that fence; normal take does not wait for it.

The two proofs intentionally differ:

| Proof | Meaning |
| --- | --- |
| Ready + setup returned + managed callback/control/registration drain | Business result/error is frozen and the worker cannot access its former input objects; take and normal request-owner release are permitted. |
| Public request join/safe public snapshot | The above plus actual notification return and necessary unclaimed-result cleanup; permits retiring an unknown callback obligation. |

Generic fallback must wait the request notification fence even if resource
cleanup fails. A public snapshot must not report `LocalResourcesReleased=true`
while that tail remains active. No close worker may wait for its own ticket.
An unclaimed returned owner is discarded with the existing owner cleanup
semantics and truthful cleanup evidence; it must not silently leak a live
transaction or make an unsafe connection reusable.

Keep command quietness separate from its parent's cleanup outcome. After the
notification fence and outstanding result/error have retired, an existing
business error's secondary parent-cleanup detail does not by itself make the
command unsafe. Source and Transaction retain their own cleanup obligations.
In contrast, if cold request join must retire an unclaimed newly returned
Transaction/Savepoint owner and that retirement fails, retain that owner and
the command's cleanup evidence; its safe snapshot remains false. Discarding an
unclaimed Unknown snapshot buffer must not force the existing transaction to
finish before its original early-outcome boundary.

If a managed bridge fails after request invocation, preserve any native output
handle in a stable finally-visible slot. With a handle, force-close/join that
specific request through the frozen fallback. Without a recoverable handle,
only a Source-level proof covering the new command ledger can retire an unknown
callback root. A Session resource snapshot alone is not such a proof. If proof
fails, retain the root/slot and report the original failure plus cleanup failure.

## Public behavior to preserve

Ready means the individual execution result is available. It does **not** mean
an explicit transaction has committed, rolled back or completed its background
cleanup unless its actual business result says so. In particular an Unknown
transaction outcome must be published at the existing decision boundary;
waiting for all transaction cleanup before ready would change the public
contract. Its snapshot must retain `LocalResourcesReleased=false` when applicable.

Pre-admission validation and an already-accepted worker have distinct error
ordering. Reuse the original business helpers. Do not copy pull's admission
order mechanically into nonquery/transaction workers: the old ordinary
`DbOperation::run` does not universally re-admit Source before invoking them.
Cancellation after readiness cannot overwrite a frozen provider error, cleanup
receipt or committed outcome. Provider cancellation hooks run outside the
command-state mutex; atomic cancellation intent must not add a lock inversion.

Managed execution keeps a single one-shot controller, counted request/cancel
controls, bounded scheduler reservation and rooted callback until proven safe.
Setters retain asynchronous continuations. Accepted-but-not-ready work waits
for ready, not a prequeued no-op. Setup rejection, scheduler refusal, cancellation
registration disposal and indeterminate acceptance keep explicit progress paths.
No normal `Operation.TryRetire` poll or 10 ms retirement timer remains for these
entry points; cold fallback remains observable and separately counted.

## Scalar count boundary

The current count helper creates a two-row buffer and parses NWDF, coupling a
scalar result to `MaxBatchRows >= 2`. A new one-shot scalar helper should use the
existing provider statement and codec machinery directly: validate the complete
column layout; read one non-null eight-byte count; inspect a possible second row
and terminal/error; preserve the existing cardinality, width, cancellation,
timeout, late-error and cleanup semantics. No public batch or NWDF arena is
required. `MaxBatchRows=1` must work on this new scalar path.

Retiring the provider statement and finishing the parent admission gate are
separate cleanup boundaries. Preserve a conversion, provider or cardinality
error if parent cleanup scheduling also fails; a retryable parent launch error
must not masquerade as unknown provider retirement. When parent closure has
already scheduled cursor cleanup, a no-op `close_now` is insufficient proof:
the helper must join that actual cleanup or retain truthful unconfirmed state.

The initial scope is the new one-shot path. Frozen legacy scalar execution and
its regression fixtures remain separately identified. Any change to their
historical behavior requires an explicit decision, not an incidental routing
change. `AnyAsync` still consumes the same count result with its existing
managed boolean interpretation.

## Deterministic validation before measurement

The independent test owner can compile the actual private C ABI into a dedicated
`nw_command_completion_tests` target using existing Host test support. Preserve
the original frozen ABI fixtures and add only the new profile/probe inventory.

- Every request kind: zero/positive count, transaction/savepoint owner and owned
  snapshot, wrong expected kind without consumption, Pending/duplicate/missing
  result, invalid handle/alignment and dirty-output clearing.
- Before-work hold; after-input-accessors-dropped/before-ready hold; held ready
  callback; after-ready native tail hold. Prove normal take can finish while the
  tail is held, and request public join/snapshot and Source join cannot claim
  quiet prematurely. Include last request-owner release and parent Source close.
- Rejection before acceptance versus accepted queue failure: callback count
  exactly zero or one respectively; reservation/fence launch compensation;
  Source `admission_stop`; no late fence admission or self-wait.
- Cancellation before request, accepted before work, provider hook active,
  concurrent cancel/ready/take, cancellation after a frozen provider failure;
  separately verify the original parent-close/error ordering at each boundary.
- Rich error identity and independent cleanup/bulk retention, actual provider
  failures, allocation/queue failures, unknown transaction result before later
  cleanup, failed cleanup producing poison/unreleased evidence.
- Direct scalar: batch rows 1, full shape/null/width, zero/two rows, a late
  provider error after the first value, mapper-free scalar conversion and
  statement/connection retirement on each failure.
- Actual managed Native AOT public Count/Any, nonreturning CRUD, begin/finish,
  savepoints and disposal; held setup/callback/control/registration, rejected
  scheduler, uncertain native-call return, malformed owned take and original
  exception identity. Owner counters must cover request state and detached work,
  not only the former six owners.

Only after the correctness/package gate, repeat the same ordinary three-case
plans and separate ABI diagnostics. The instrumentation inventory must include
the new exports so a zero generic count cannot conceal missing new calls.
Expect mandatory commands per business operation to use direct request/take,
with conditional transaction disposal separately counted. Compare ordinary
latency/CPU/whole-process B/op/GC and retain failures. Do not use diagnostic
latency, shorten the old timer, infer framework 0 B, or grant long-run acceptance
from these short runs.

[base]: https://github.com/IzuSharp/Korda/tree/933d16bf673dff5310db37cc444ba5019842d81d
[host]: https://github.com/IzuSharp/Korda/blob/933d16bf673dff5310db37cc444ba5019842d81d/native/cpp/src/host.cpp
[abi]: https://github.com/IzuSharp/Korda/blob/933d16bf673dff5310db37cc444ba5019842d81d/native/cpp/src/host_abi.cpp
[npgsql]: https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlCommand.cs
[dapper]: https://github.com/DapperLib/DapperAOT/blob/0e071bf05e54caecfa98c885b075fa3e247f3ecc/src/Dapper.AOT/CommandT.Query.cs
