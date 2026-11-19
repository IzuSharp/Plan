# Perf-01 compact DB outcome journal: independent source review

## Scope and disposition

The protocol reviewer independently read the DB author's explicit-compact
outcome storage change on CPU 8 while the integration owner retained the
measurement resources. **Source review passed; no execution, syntax compilation,
test, application load, or timing was performed by this reviewer.** The parent
receipt projection and common long-run verifier were assigned separately to the
codec reviewer. Their review and the finite execution gates are not implied by
this disposition.

The reviewed source was an uncommitted change based on product checkout
`bf646d59c219bd1249624f752711121819b99d29`. These content identities bind the
review independently of a later commit or cherry-pick:

| Repository path | SHA-256 |
|---|---|
| `tests/Perf01.Database/perf01_outcomes.py` | `f0cf9c6162817be9ac936b29072ff2e1c85b2844b13d08e2809afe34919831e2` |
| `tests/Perf01.Database/target.py` | `d49a5adfff76261b6db115bc5faa284fb7d9e5a04174cf248b91d99d8af08272` |
| `tests/Perf01.Database/test_outcomes.py` | `c9e52f7cca00b09488e3215b278ff2db14194691bdfa82e4f0a453c6a83d41d4` |
| Unchanged `src/Benchmarks.Domain/http_target.py` | `cde9c7c492cfbdf016c1e3c5ed0048f61e45360919fd5fb9715bda5a4aabaede` |
| Unchanged `src/Benchmarks.Domain/common.py` | `f4eebb84835ffba8f6826065197740e1234ee8f3c4f7c6a51af5b2debb9c3135` |

## Content, order, and correctness boundary

The historical adapter's two append sites are in `Target.run.execute`
(`http_target.py:597-630`). The successful operation has already passed both the
domain response checks and the independent expected-value comparison before the
ordinary completion row is appended and emitted. Failed and cancelled outcomes
use the same storage boundary. The new `OutcomeJournal.append`
(`perf01_outcomes.py:36-54`) synchronously serializes the complete row before the
existing completed event is emitted. It preserves actual completion order,
warmup IDs, duplicate IDs, statuses, and complete values. It does not sort or
deduplicate observations, truncate page content, or redefine A21 acceptance.

`Target.durable_oracle` (`http_target.py:540-568`) continues to use the separately
retained mutation confirmations and independent database/file queries. Recovery
continues to call the domain operation directly and remains in its existing
separate receipt. This change does not replace either the live value oracle or
the independent persistence oracle.

The compact path is enabled only by the explicit Boolean profile field.
`PerfTarget.start_outcome_journal` (`target.py:84-99`) replaces the append sink and
intercepts only the final receipt at this target's exact path. Other saves use
the original function. Historical B23 and A21 sources are unchanged. The override
is restored by the owning finalizer (`target.py:101-119`).

## Failure and publication boundary

An append occurs outside the historical per-operation exception handler. A task
can also have left the retained task set before its append error is observed.
Therefore the new sticky journal error is necessary: serialization, partial
write, flush, close, replay, and post-seal append failures poison subsequent
publication. Count, byte count, and live SHA-256 advance only after a complete
write. Sealing precedes flushing, so a late append cannot become an accepted
record after finalization begins (`perf01_outcomes.py:26-100`).

The final writer replays bounded complete rows, validates the complete count,
byte length, and live digest, then rehashes the sealed file before atomic receipt
replacement (`perf01_outcomes.py:110-159`). A failed attempt preserves the initial
running receipt, exact journal, and any partial temporary output. Publication is
one-shot. Metadata and rows use the same pretty JSON representation as the
historical `common.save`; the finite fixture source explicitly compares the
complete bytes for empty and nonempty arrays on all three routes.

The owner finalizer records the journal status, changes the extra receipt to
failed on any poison, and raises if an otherwise successful return acquired a
late journal error (`target.py:315-361`). An earlier setup/load failure remains
the original exception. Normal operation already drains tasks before receipt
publication; exceptional partial evidence is not credited as a successful cell.

## Verification limits

The reviewed finite fixture source covers snapshot independence, actual order,
duplicate and warmup IDs, Unicode/escaped values, full pretty-byte parity,
partial writes, serialization/flush/close failures, missing/extra/reordered or
modified journal rows, post-replay alteration, atomic replacement failure, and
explicit-mode/late-poison ownership. These are source observations, not executed
test results. The review also ran only a source whitespace check, which passed.

The memory conclusion is structural: no complete list of outcome payload graphs
or complete receipt string is built by this helper. A bounded number of row
graphs and encoded row buffers can coexist during replay. Mutation confirmations,
resource samples, scalar A21 records, and other preexisting structures remain;
this review does not claim constant total process RSS. Journal serialization and
buffered file writes add generator work, so all accepted before/after/comparator
cohorts must use the same frozen harness and be calibrated again. Actual memory,
generator validity, and finite failure behavior require the integration owner's
execution gates. No performance or long-duration credit is established here.
