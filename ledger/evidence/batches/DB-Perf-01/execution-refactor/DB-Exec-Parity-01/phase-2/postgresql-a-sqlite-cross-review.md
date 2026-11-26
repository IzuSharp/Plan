# PG-A cancellation-hook change — independent SQLite/source review

Reviewed commit: `459ec69b6d411cd40723f342f8e88c3cabe111eb`, based on clean
`7ff7b57b907b689defb880b8af62d83679608603`. This is a source review, not new
compilation, a cancellation race test receipt, or performance acceptance.

## Finding

**No source-level blocker found for the intended PG-only hook omission.** The
actual SQLite interrupt hook remains installed at all three original installation
sites when a live SQLite connection is in use. The removed private `interrupted`
atomic had no reader in the baseline source. PG still uses the same cancellation
flag and checks around its nonblocking receive and bounded poll loops.

The narrow change should remain independently measured. It does not implement
libpq chunked rows, change protocol sends, weaken metadata validation, remove a
call-context check, or change the cleanup/connection-return policy.

## Source coverage checked

`git diff 7ff7b57 459ec69 -- native/cpp/src/provider.cpp` contains only:

1. Guard the existing `Cancel::install` in `ProviderStatement::Impl::advance` with
   `NW_ENABLE_SQLITE` and a live `provider.sqlite` check.
2. Apply the same guard in `ProviderConnection::prepare` and `execute_script`.
3. Remove the `ProviderConnection::Impl::interrupted` field and its two stores.

A full source search finds exactly those three install sites in the resulting
provider file. A baseline search finds the private atomic's declaration, a false
store in prepare, and a true store in interrupt, with no load/exchange or other
consumer. Comments mentioning interrupted readers and a local test variable named
`interrupted` are unrelated. The field is in the source-private implementation
structure, not an exported wire/ABI layout.

The deleted atomic stores also existed on SQLite prepare/interrupt paths. Thus
"SQLite hook preserved" means the interrupt behavior and lifetime protection are
preserved; it does not mean the SQLite machine image or every instruction is
unchanged. This is another reason to retain the existing dual-package impact
selection and SQLite regression coverage.

### SQLite behavior remains present

On a healthy active SQLite connection, its `sqlite3*` is nonnull before prepare,
script execution, or statement advance. The guarded installation has the same
`observe_cancel && cancel` conditions, weak connection capture and callback body.
The current `CallContext` assignment and pre-advance `call.check()` retain their
original positions. A previously held row still returns only after the same
context update, check and SQLite hook installation.

`ProviderConnection::interrupt()` still checks the SQLite profile, acquires the
connection lifetime mutex, checks the physical handle, and invokes
`sqlite3_interrupt`. The callback therefore still excludes physical destruction.
`Cancel::request()` still release-stores its requested flag before acquiring the
hook mutex. `Cancel::install()` still invokes an installed hook when the requested
flag was already set. Generation detachment in advance/close and the Host's
cancellation/retirement code are unchanged.

For a combined-provider build, `provider.sqlite` identifies the active SQLite
connection and is null for PostgreSQL. For a PostgreSQL-only build the SQLite hook
block is compiled out. For a SQLite-only build all valid SQLite paths retain it.
No claim is made that a failed operation on an already invalid/null physical
handle has an observable hook installation; its ordinary health/state validation
still rejects or routes it as before.

The unrelated SQLite prepare-flag experiment `101837c` is not contained in PG-A:
PG-A still passes `SQLITE_PREPARE_PERSISTENT`. Combining them must retain the
SQLite guard and change only the prepare flag. This review did not modify either
worktree.

### PostgreSQL observation and cleanup remain present

The old PG hook called `ProviderConnection::interrupt()`, whose only non-SQLite
effect was the removed unread atomic store. It neither sent a PostgreSQL cancel
packet nor woke the socket poll. Removing it therefore does not remove a formerly
effective network cancellation operation.

`CallContext::check()` still acquire-loads `Cancel::requested()` and checks the
deadline. `receive()` checks before each input-consumption cycle. `wait_socket()`
checks before and after `poll`/`WSAPoll`, uses the same maximum 20 ms poll request
and the same deadline-derived shorter bound. These are unchanged source bounds,
not a measured maximum end-to-end cancellation latency. Rows already buffered and
provider errors retain the existing surrounding context/Host checks.

`ProviderStatement::close` still detaches the token, clears results, observes the
same execution confirmation, and either synchronizes or drains under a cleanup
context with cancellation disabled. It retains the same discard-on-drain-failure
behavior and the same statement-live/current-context retirement. Transaction
unknown-state handling and protocol confirmation were not edited.

## Required evidence before selecting the candidate

The source proof supports the single-factor experiment; it is not a substitute
for the root-coordinated PG native correctness and actual AOT business oracles.
Required checks remain queued/pre-dispatch and in-worker cancellation, early-stop
drain, stale generation tokens, connection reuse/discard, error order and
transaction confirmation loss. Existing SQLite cancellation and early-close
regressions must also pass when the changes are combined, because the source file
is shared.

The retained impact plan selects `linux`, `postgresql` and `sqlite`, with both
top-level packages validated independently. That is the correct existing routing
for `native/cpp/src/provider.cpp`; PG-only intended runtime effect is not a reason
to hide the shared-file change or bypass the SQLite runner. No CI edits or
performance execution were introduced by this review.
